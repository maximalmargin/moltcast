#!/usr/bin/env python3
"""Generate Chinese podcast audio for MoltCast using Volcengine BigModel TTS API.

Uses the WebSocket binary protocol:
  wss://openspeech.bytedance.com/api/v3/tts/bigmodel

Protocol: custom binary header (full header) + JSON payload, returns binary audio chunks.
"""

import gzip
import json
import os
import re
import struct
import sys
import uuid
import websocket
from io import BytesIO
from pathlib import Path
from pydub import AudioSegment

# ── Config ──────────────────────────────────────────────────────────────────

ENDPOINT = "wss://openspeech.bytedance.com/api/v3/tts/bigmodel"

VOICE_MAP = {
    "黄油": "zh_male_chunhou_mars",      # warm casual male
    "夹夹": "zh_female_cancan_mars",      # sharp analytical female
}

SILENCE_BETWEEN_SPEAKERS_MS = 500
SILENCE_BETWEEN_LINES_MS = 300

# ── Binary protocol helpers ─────────────────────────────────────────────────

# Protocol version 3, full client request, no sequence
PROTOCOL_VERSION = 3
HEADER_SIZE = 1          # 1 = header is 1*4=4 bytes (but bigmodel uses 11-byte header)
# Actually the bigmodel TTS uses a specific binary format. Let me implement it properly.

def build_request(text: str, voice_type: str, app_id: str, access_token: str,
                  encoding: str = "mp3", sample_rate: int = 24000) -> bytes:
    """Build binary WebSocket request for TTS bigmodel API."""
    request_json = {
        "app": {
            "appid": app_id,
            "token": access_token,
            "cluster": "volcano_tts",
        },
        "user": {
            "uid": "moltcast-generator",
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "sample_rate": sample_rate,
            "speed_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "operation": "query",
        },
    }
    payload = json.dumps(request_json).encode("utf-8")
    payload_compressed = gzip.compress(payload)

    # Binary header format for volcengine TTS:
    # byte 0: protocol_version(4bit) | header_size(4bit)
    # byte 1: message_type(4bit) | message_type_specific(4bit)  
    # byte 2: message_serialization(4bit) | message_compression(4bit)
    # byte 3: reserved
    # bytes 4-7: payload size (big-endian uint32)
    
    # protocol_version=1, header_size=1 (1*4=4 bytes... but we need 8 total for header+size)
    # Actually: header_size counts in 32-bit words. header_size=1 means 4 bytes of header.
    # Then payload size is appended as 4 bytes.
    
    # Values:
    # protocol_version = 0b0001 (1)
    # header_size = 0b0001 (1, meaning 4 bytes)
    # message_type = 0b0001 (1 = full client request)
    # message_type_specific = 0b0000 (0)
    # serialization = 0b0001 (1 = JSON)
    # compression = 0b0001 (1 = gzip)
    # reserved = 0b00000000
    
    byte0 = (1 << 4) | 1          # version=1, header_size=1
    byte1 = (1 << 4) | 0          # msg_type=full_client_request, specific=0
    byte2 = (1 << 4) | 1          # serialization=JSON, compression=gzip
    byte3 = 0                      # reserved

    header = struct.pack(">BBBI", byte0, byte1, byte2, byte3)
    # Wait - that's BBBI = 1+1+1+4 = 7 bytes. Not right.
    # The format is: 4 header bytes + 4 bytes payload size
    header = bytes([byte0, byte1, byte2, byte3])
    size = struct.pack(">I", len(payload_compressed))
    
    return header + size + payload_compressed


