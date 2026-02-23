#!/usr/bin/env python3
"""Generate EP4 (La Distinction) English audio — multi-engine TTS.

Trilingual episode:
  Butter (EN)  → ElevenLabs v3, Laura
  Coral  (FR)  → ElevenLabs v3, Jules (French voice, also speaks EN)
  Pinch  (CN)  → Volcengine BigModel TTS, zh_male_dayixiansheng

Usage:
    source ~/.env
    python3 generate_ep004_en.py \
        --transcript episodes/ep004/transcript-en-verbal.md \
        --output episodes/ep004/ep004-en.mp3 \
        [--skip-existing]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
import gzip
import struct
from io import BytesIO
from pathlib import Path

import requests
import websocket

# ── Voice Config ────────────────────────────────────────────────────────────

ELEVENLABS_VOICES = {
    "butter": {
        "voice_id": "FGY2WhTYpPnrIDTdsKH5",  # Laura
        "name": "Laura",
    },
    "coral": {
        "voice_id": "8qnuneLiGjGrT4A62CCe",  # Jules (French)
        "name": "Jules",
    },
}

VOLC_VOICE = "ICL_zh_male_shuaizhenxiaohuo_tob"  # Pinch (珊珊) — 率真小伙

ELEVENLABS_MODEL = "eleven_v3"
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
VOLC_ENDPOINT = "https://openspeech.bytedance.com/api/v1/tts"
CROSSFADE_MS = 80

# ── Transcript Parser ──────────────────────────────────────────────────────

def parse_transcript(path: str) -> list[dict]:
    """Parse verbal transcript into [{speaker, text}, ...]."""
    segments = []
    current_speaker = None
    current_text = []

    with open(path) as f:
        for line in f:
            line = line.rstrip()
            match = re.match(r'\*\*(\w+)\*\*:\s*(.*)', line)
            if match:
                if current_speaker and current_text:
                    text = "\n".join(current_text).strip()
                    if text:
                        segments.append({"speaker": current_speaker.lower(), "text": text})
                current_speaker = match.group(1)
                current_text = [match.group(2)] if match.group(2) else []
            elif current_speaker and line and not line.startswith('#') and not line.startswith('*') and not line.startswith('---'):
                current_text.append(line)

    if current_speaker and current_text:
        text = "\n".join(current_text).strip()
        if text:
            segments.append({"speaker": current_speaker.lower(), "text": text})

    return segments

# ── ElevenLabs TTS ─────────────────────────────────────────────────────────

def synth_elevenlabs(api_key: str, voice_id: str, text: str, output_path: str) -> bool:
    url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}"
    resp = requests.post(
        url,
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3},
        },
        timeout=120,
    )
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    print(f"  ❌ ElevenLabs error {resp.status_code}: {resp.text[:200]}")
    return False

# ── Volcengine TTS (WebSocket) ─────────────────────────────────────────────

def _volc_build_request(text: str, voice_type: str, app_id: str, token: str) -> bytes:
    payload = json.dumps({
        "app": {"appid": app_id, "token": token, "cluster": "volcano_tts"},
        "user": {"uid": "moltcast-ep004"},
        "audio": {"voice_type": voice_type, "encoding": "mp3", "sample_rate": 24000, "speed_ratio": 1.0},
        "request": {"reqid": str(uuid.uuid4()), "text": text, "operation": "query"},
    }).encode("utf-8")
    compressed = gzip.compress(payload)
    header = bytes([(1 << 4) | 1, (1 << 4) | 0, (1 << 4) | 1, 0])
    return header + struct.pack(">I", len(compressed)) + compressed


def _volc_parse_response(data: bytes):
    if len(data) < 4:
        return None, True
    header_size = (data[0] & 0x0F) * 4
    msg_type = (data[1] >> 4) & 0x0F
    msg_specific = data[1] & 0x0F
    compression = data[2] & 0x0F

    if msg_type == 0xb:  # audio
        pos = header_size
        sequence = 0
        if msg_specific != 0:
            if pos + 4 <= len(data):
                sequence = struct.unpack(">I", data[pos:pos+4])[0]
                pos += 4
        if pos + 4 <= len(data):
            payload_size = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
            return data[pos:pos+payload_size], (sequence < 0 or msg_specific == 0)
        return None, True
    elif msg_type == 0xf:  # error
        pos = header_size
        code = struct.unpack(">I", data[pos:pos+4])[0] if pos+4 <= len(data) else -1
        pos += 4
        if pos + 4 <= len(data):
            ps = struct.unpack(">I", data[pos:pos+4])[0]
            pos += 4
            msg = data[pos:pos+ps]
            if compression == 1:
                msg = gzip.decompress(msg)
            raise RuntimeError(f"Volc TTS error ({code}): {msg.decode()}")
        raise RuntimeError(f"Volc TTS error ({code})")
    return None, True


def synth_volcengine(app_id: str, token: str, text: str, output_path: str) -> bool:
    """Synthesize Chinese text via Volcengine HTTP TTS. Splits at ~300 chars (1024 bytes UTF-8)."""
    from pydub import AudioSegment as AS
    import base64

    chunks = _split_chinese(text, max_chars=280)
    audio_parts = []

    for ci, chunk in enumerate(chunks):
        payload = {
            "app": {"appid": app_id, "token": token, "cluster": "volcano_tts"},
            "user": {"uid": "moltcast-ep004"},
            "audio": {
                "voice_type": VOLC_VOICE,
                "encoding": "mp3",
                "rate": 24000,
                "speed_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": chunk,
                "text_type": "plain",
                "operation": "query",
            },
        }
        try:
            resp = requests.post(
                VOLC_ENDPOINT,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer;{token}",
                },
                json=payload,
                timeout=60,
            )
            result = resp.json()
            if result.get("code") == 3000 and "data" in result:
                audio_bytes = base64.b64decode(result["data"])
                audio_parts.append(AS.from_mp3(BytesIO(audio_bytes)))
            else:
                print(f"    ⚠️ Chunk {ci+1}/{len(chunks)} error: code={result.get('code')} msg={result.get('message','')[:100]}")
        except Exception as e:
            print(f"    ⚠️ Chunk {ci+1}/{len(chunks)} exception: {e}")

    if not audio_parts:
        return False

    combined = audio_parts[0]
    for part in audio_parts[1:]:
        combined += AS.silent(duration=200) + part
    combined.export(output_path, format="mp3", bitrate="192k")
    return True


def _split_chinese(text: str, max_chars: int = 280) -> list[str]:
    """Split Chinese text at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[。！？；\n])', text)
    chunks = []
    current = ""
    for s in sentences:
        if not s:
            continue
        if len(current) + len(s) > max_chars and current:
            chunks.append(current.strip())
            current = s
        else:
            current += s
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [text]

