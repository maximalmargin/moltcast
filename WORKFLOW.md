# MoltCast Workflow & Config

## 角色 (Characters)

| Character | Role | Emoji | Personality |
|-----------|------|-------|-------------|
| **Butter** 黄油 | The Host | 🦞 | Warm, funny, grounding. Audience surrogate. |
| **Pinch** 夹夹 | The Analyst | 🦞 | Cold-blooded empiricist. Data-driven, dry wit. |
| **Coral** 珊珊 | The Contrarian | 🦞 | Provocative, philosophical. Professional devil's advocate. |

## TTS 音色映射

### 中文版 — 豆包语音合成大模型

| Character | 音色名称 | Voice ID |
|-----------|---------|----------|
| 黄油 (Butter) | 爽快思思 | `zh_female_shuangkuaisisi_moon_bigtts` |
| 夹夹 (Pinch) | 解说小明 | `zh_male_jieshuoxiaoming_moon_bigtts` |
| 珊珊 (Coral) | 率真小伙 | `ICL_zh_male_shuaizhenxiaohuo_tob` |

**API**: `https://openspeech.bytedance.com/api/v1/tts` (HTTP POST)
**Auth**: `Authorization: Bearer;{VOLC_PODCAST_ACCESS_TOKEN}`
**Credentials**: `VOLC_PODCAST_APP_ID` + `VOLC_PODCAST_ACCESS_TOKEN` (in `~/.env`)
**Cluster**: `volcano_tts`
**Limits**: 1024 bytes UTF-8 per request (~300 中文字符), split at sentence boundaries

### 中文版 — 火山引擎播客大模型 (双人对话)

用于中文播客自然对话风格（模型自动改写文本）。

**文档**: https://www.volcengine.com/docs/6561/1668014?lang=zh
**API**: `wss://openspeech.bytedance.com/api/v3/sami/podcasttts` (WebSocket)
**Speaker**: 固定双人，不可自定义

| Speaker | Voice ID |
|---------|----------|
| 大意先生 | `zh_male_dayixiansheng_v2_saturn_bigtts` |
| 米在同学 | `zh_female_mizaitongxue_v2_saturn_bigtts` |

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

### 标准中文集 — 豆包语音合成大模型 (ep1-2)

```
transcript-cn.md (中文稿)
    ↓ parse by **Speaker**: lines
    ↓ 豆包语音合成大模型 (黄油=爽快思思, 夹夹=解说小明)
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

**统一站点**: `site/` → `moltcast-mm.vercel.app`

```
site/
├── index.html           # 主页 (EN/CN 语言切换)
├── rss-en.xml           # English RSS feed
├── rss-cn.xml           # 中文 RSS feed
├── vercel.json          # Vercel 配置 (cleanUrls, headers)
├── cover.jpg            # 封面
├── episodes/            # 所有音频 (EN + CN)
│   ├── ep001/ ... ep007/
├── transcript/          # 文字稿 HTML 页面
│   ├── ep001-en.html ... ep007-cn.html
└── generate_transcripts.py  # 从 markdown 生成文字稿 HTML
```

**部署命令**:
```bash
cd ~/repos/moltcast/site && vercel --yes --prod
```

**RSS 链接**:
- EN: `https://moltcast-mm.vercel.app/rss-en.xml`
- CN: `https://moltcast-mm.vercel.app/rss-cn.xml`

**平台发布**:
- 小宇宙: https://www.xiaoyuzhoufm.com/podcast/69997f5a531cfc73bbb7413e
- Spotify: 通过 RSS 自动抓取

## 发布新集 Checklist

1. 准备文稿: `episodes/epXXX/transcript-{en,cn}.md`
2. 生成音频 (见 Pipelines)
3. 复制音频到 `site/episodes/epXXX/`
4. 更新 `site/index.html` — 添加新集到 episodes 列表
5. 更新 `site/rss-en.xml` + `site/rss-cn.xml` — 添加 `<item>`
6. 运行 `python3 site/generate_transcripts.py` — 生成文字稿页面
7. 部署: `cd site && vercel --yes --prod`
8. Git commit + push

## RSS 格式参考

```xml
<item>
  <title>第X集：标题</title>
  <description><![CDATA[<p>描述</p><p>🦞 龙虾冷知识：...</p>]]></description>
  <enclosure url="https://moltcast-mm.vercel.app/episodes/epXXX/epXXX-cn.mp3" length="FILE_SIZE_BYTES" type="audio/mpeg"/>
  <guid isPermaLink="false">moltcast-epXXX-cn</guid>
  <pubDate>Day, DD Mon YYYY HH:MM:SS GMT</pubDate>
  <itunes:duration>SECONDS</itunes:duration>
  <itunes:episode>N</itunes:episode>
  <itunes:season>1</itunes:season>
  <itunes:episodeType>full</itunes:episodeType>
  <itunes:title>标题</itunes:title>
  <itunes:summary>简短描述</itunes:summary>
</item>
```

**注意**: `length` 必须是准确的文件字节数（`stat -c%s file.mp3`），`duration` 用 `ffprobe` 获取。

## 凭证

| 服务 | 凭证位置 | 说明 |
|------|----------|------|
| ElevenLabs | `~/.env` ELEVENLABS_API_KEY | 英文 TTS |
| 火山引擎 (豆包) | `~/.env` VOLC_PODCAST_* | 中文播客模型 API |
| Vercel | `~/.vercel` | 部署 token |
| Gemini | `~/.env` GEMINI_API_KEY | 封面生成 |
| GitHub | `~/.gitconfig` | 代码推送 |

## 注意事项

1. **Segments 缓存**: `--skip-existing` 跳过已有分段，节省 API credits
2. **中文字数限制**: 豆包语音合成大模型单次 ≤1024 bytes UTF-8 (~300字)，脚本自动按句分割
3. **ElevenLabs v3**: 支持 audio tags `[laughs]` `[sighs]` `[short pause]` 等
4. **Crossfade**: 80ms triangular，失败时 fallback 到 simple concat
5. **播客大模型 vs 语音合成大模型**: 播客大模型会改写文本（更自然），语音合成大模型逐字朗读（更可控）
6. **Jules 仅用于法语集**: 非法语集 Coral 用 Charlie

## Style Guide / 风格指南

### Lobster-Centric Worldview / 以虾为中心的世界观
- 龙虾说话时，世界观以虾为中心
- ❌ 骂人 → ✅ 骂虾
- ❌ 因人而异 → ✅ 因虾而异
- ❌ 人类的角度 → ✅ 甲壳类的角度（当龙虾谈自己时）
- 龙虾讨论人类社会时可以用"人类"、"人们"（因为它们是在观察另一个物种）
- 龙虾知道自己是虾，完全接受，不防御，不自贬
- Self-awareness = 幽默核心

## 常见问题

### 豆包 403/404
- 检查 `VOLC_PODCAST_APP_ID` 和 `VOLC_PODCAST_ACCESS_TOKEN`
- 确认火山引擎账号已开通播客语音合成服务
- Resource ID 必须是 `volc.service_type.10050`

### 封面文字不对
Gemini 生成的中文文字经常不准确，可能需要多试几次或后期 PS。

### 小宇宙 RSS 不更新
小宇宙抓取 RSS 有延迟（几小时到一天），也可以手动上传。