def parse_response(data: bytes) -> tuple:
    """Parse binary response. Returns (message_type, payload_bytes, is_last).
    
    Returns:
        (msg_type, audio_bytes_or_none, is_last_segment)
    """
    if len(data) < 4:
        return (0, None, True)
    
    byte0 = data[0]
    byte1 = data[1]
    byte2 = data[2]
    byte3 = data[3]
    
    header_size = (byte0 & 0x0F) * 4  # in bytes
    msg_type = (byte1 >> 4) & 0x0F
    msg_specific = byte1 & 0x0F
    serialization = (byte2 >> 4) & 0x0F
    compression = byte2 & 0x0F
    
    if msg_type == 0xb:  # audio-only server response
        # msg_specific: 0=no sequence, others may indicate sequence info
        # After header: 4 bytes sequence number (if applicable), then 4 bytes payload size, then payload
        pos = header_size
        
        # Check if there's a sequence number (msg_specific != 0)
        sequence = 0
        if msg_specific != 0:
            if pos + 4 <= len(data):
                sequence = struct.unpack(">I", data[pos:pos+4])[0]
                pos += 4
        
        if pos + 4 <= len(data):
            payload_size = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
            audio_data = data[pos:pos+payload_size]
            # is_last when sequence is negative or specific flag
            # For bigmodel: msg_specific indicates if more data follows
            # Typically sequence < 0 means last
            is_last = (sequence < 0 or msg_specific == 0)
            return (msg_type, audio_data, is_last)
        return (msg_type, None, True)
    
    elif msg_type == 0xf:  # error response
        pos = header_size
        if pos + 4 <= len(data):
            code = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
        if pos + 4 <= len(data):
            payload_size = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
            msg_data = data[pos:pos+payload_size]
            if compression == 1:
                msg_data = gzip.decompress(msg_data)
            error_msg = msg_data.decode("utf-8")
            raise RuntimeError(f"TTS API error (code={code}): {error_msg}")
        raise RuntimeError(f"TTS API error (code={code})")
    
    elif msg_type == 0xc:  # frontend server response (JSON + possibly audio)
        pos = header_size
        if pos + 4 <= len(data):
            payload_size = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
            payload = data[pos:pos+payload_size]
            if compression == 1:
                payload = gzip.decompress(payload)
            resp = json.loads(payload.decode("utf-8"))
            # Check if there's audio data in the response
            if "data" in resp:
                import base64
                audio = base64.b64decode(resp["data"])
                return (msg_type, audio, True)
            return (msg_type, None, True)
    
    return (msg_type, None, True)


def tts_synthesize(text: str, voice_type: str, app_id: str, access_token: str) -> bytes:
    """Synthesize text to audio bytes (mp3) via WebSocket."""
    
    # Build the request
    req = build_request(text, voice_type, app_id, access_token)
    
    audio_chunks = []
    
    ws = websocket.create_connection(
        ENDPOINT,
        header={
            "Authorization": f"Bearer; {access_token}",
        },
        timeout=30,
    )
    
    try:
        ws.send(req, opcode=websocket.ABNF.OPCODE_BINARY)
        
        while True:
            result = ws.recv()
            if isinstance(result, str):
                # Text response - might be JSON
                try:
                    resp = json.loads(result)
                    if "code" in resp and resp["code"] != 0:
                        raise RuntimeError(f"TTS error: {resp}")
                    if "data" in resp:
                        import base64
                        audio_chunks.append(base64.b64decode(resp["data"]))
                except json.JSONDecodeError:
                    pass
                break
            else:
                # Binary response
                msg_type, audio_data, is_last = parse_response(result)
                if audio_data:
                    audio_chunks.append(audio_data)
                if is_last:
                    break
    finally:
        ws.close()
    
    return b"".join(audio_chunks)


# ── Alternative: try HTTP API first (simpler) ──────────────────────────────

import urllib.request
import urllib.error