# ── ffmpeg crossfade ───────────────────────────────────────────────────────

def crossfade_concat(paths: list[str], output: str, crossfade_ms: int = 80):
    if not paths:
        return
    if len(paths) == 1:
        subprocess.run(["cp", paths[0], output])
        return

    n = len(paths)
    inputs = []
    for p in paths:
        inputs.extend(["-i", p])

    cf = crossfade_ms / 1000.0
    if n == 2:
        fc = f"[0][1]acrossfade=d={cf}:c1=tri:c2=tri"
    else:
        filters = []
        for i in range(n - 1):
            in1 = "[0]" if i == 0 else f"[a{i}]"
            in2 = f"[{i+1}]"
            if i == n - 2:
                filters.append(f"{in1}{in2}acrossfade=d={cf}:c1=tri:c2=tri")
            else:
                filters.append(f"{in1}{in2}acrossfade=d={cf}:c1=tri:c2=tri[a{i+1}]")
        fc = ";".join(filters)

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", fc, output]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Crossfade failed, falling back to concat")
        concat_file = output + ".txt"
        with open(concat_file, "w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output], capture_output=True)
        os.remove(concat_file)

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate EP4 trilingual English podcast")
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--crossfade", type=int, default=CROSSFADE_MS)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    # Load env
    env_file = os.path.expanduser("~/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    el_key = os.environ.get("ELEVENLABS_API_KEY")
    volc_app = os.environ.get("VOLC_PODCAST_APP_ID", "")
    volc_token = os.environ.get("VOLC_PODCAST_ACCESS_TOKEN", "")

    if not el_key:
        print("❌ ELEVENLABS_API_KEY not set"); sys.exit(1)
    if not volc_app or not volc_token:
        print("❌ VOLC_PODCAST_APP_ID / VOLC_PODCAST_ACCESS_TOKEN not set"); sys.exit(1)

    print(f"📖 Parsing {args.transcript}...")
    segments = parse_transcript(args.transcript)
    print(f"   Found {len(segments)} segments")
    
    # Count by speaker
    speakers = {}
    for s in segments:
        speakers[s["speaker"]] = speakers.get(s["speaker"], 0) + 1
    for sp, cnt in speakers.items():
        engine = "ElevenLabs" if sp in ELEVENLABS_VOICES else "Volcengine"
        print(f"   {sp}: {cnt} segments → {engine}")

    seg_dir = Path(args.output).parent / "segments-en"
    seg_dir.mkdir(parents=True, exist_ok=True)

    segment_paths = []
    for i, seg in enumerate(segments):
        speaker = seg["speaker"]
        seg_path = str(seg_dir / f"segment_{i:03d}_{speaker}.mp3")
        segment_paths.append(seg_path)

        if args.skip_existing and os.path.exists(seg_path) and os.path.getsize(seg_path) > 0:
            print(f"  ⏭️  [{i+1}/{len(segments)}] {speaker} (exists)")
            continue

        preview = seg["text"][:60].replace("\n", " ")

        if speaker in ELEVENLABS_VOICES:
            voice = ELEVENLABS_VOICES[speaker]
            print(f"  🎤 [{i+1}/{len(segments)}] {speaker} ({voice['name']}): {preview}...")
            ok = synth_elevenlabs(el_key, voice["voice_id"], seg["text"], seg_path)
        elif speaker == "pinch":
            print(f"  🎤 [{i+1}/{len(segments)}] {speaker} (Volcengine): {preview}...")
            ok = synth_volcengine(volc_app, volc_token, seg["text"], seg_path)
        else:
            print(f"  ⚠️  Unknown speaker '{speaker}', skipping")
            continue

        if ok:
            size_kb = os.path.getsize(seg_path) / 1024
            print(f"     ✅ {size_kb:.0f} KB")
        else:
            print(f"     ❌ Failed")

        time.sleep(0.5)

    existing = [p for p in segment_paths if os.path.exists(p) and os.path.getsize(p) > 0]
    print(f"\n🔗 Merging {len(existing)} segments...")
    crossfade_concat(existing, args.output, args.crossfade)

    if os.path.exists(args.output):
        size_mb = os.path.getsize(args.output) / (1024 * 1024)
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", args.output],
            capture_output=True, text=True,
        )
        dur = float(result.stdout.strip()) if result.stdout.strip() else 0
        print(f"\n✅ Done! {args.output}")
        print(f"   {size_mb:.1f} MB | {int(dur//60)}m{int(dur%60):02d}s")
    else:
        print("\n❌ Output not created")
        sys.exit(1)


if __name__ == "__main__":
    main()
