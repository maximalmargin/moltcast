# English Podcast Pipeline

## Overview

```
transcript-en.md (script)
    ↓ manual rewrite
transcript-en-verbal.md (conversational, oral style)
    ↓ parse by speaker
segments-en/segment_001_butter.mp3, segment_002_coral.mp3, ...
    ↓ ElevenLabs v3 TTS
    ↓ ffmpeg crossfade concat (80ms)
ep0XX-en.mp3
```

## Voices

| Character | Voice Name | Voice ID | Style |
|-----------|-----------|----------|-------|
| **Butter** (Host) | Laura | `FGY2WhTYpPnrIDTdsKH5` | Female, sassy |
| **Coral** (Analyst) | Charlie | `IKne3meq5aSn9XLyUdCD` | Australian |

## TTS Config

- **Model**: `eleven_v3` (most expressive)
- **Stability**: 0.5
- **Similarity boost**: 0.75
- **Style**: 0.3 (natural, not over-dramatic)
- **Format**: MP3, 44.1kHz, 128kbps

## Audio Tags (v3 supported)

Add these in `transcript-en-verbal.md` for expressiveness:

```
[laughs]  [sighs]  [whispers]  [shouts]
[short pause]  [long pause]  [pause]
[sarcastic]  [curious]  [excited]  [crying]
```

## Crossfade

- 80ms triangular crossfade between segments
- Prevents hard cuts between speakers
- Fallback: simple concat if crossfade fails

## Usage

```bash
source ~/.env
cd ~/repos/moltcast

# Generate (saves segments individually)
python3 engine/generate_en_podcast.py \
    --transcript episodes/ep003/transcript-en-verbal.md \
    --output episodes/ep003/ep003-en.mp3

# Resume after failure (skips existing segments)
python3 engine/generate_en_podcast.py \
    --transcript episodes/ep003/transcript-en-verbal.md \
    --output episodes/ep003/ep003-en.mp3 \
    --skip-existing
```

## Verbal Transcript Guidelines

The verbal version rewrites the script for spoken delivery:

1. **Fillers**: "right?", "I mean", "like", "okay", "look"
2. **Reactions**: "Ha!", "Wait—", "...seriously?"
3. **Interruptions**: One speaker reacting mid-thought
4. **No role labels**: Just `**Butter**:` not `**Butter** (The Host):`
5. **Audio tags**: `[laughs]`, `[short pause]` where natural
6. **Keep all info**: Same facts/arguments, just oral delivery

## Speed

- Default: 1.0x (v3 natural pacing)
- Speed-up is a post-production decision, not baked in
- If needed: `ffmpeg -i input.mp3 -filter:a "atempo=1.15" output.mp3`

## Credit Savings

- Segments saved individually — never re-generate what exists
- Use `--skip-existing` to resume
- Each segment ~100-500 chars → small API calls
- v3 costs more per char than v2, but sounds much better

## Comparison with CN Pipeline

| | CN (豆包) | EN (ElevenLabs) |
|---|---|---|
| Oral rewrite | action=0 (auto) | manual verbal transcript |
| TTS | Single call, dual-speaker | Per-segment, single-speaker |
| Concat | Built-in | ffmpeg crossfade |
| Natural feel | Very high (native dual) | Good (v3 + crossfade) |
| Model | 豆包语音播客模型 | eleven_v3 |
