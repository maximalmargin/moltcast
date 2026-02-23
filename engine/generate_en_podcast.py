#!/usr/bin/env python3
"""Generate English podcast audio from verbal transcript using ElevenLabs API.

Usage:
    source ~/.env
    python3 generate_en_podcast.py --transcript episodes/ep003/transcript-en-verbal.md --output episodes/ep003/ep003-en.mp3

Saves individual segments to {output_dir}/segments-en/ for credit savings.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

# Voice assignments
VOICES = {
    "butter": {
        "voice_id": "FGY2WhTYpPnrIDTdsKH5",  # Laura (female, sassy)
        "name": "Laura",
    },
    "coral": {
        "voice_id": "IKne3meq5aSn9XLyUdCD",  # Charlie (Australian)
        "name": "Charlie",
    },
}

MODEL_ID = "eleven_v3"
API_BASE = "https://api.elevenlabs.io/v1"
CROSSFADE_MS = 80  # crossfade duration between segments


def parse_transcript(transcript_path: str) -> list[dict]:
    """Parse verbal transcript into list of {speaker, text} segments."""
    segments = []
    current_speaker = None
    current_text = []

    with open(transcript_path) as f:
        for line in f:
            line = line.rstrip()

            # Match speaker lines: **Butter**: text or **Coral**: text
            match = re.match(r'\*\*(\w+)\*\*:\s*(.*)', line)
            if match:
                # Save previous segment
                if current_speaker and current_text:
                    text = "\n".join(current_text).strip()
                    if text:
                        segments.append({
                            "speaker": current_speaker.lower(),
                            "text": text,
                        })

                current_speaker = match.group(1)
                current_text = [match.group(2)] if match.group(2) else []
            elif current_speaker and line and not line.startswith('#') and not line.startswith('*') and not line.startswith('---'):
                # Continuation of current speaker's text
                current_text.append(line)

    # Save last segment
    if current_speaker and current_text:
        text = "\n".join(current_text).strip()
        if text:
            segments.append({
                "speaker": current_speaker.lower(),
                "text": text,
            })

    return segments


def synthesize_segment(api_key: str, voice_id: str, text: str, output_path: str) -> bool:
    """Synthesize a single segment via ElevenLabs API."""
    url = f"{API_BASE}/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    data = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
        },
    }

    resp = requests.post(url, headers=headers, json=data, timeout=120)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    else:
        print(f"  ❌ API error {resp.status_code}: {resp.text[:200]}")
        return False


def crossfade_concat(segment_paths: list[str], output_path: str, crossfade_ms: int = 80):
    """Concatenate audio segments with crossfade using ffmpeg."""
    if len(segment_paths) == 0:
        return
    if len(segment_paths) == 1:
        subprocess.run(["cp", segment_paths[0], output_path])
        return

    # Build ffmpeg filter chain for crossfade
    # For N inputs, we need N-1 crossfade operations
    n = len(segment_paths)
    inputs = []
    for p in segment_paths:
        inputs.extend(["-i", p])

    crossfade_s = crossfade_ms / 1000.0

    if n == 2:
        filter_complex = f"[0][1]acrossfade=d={crossfade_s}:c1=tri:c2=tri"
    else:
        # Chain crossfades: [0][1] -> [a1], [a1][2] -> [a2], etc.
        filters = []
        for i in range(n - 1):
            if i == 0:
                in1 = "[0]"
                in2 = "[1]"
            else:
                in1 = f"[a{i}]"
                in2 = f"[{i+1}]"

            if i == n - 2:
                out = ""  # final output, no label
                filters.append(f"{in1}{in2}acrossfade=d={crossfade_s}:c1=tri:c2=tri")
            else:
                out = f"[a{i+1}]"
                filters.append(f"{in1}{in2}acrossfade=d={crossfade_s}:c1=tri:c2=tri{out}")

        filter_complex = ";".join(filters)

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Crossfade failed, falling back to simple concat")
        print(f"  stderr: {result.stderr[:300]}")
        # Fallback: simple concat
        concat_file = output_path + ".concat.txt"
        with open(concat_file, "w") as f:
            for p in segment_paths:
                f.write(f"file '{p}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file, "-c", "copy", output_path
        ], capture_output=True)
        os.remove(concat_file)


def main():
    parser = argparse.ArgumentParser(description="Generate English podcast from verbal transcript")
    parser.add_argument("--transcript", required=True, help="Path to transcript-en-verbal.md")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--crossfade", type=int, default=CROSSFADE_MS, help="Crossfade duration in ms")
    parser.add_argument("--skip-existing", action="store_true", help="Skip segments that already exist")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ Set ELEVENLABS_API_KEY environment variable")
        sys.exit(1)

    # Parse transcript
    print(f"📖 Parsing {args.transcript}...")
    segments = parse_transcript(args.transcript)
    print(f"   Found {len(segments)} segments")

    if not segments:
        print("❌ No segments found")
        sys.exit(1)

    # Create segments directory
    output_dir = Path(args.output).parent / "segments-en"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate each segment
    segment_paths = []
    for i, seg in enumerate(segments):
        speaker = seg["speaker"]
        voice = VOICES.get(speaker)
        if not voice:
            print(f"  ⚠️ Unknown speaker '{speaker}', skipping")
            continue

        segment_path = str(output_dir / f"segment_{i:03d}_{speaker}.mp3")
        segment_paths.append(segment_path)

        if args.skip_existing and os.path.exists(segment_path) and os.path.getsize(segment_path) > 0:
            print(f"  ⏭️  [{i+1}/{len(segments)}] {speaker} (exists, skipping)")
            continue

        text_preview = seg["text"][:60].replace("\n", " ")
        print(f"  🎤 [{i+1}/{len(segments)}] {speaker} ({voice['name']}): {text_preview}...")

        success = synthesize_segment(api_key, voice["voice_id"], seg["text"], segment_path)
        if not success:
            print(f"  ❌ Failed to generate segment {i+1}")
            continue

        size_kb = os.path.getsize(segment_path) / 1024
        print(f"     ✅ {size_kb:.0f} KB")

        # Rate limiting — be gentle
        time.sleep(0.5)

    # Filter to existing segments
    existing_paths = [p for p in segment_paths if os.path.exists(p) and os.path.getsize(p) > 0]
    print(f"\n🔗 Concatenating {len(existing_paths)} segments with {args.crossfade}ms crossfade...")
    crossfade_concat(existing_paths, args.output, args.crossfade)

    if os.path.exists(args.output):
        size_mb = os.path.getsize(args.output) / (1024 * 1024)
        # Get duration
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", args.output],
            capture_output=True, text=True
        )
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"\n✅ Done! {args.output}")
        print(f"   {size_mb:.1f} MB | {minutes}m{seconds:02d}s")
    else:
        print("\n❌ Output file not created")
        sys.exit(1)


if __name__ == "__main__":
    main()