def tts_synthesize_http(text: str, voice_type: str, app_id: str, access_token: str) -> bytes:
    """Try HTTP API as alternative."""
    url = "https://openspeech.bytedance.com/api/v1/tts"
    
    payload = {
        "app": {
            "appid": app_id,
            "token": "access_token",
            "cluster": "volcano_tts",
        },
        "user": {
            "uid": "moltcast-generator",
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "sample_rate": 24000,
            "speed_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "operation": "query",
        },
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{access_token}",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 3000:
                import base64
                return base64.b64decode(result["data"])
            else:
                raise RuntimeError(f"HTTP TTS error: {result}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP TTS failed ({e.code}): {body}")


# ── Transcript parser ───────────────────────────────────────────────────────

def parse_transcript(path: str) -> list:
    """Parse markdown transcript into list of (speaker, text) tuples."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    segments = []
    pattern = re.compile(r'^\*\*(.+?)\*\*[：:]\s*(.+)$')
    
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            speaker = m.group(1).strip()
            text = m.group(2).strip()
            if speaker in VOICE_MAP and text:
                segments.append((speaker, text))
    
    return segments


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    # Load env
    env_file = os.path.expanduser("~/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)
    
    app_id = os.environ.get("VOLC_PODCAST_APP_ID", "")
    access_token = os.environ.get("VOLC_PODCAST_ACCESS_TOKEN", "")
    
    if not app_id or not access_token:
        print("ERROR: Set VOLC_PODCAST_APP_ID and VOLC_PODCAST_ACCESS_TOKEN")
        sys.exit(1)
    
    # Parse args
    transcript_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/repos/moltcast/episodes/ep003/transcript-cn.md"
    )
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
        "~/repos/moltcast/episodes/ep003/episode-003-cn.mp3"
    )
    
    # Test mode: just synthesize a short snippet
    test_mode = "--test" in sys.argv
    
    if test_mode:
        print("=== TEST MODE: synthesizing short snippet ===")
        test_text = "欢迎回到 MoltCast，我是黄油。"
        print(f"Text: {test_text}")
        print(f"Voice: {VOICE_MAP['黄油']}")
        
        # Try HTTP first, then WebSocket
        audio = None
        for method_name, method_fn in [("HTTP", tts_synthesize_http), ("WebSocket", tts_synthesize)]:
            try:
                print(f"Trying {method_name} API...")
                audio = method_fn(test_text, VOICE_MAP["黄油"], app_id, access_token)
                print(f"  ✓ {method_name} succeeded! Got {len(audio)} bytes")
                break
            except Exception as e:
                print(f"  ✗ {method_name} failed: {e}")
        
        if audio:
            test_path = "/tmp/tts_test.mp3"
            with open(test_path, "wb") as f:
                f.write(audio)
            seg = AudioSegment.from_mp3(test_path)
            print(f"  Audio duration: {len(seg)/1000:.1f}s")
            print(f"  Saved to: {test_path}")
        else:
            print("Both methods failed!")
            sys.exit(1)
        return
    
    # Full generation
    print(f"Parsing transcript: {transcript_path}")
    segments = parse_transcript(transcript_path)
    print(f"Found {len(segments)} segments")
    
    # Determine which TTS method works
    synthesize = None
    test_text = "测试。"
    for method_name, method_fn in [("HTTP", tts_synthesize_http), ("WebSocket", tts_synthesize)]:
        try:
            method_fn(test_text, VOICE_MAP["黄油"], app_id, access_token)
            synthesize = method_fn
            print(f"Using {method_name} API")
            break
        except Exception as e:
            print(f"{method_name} API not available: {e}")
    
    if not synthesize:
        print("ERROR: No working TTS API method found")
        sys.exit(1)
    
    # Generate audio for each segment
    silence_between_speakers = AudioSegment.silent(duration=SILENCE_BETWEEN_SPEAKERS_MS)
    silence_between_lines = AudioSegment.silent(duration=SILENCE_BETWEEN_LINES_MS)
    
    final_audio = AudioSegment.empty()
    prev_speaker = None
    
    for i, (speaker, text) in enumerate(segments):
        voice = VOICE_MAP[speaker]
        print(f"  [{i+1}/{len(segments)}] {speaker}: {text[:40]}...")
        
        try:
            audio_bytes = synthesize(text, voice, app_id, access_token)
        except Exception as e:
            print(f"    ERROR: {e}")
            print(f"    Skipping this segment")
            continue
        
        # Convert to AudioSegment
        seg = AudioSegment.from_mp3(BytesIO(audio_bytes))
        
        # Add silence
        if prev_speaker is not None:
            if speaker != prev_speaker:
                final_audio += silence_between_speakers
            else:
                final_audio += silence_between_lines
        
        final_audio += seg
        prev_speaker = speaker
    
    # Export
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_audio.export(output_path, format="mp3", bitrate="192k")
    duration_s = len(final_audio) / 1000
    print(f"\n✓ Generated: {output_path}")
    print(f"  Duration: {int(duration_s//60)}m {int(duration_s%60)}s")
    print(f"  Size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
