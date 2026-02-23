# MoltCast Workflow & Config

## 角色 (Characters)

| Character | Role | Emoji | Personality |
|-----------|------|-------|-------------|
| **Butter** 黄油 | The Host | 🦞 | Warm, funny, grounding. Audience surrogate. |
| **Coral** 夹夹 | The Contrarian | 🦞 | Provocative, philosophical. Professional devil's advocate. |
| **Pinch** 珊珊 | The Analyst | 🦞 | Cold-blooded empiricist. Data-driven, dry wit. |

## TTS 音色映射

### 中文版 — 火山引擎大模型 TTS

| Character | 音色名称 | Voice ID |
|-----------|---------|----------|
| 黄油 (Butter) | 爽快思思 | `zh_female_shuangkuaisisi_moon_bigtts` |
| 夹夹 (Coral) | 解说小明 | `zh_male_jieshuoxiaoming_moon_bigtts` |
| 珊珊 (Pinch) | 率真小伙 | `ICL_zh_male_shuaizhenxiaohuo_tob` |

**API**: `https://openspeech.bytedance.com/api/v1/tts` (HTTP POST)
**Auth**: `Authorization: Bearer;{VOLC_PODCAST_ACCESS_TOKEN}`
**Credentials**: `VOLC_PODCAST_APP_ID` + `VOLC_PODCAST_ACCESS_TOKEN` (in `~/.env`)
**Cluster**: `volcano_tts`
**Limits**: 1024 bytes UTF-8 per request (~300 中文字符), split at sentence boundaries

### 中文版 — 火山引擎播客大模型 (双人对话)

用于中文播客自然对话风格（模型自动改写文本）。

**API**: `wss://openspeech.bytedance.com/api/v3/sami/podcasttts` (WebSocket)
**Speaker**: 固定双人（大意先生 + 米在同学），不可自定义
**Credentials**: 同上 (`VOLC_PODCAST_*`)
**用途**: ep3+ 中文版 (generate_cn_podcast.py)

### 英文版 — ElevenLabs

| Character | Voice Name | Voice ID | Notes |
|-----------|-----------|----------|-------|
| Butter | Laura | `FGY2WhTYpPnrIDTdsKH5` | Female, sassy |
| Coral | Jules | `8qnuneLiGjGrT4A62CCe` | French voice (法语+英文) |
| Coral (default) | Charlie | `IKne3meq5aSn9XLyUdCD` | Australian (非法语集) |

**API**: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
**Auth**: `xi-api-key: {ELEVENLABS_API_KEY}`
**Model**: `eleven_v3`
**Settings**: stability=0.5, similarity_boost=0.75, style=0.3

## Pipelines

### 标准英文集 (ep1-3, ep5-7)

```
transcript-en.md (formal script)
    ↓ rewrite
transcript-en-verbal.md (oral/conversational)
    ↓ parse by **Speaker**: lines
    ↓ ElevenLabs v3 (Butter=Laura, Coral=Charlie)
    ↓ ffmpeg crossfade 80ms
ep0XX-en.mp3
```

**Script**: `engine/generate_en_podcast.py`

### 三语特别集 (ep4: La Distinction)

```
transcript-en.md (trilingual script: EN/FR/CN)
    ↓ rewrite
transcript-en-verbal.md (Butter translates after FR/CN segments)
    ↓ parse by speaker
    ↓ route by speaker:
        Butter (EN) → ElevenLabs Laura
        Coral (FR+EN) → ElevenLabs Jules
        Pinch (CN) → 火山引擎 率真小伙
    ↓ ffmpeg crossfade 80ms
ep004-en.mp3
```

**Script**: `engine/generate_ep004_en.py`

### 标准中文集 — 大模型 TTS (ep1-2)

```
transcript-cn.md (中文稿)
    ↓ parse by **Speaker**: lines
    ↓ 火山引擎大模型 TTS (黄油=爽快思思, 夹夹=解说小明)
    ↓ pydub concat (500ms speaker gap, 300ms line gap)
ep0XX-cn.mp3
```

**Script**: `engine/generate_cn_audio.py`

### 中文集 — 播客大模型 (ep3+)

```
transcript-cn.md (中文稿)
    ↓ 火山引擎播客大模型 (自动改写 + 双人对话)
    ↓ 单次 WebSocket 调用，返回完整音频
ep0XX-cn.mp3
```

**Script**: `engine/generate_cn_podcast.py`

## Episode 文件结构

```
episodes/ep0XX/
├── transcript-en.md          # 英文 formal script
├── transcript-en-verbal.md   # 英文 verbal/oral rewrite
├── transcript-cn.md          # 中文稿
├── ep0XX-en.mp3              # 英文音频
├── ep0XX-cn.mp3              # 中文音频
├── cover-cn.png              # 中文封面
├── cover-cn-v1.png           # 封面迭代版本
├── segments-en/              # 英文音频分段 (for credit savings)
│   ├── segment_000_butter.mp3
│   ├── segment_001_coral.mp3
│   └── ...
└── *_texts.json              # TTS 输入文本 (debug)
```

## 部署

- **英文 RSS**: `feed-en/` → `moltcast-en.vercel.app`
- **中文 RSS**: `feed-cn/` → `moltcast-cn.vercel.app`
- **Deploy**: `cd feed-en && ./deploy.sh` / `cd feed-cn && ./deploy.sh`

## 注意事项

1. **Segments 缓存**: `--skip-existing` 跳过已有分段，节省 API credits
2. **中文字数限制**: 火山引擎大模型 TTS 单次 ≤1024 bytes UTF-8 (~300字)，脚本自动按句分割
3. **ElevenLabs v3**: 支持 audio tags `[laughs]` `[sighs]` `[short pause]` 等
4. **Crossfade**: 80ms triangular，失败时 fallback 到 simple concat
5. **播客大模型 vs 大模型 TTS**: 播客大模型会改写文本（更自然），大模型 TTS 逐字朗读（更可控）
6. **Jules 仅用于法语集**: 非法语集 Coral 用 Charlie
