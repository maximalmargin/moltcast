#!/usr/bin/env python3
"""Generate Chinese podcast audio using Volcengine 豆包·语音播客模型.

Usage:
    python generate_cn_podcast.py --transcript ../episodes/ep003/transcript-cn.md --output ../episodes/ep003/ep003-cn.mp3
"""
import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
import uuid

import websockets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from protocols import (
    EventType,
    MsgType,
    finish_connection,
    finish_session,
    receive_message,
    start_connection,
    start_session,
    wait_for_event,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PodcastTTS")

ENDPOINT = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"


def extract_dialogue(transcript_path: str) -> str:
    """Extract dialogue text from transcript markdown, stripping metadata."""
    with open(transcript_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove markdown header lines (title, recording date, theme)
    lines = content.split("\n")
    dialogue_lines = []
    in_dialogue = False
    for line in lines:
        # Start capturing after the --- separator
        if line.strip() == "---":
            if in_dialogue:
                # Second --- means end section
                continue
            in_dialogue = True
            continue
        if in_dialogue and line.strip():
            # Clean up markdown bold markers for speaker names
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            # Remove italic markers
            cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
            dialogue_lines.append(cleaned)

    return "\n".join(dialogue_lines)


async def generate_podcast(appid: str, access_token: str, text: str, output_path: str,
                          encoding: str = "mp3"):
    """Generate podcast audio via Volcengine podcast model."""
    headers = {
        "X-Api-App-Id": appid,
        "X-Api-App-Key": "aGjiRDfUWi",
        "X-Api-Access-Key": access_token,
        "X-Api-Resource-Id": "volc.service_type.10050",
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }

    req_params = {
        "input_id": f"moltcast_ep003_cn_{int(time.time())}",
        "input_text": text,
        "action": 0,
        "use_head_music": True,
        "use_tail_music": True,
        "input_info": {
            "return_audio_url": False,
            "only_nlp_text": False,
        },
        "speaker_info": {"random_order": False},
        "audio_config": {
            "format": encoding,
            "sample_rate": 24000,
            "speech_rate": 0,
        },
    }

    is_podcast_round_end = True
    last_round_id = -1
    task_id = ""
    retry_num = 5
    podcast_audio = bytearray()
    audio = bytearray()
    voice = ""
    current_round = 0
    podcast_texts = []

    while retry_num > 0:
        websocket = await websockets.connect(ENDPOINT, additional_headers=headers)
        logger.info(f"Connected to {ENDPOINT}")

        if not is_podcast_round_end:
            req_params["retry_info"] = {
                "retry_task_id": task_id,
                "last_finished_round_id": last_round_id,
            }

        try:
            # StartConnection
            await start_connection(websocket)
            await wait_for_event(websocket, MsgType.FullServerResponse, EventType.ConnectionStarted)
            logger.info("Connection started")

            session_id = str(uuid.uuid4())
            if not task_id:
                task_id = session_id

            # StartSession with text
            await start_session(websocket, json.dumps(req_params).encode(), session_id)
            await wait_for_event(websocket, MsgType.FullServerResponse, EventType.SessionStarted)
            logger.info("Session started")

            # FinishSession (signal all input sent)
            await finish_session(websocket, session_id)

            while True:
                msg = await receive_message(websocket)

                if msg.type == MsgType.AudioOnlyServer and msg.event == EventType.PodcastRoundResponse:
                    audio.extend(msg.payload)
                    if len(audio) % (50 * 1024) < len(msg.payload):
                        logger.info(f"Audio chunk received, total round bytes: {len(audio)}")

                elif msg.type == MsgType.Error:
                    raise RuntimeError(f"Server error: {msg.payload.decode()}")

                elif msg.type == MsgType.FullServerResponse:
                    if msg.event == EventType.PodcastRoundStart:
                        data = json.loads(msg.payload.decode())
                        voice = data.get("speaker", "unknown")
                        current_round = data.get("round_id", 0)
                        if current_round == -1:
                            voice = "head_music"
                        if current_round == 9999:
                            voice = "tail_music"
                        is_podcast_round_end = False
                        text_preview = data.get("text", "")[:50]
                        logger.info(f"Round {current_round} started: [{voice}] {text_preview}...")
                        if data.get("text"):
                            podcast_texts.append({"text": data["text"], "speaker": voice})

                    elif msg.event == EventType.PodcastRoundEnd:
                        data = json.loads(msg.payload.decode())
                        if data.get("is_error"):
                            logger.error(f"Round error: {data}")
                            break
                        is_podcast_round_end = True
                        last_round_id = current_round
                        if audio:
                            podcast_audio.extend(audio)
                            logger.info(f"Round {current_round} [{voice}] done: {len(audio)} bytes")
                            audio.clear()

                    elif msg.event == EventType.PodcastEnd:
                        data = json.loads(msg.payload.decode())
                        logger.info(f"Podcast end: {data}")

                if msg.event == EventType.SessionFinished:
                    break

            # FinishConnection
            await finish_connection(websocket)
            await wait_for_event(websocket, MsgType.FullServerResponse, EventType.ConnectionFinished)

            if is_podcast_round_end:
                # Save final audio
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(podcast_audio)
                logger.info(f"✅ Final audio saved: {output_path} ({len(podcast_audio)} bytes)")

                # Save generated texts
                texts_path = output_path.rsplit(".", 1)[0] + "_texts.json"
                with open(texts_path, "w", encoding="utf-8") as f:
                    json.dump(podcast_texts, f, ensure_ascii=False, indent=2)
                logger.info(f"Texts saved: {texts_path}")
                break
            else:
                logger.warning(f"Podcast not finished, retrying from round {last_round_id}")
                retry_num -= 1
                await asyncio.sleep(1)
        finally:
            await websocket.close()

    return output_path


async def main():
    parser = argparse.ArgumentParser(description="Generate podcast audio with Volcengine")
    parser.add_argument("--transcript", required=True, help="Path to transcript markdown")
    parser.add_argument("--output", required=True, help="Output audio path")
    parser.add_argument("--encoding", default="mp3", choices=["mp3", "wav"])
    parser.add_argument("--raw-text", action="store_true", help="Pass transcript as raw text (no parsing)")
    args = parser.parse_args()

    # Load credentials from env
    appid = os.environ.get("VOLC_PODCAST_APP_ID", "")
    access_token = os.environ.get("VOLC_PODCAST_ACCESS_TOKEN", "")
    if not appid or not access_token:
        logger.error("Set VOLC_PODCAST_APP_ID and VOLC_PODCAST_ACCESS_TOKEN env vars")
        sys.exit(1)

    if args.raw_text:
        with open(args.transcript, "r") as f:
            text = f.read()
    else:
        text = extract_dialogue(args.transcript)

    logger.info(f"Input text length: {len(text)} chars")
    logger.info(f"First 200 chars: {text[:200]}")

    await generate_podcast(appid, access_token, text, args.output, args.encoding)


if __name__ == "__main__":
    asyncio.run(main())
