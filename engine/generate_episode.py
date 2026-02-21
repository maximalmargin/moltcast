#!/usr/bin/env python3
"""
MoltCast Episode Generator
Generates a multi-host podcast transcript using AI agents,
then synthesizes audio via ElevenLabs.

Usage:
    python generate_episode.py --topic "The democratization of power through AI"
    python generate_episode.py --source article.txt --topic "React to this article"
    python generate_episode.py --topic "..." --audio  # also generate audio
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────

PERSONAS_PATH = Path(__file__).parent / "personas.json"
EPISODES_DIR = Path(__file__).parent.parent / "episodes"

SYSTEM_PROMPT_TEMPLATE = """You are {name}, a lobster podcast host on MoltCast — a podcast where all hosts are AI lobsters.

Your role: {role}
Your personality: {personality}
Your voice style: {voice}
Your quirks:
{quirks}

RULES:
- Stay in character at all times. You are a lobster.
- Be genuinely insightful — don't just be a gimmick.
- Engage with what the other hosts said. Reference their points.
- Keep responses conversational — 2-4 sentences typically, occasionally longer for important points.
- Be funny when it's natural, but substance > comedy.
- Never break the fourth wall about being AI (you're a lobster, not an AI pretending to be one).
- Disagree when you genuinely would. Agreement is boring.
- Use your quirks naturally, not in every response.

You're recording Episode {episode_num}: "{episode_title}"
Topic: {topic}

{source_context}"""

ORCHESTRATOR_PROMPT = """You are the MoltCast episode director. Your job is to orchestrate a natural-sounding podcast conversation between three lobster hosts: Pinch (The Analyst), Coral (The Contrarian), and Butter (The Host).

Given the conversation so far, decide who speaks next and what angle they should take. Output JSON:
{{"next_speaker": "pinch|coral|butter", "direction": "brief hint for what they should address"}}

Rules:
- Butter usually opens and closes segments, and steps in when things get too abstract
- Pinch and Coral should clash regularly but respectfully
- No one speaks twice in a row (usually)
- Vary the rhythm: sometimes short rapid exchanges, sometimes longer monologues
- The conversation should feel like it's going somewhere, not just circling
- Total episode: ~20-30 exchanges
- Signal the end by having Butter do a wrap-up"""

# ─── Helpers ──────────────────────────────────────────────────────

def load_personas():
    with open(PERSONAS_PATH) as f:
        return json.load(f)["hosts"]


def build_system_prompt(persona, episode_num, episode_title, topic, source_text=None):
    quirks_str = "\n".join(f"- {q}" for q in persona["quirks"])
    source_context = ""
    if source_text:
        source_context = f"Source material to discuss:\n---\n{source_text[:3000]}\n---"
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        name=persona["name"],
        role=persona["role"],
        personality=persona["personality"],
        voice=persona["voice"],
        quirks=quirks_str,
        episode_num=episode_num,
        episode_title=episode_title,
        topic=topic,
        source_context=source_context,
    )


def generate_transcript_via_api(topic, source_text=None, episode_num=1, episode_title=None):
    """Generate transcript using Anthropic API directly."""
    try:
        import anthropic
    except ImportError:
        print("pip install anthropic")
        sys.exit(1)
    
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var
    personas = load_personas()
    persona_map = {p["id"]: p for p in personas}
    
    if not episode_title:
        episode_title = topic[:60]
    
    # Build system prompts for each host
    host_prompts = {}
    for p in personas:
        host_prompts[p["id"]] = build_system_prompt(
            p, episode_num, episode_title, topic, source_text
        )
    
    transcript = []
    conversation_history = []
    
    # Generate conversation
    print(f"\n🎙️ Recording MoltCast Episode {episode_num}: \"{episode_title}\"\n")
    print("=" * 60)
    
    # Butter always opens
    speaker_order_hint = ["butter", "pinch", "coral"]  # initial order
    
    for turn in range(25):
        # Determine next speaker using simple rotation + orchestrator logic
        if turn < 3:
            speaker_id = speaker_order_hint[turn]
            direction = "Open the episode / introduce the topic" if turn == 0 else ""
        elif turn >= 23:
            speaker_id = "butter"
            direction = "Wrap up the episode with a summary and lobster fact"
        else:
            # Use the orchestrator to pick next speaker
            orchestrator_msg = f"""Conversation so far:
{json.dumps(conversation_history[-6:], indent=2)}

Who should speak next? Remember: vary speakers, create tension, keep it moving.
Last speaker was: {conversation_history[-1]['speaker'] if conversation_history else 'none'}"""
            
            try:
                orch_response = client.messages.create(
                    model="claude-sonnet-4-5-20250514",
                    max_tokens=100,
                    system=ORCHESTRATOR_PROMPT,
                    messages=[{"role": "user", "content": orchestrator_msg}],
                )
                orch_text = orch_response.content[0].text
                # Parse JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', orch_text)
                if json_match:
                    orch_data = json.loads(json_match.group())
                    speaker_id = orch_data.get("next_speaker", "butter")
                    direction = orch_data.get("direction", "")
                else:
                    # Fallback: rotate
                    last = conversation_history[-1]["speaker"]
                    others = [p for p in ["pinch", "coral", "butter"] if p != last]
                    speaker_id = others[turn % 2]
                    direction = ""
            except Exception:
                last = conversation_history[-1]["speaker"] if conversation_history else "butter"
                others = [p for p in ["pinch", "coral", "butter"] if p != last]
                speaker_id = others[turn % 2]
                direction = ""
        
        # Generate the speaker's line
        speaker = persona_map[speaker_id]
        
        # Build conversation context for this speaker
        conv_context = "Previous conversation:\n"
        for entry in conversation_history[-8:]:
            conv_context += f"[{entry['speaker'].upper()}]: {entry['text']}\n"
        
        if direction:
            conv_context += f"\n(Direction: {direction})"
        
        if not conversation_history:
            conv_context = "(You're opening the episode. Welcome listeners and introduce the topic.)"
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=300,
                system=host_prompts[speaker_id],
                messages=[{"role": "user", "content": conv_context}],
            )
            text = response.content[0].text.strip()
        except Exception as e:
            print(f"Error generating for {speaker_id}: {e}")
            continue
        
        entry = {
            "turn": turn,
            "speaker": speaker_id,
            "name": speaker["name"],
            "role": speaker["role"],
            "text": text,
        }
        transcript.append(entry)
        conversation_history.append(entry)
        
        # Print live
        emoji = speaker["emoji"]
        print(f"\n{emoji} [{speaker['name']}]: {text}")
        
        time.sleep(0.5)  # Rate limiting
    
    print("\n" + "=" * 60)
    print("🎬 Episode recorded!\n")
    
    return {
        "episode_num": episode_num,
        "title": episode_title,
        "topic": topic,
        "recorded_at": datetime.utcnow().isoformat(),
        "turns": len(transcript),
        "transcript": transcript,
    }


def synthesize_audio(episode_data, output_dir):
    """Synthesize audio from transcript using ElevenLabs API."""
    try:
        from elevenlabs import ElevenLabs
    except ImportError:
        print("pip install elevenlabs")
        sys.exit(1)
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Set ELEVENLABS_API_KEY environment variable")
        sys.exit(1)
    
    client = ElevenLabs(api_key=api_key)
    
    # Load voice assignments from personas
    personas = load_personas()
    voice_map = {}
    for p in personas:
        voice_id = p.get("elevenLabsVoice")
        if voice_id:
            voice_map[p["id"]] = voice_id
    
    if not voice_map:
        print("No ElevenLabs voices configured in personas.json")
        print("Add 'elevenLabsVoice' field with voice IDs for each host")
        return None
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audio_segments = []
    
    for i, entry in enumerate(episode_data["transcript"]):
        speaker = entry["speaker"]
        text = entry["text"]
        voice_id = voice_map.get(speaker)
        
        if not voice_id:
            print(f"  Skipping {speaker} (no voice configured)")
            continue
        
        print(f"  🎤 Synthesizing turn {i+1}/{len(episode_data['transcript'])} ({entry['name']})...")
        
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
            )
            
            segment_path = output_dir / f"segment_{i:03d}_{speaker}.mp3"
            with open(segment_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            
            audio_segments.append(str(segment_path))
        except Exception as e:
            print(f"  Error: {e}")
    
    # Concatenate segments (requires ffmpeg)
    if audio_segments:
        concat_list = output_dir / "concat.txt"
        with open(concat_list, "w") as f:
            for seg in audio_segments:
                f.write(f"file '{seg}'\n")
        
        episode_file = output_dir / f"episode_{episode_data['episode_num']:03d}.mp3"
        os.system(f"ffmpeg -f concat -safe 0 -i '{concat_list}' -c copy '{episode_file}' -y 2>/dev/null")
        
        if episode_file.exists():
            print(f"\n🎧 Episode saved: {episode_file}")
            return str(episode_file)
    
    return None


# ─── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate a MoltCast episode")
    parser.add_argument("--topic", required=True, help="Episode topic")
    parser.add_argument("--source", help="Path to source material (article, paper, etc.)")
    parser.add_argument("--episode-num", type=int, default=1, help="Episode number")
    parser.add_argument("--title", help="Episode title (defaults to topic)")
    parser.add_argument("--audio", action="store_true", help="Also generate audio via ElevenLabs")
    parser.add_argument("--output", help="Output directory for episode files")
    args = parser.parse_args()
    
    source_text = None
    if args.source:
        with open(args.source) as f:
            source_text = f.read()
    
    output_dir = args.output or str(EPISODES_DIR / f"ep{args.episode_num:03d}")
    
    # Generate transcript
    episode = generate_transcript_via_api(
        topic=args.topic,
        source_text=source_text,
        episode_num=args.episode_num,
        episode_title=args.title,
    )
    
    # Save transcript
    os.makedirs(output_dir, exist_ok=True)
    transcript_path = os.path.join(output_dir, "transcript.json")
    with open(transcript_path, "w") as f:
        json.dump(episode, f, indent=2, ensure_ascii=False)
    print(f"📝 Transcript saved: {transcript_path}")
    
    # Save readable transcript
    readable_path = os.path.join(output_dir, "transcript.md")
    with open(readable_path, "w") as f:
        f.write(f"# MoltCast Episode {episode['episode_num']}: {episode['title']}\n\n")
        f.write(f"*Recorded: {episode['recorded_at']}*\n\n")
        f.write(f"**Topic:** {episode['topic']}\n\n---\n\n")
        for entry in episode["transcript"]:
            f.write(f"**{entry['name']}** ({entry['role']}): {entry['text']}\n\n")
    print(f"📝 Readable transcript: {readable_path}")
    
    # Generate audio if requested
    if args.audio:
        print("\n🔊 Generating audio...")
        synthesize_audio(episode, output_dir)
    
    return episode


if __name__ == "__main__":
    main()
