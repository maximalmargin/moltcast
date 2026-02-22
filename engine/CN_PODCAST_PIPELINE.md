# 中文播客音频生成 Pipeline

> 使用火山引擎「豆包·语音播客模型」生成双人对话播客音频。

## 概览

- **模型**: 豆包·语音播客模型（2025年5月发布）
- **能力**: 输入文本 → 自动生成双人对话音频（含节奏、语气、口语化处理）
- **协议**: WebSocket 二进制协议（非 REST API）
- **Endpoint**: `wss://openspeech.bytedance.com/api/v3/sami/podcasttts`
- **说话人**: 模型自动分配（男声 `大意先生` + 女声 `米在同学`，不可自定义）
- **输出**: MP3 或 WAV，24kHz

## 文件结构

```
engine/
├── protocols.py              # 火山引擎 WebSocket 二进制协议库（官方 SDK 提取）
├── generate_cn_podcast.py    # 播客生成脚本
└── CN_PODCAST_PIPELINE.md    # 本文档
```

## 环境准备

### 1. 依赖

```bash
pip install websockets
```

### 2. 凭证（~/.env）

```bash
VOLC_PODCAST_APP_ID=9453059849
VOLC_PODCAST_ACCESS_TOKEN=oHpSlib8Uk7-Qtc8Fbcgm4uKgeqnbhs1
# VOLC_PODCAST_SECRET_KEY 也在 ~/.env 但播客 API 不需要
```

- **AppID**: 火山引擎控制台 → 语音技术 → 应用管理
- **Access Token**: 同上
- **Resource ID**: `volc.service_type.10050`（播客语音合成，硬编码在脚本里）

### 3. 火山引擎账号

- 注册: console.volcengine.com（需中国手机号）
- 开通「豆包语音」服务 → 播客语音合成
- maximalmargin@gmail.com 已开通（2026-02-21 试用转正成功）

## 使用方法

### 基本用法

```bash
source ~/.env
cd ~/repos/moltcast/engine

# 从 transcript markdown 生成（自动提取对话部分）
python3 generate_cn_podcast.py \
  --transcript ../episodes/ep003/transcript-cn.md \
  --output ../episodes/ep003/ep003-cn.mp3

# 从纯文本文件生成（不做 markdown 解析）
python3 generate_cn_podcast.py \
  --transcript input.txt \
  --output output.mp3 \
  --raw-text
```

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--transcript` | 输入文件路径 | 必填 |
| `--output` | 输出音频路径 | 必填 |
| `--encoding` | 音频格式 mp3/wav | mp3 |
| `--raw-text` | 跳过 markdown 解析 | false |

### 输出

- `ep003-cn.mp3` — 最终音频（所有轮次拼接 + 片头片尾音乐）
- `ep003-cn_texts.json` — 模型实际生成的对话文本（可用于对照）

## 协议流程

```
Client                              Server
  |                                    |
  |--- StartConnection [event=1] ----->|
  |<-- ConnectionStarted [event=50] ---|
  |                                    |
  |--- StartSession [event=100] ------>|  (payload: JSON with input_text)
  |<-- SessionStarted [event=150] ----|
  |                                    |
  |--- FinishSession [event=102] ----->|  (signal: all input sent)
  |                                    |
  |<-- PodcastRoundStart [event=360] --|  (round_id, speaker, text)
  |<-- PodcastRoundResponse [361] ----|  (audio chunks, repeats)
  |<-- PodcastRoundEnd [event=362] ---|  (audio_duration)
  |    ... repeat for each round ...   |
  |                                    |
  |<-- PodcastEnd [event=363] --------|  (meta_info, input_metrics)
  |<-- SessionFinished [event=152] ---|
  |                                    |
  |--- FinishConnection [event=2] --->|
  |<-- ConnectionFinished [event=52] --|
```

### 特殊轮次
- `round_id = -1` → 片头音乐 (head_music)
- `round_id = 9999` → 片尾音乐 (tail_music)
- 其他 → 正常对话轮次

### 断点续传
如果中途断开，可以通过 `retry_info` 从上次完成的 round 继续：
```json
{
  "retry_info": {
    "retry_task_id": "<original_session_id>",
    "last_finished_round_id": <last_completed_round>
  }
}
```

## HTTP Headers

| Header | 说明 | 示例 |
|--------|------|------|
| X-Api-App-Id | 应用 ID | 9453059849 |
| X-Api-App-Key | 固定值 | aGjiRDfUWi |
| X-Api-Access-Key | Access Token | oHpSlib8Uk... |
| X-Api-Resource-Id | 资源 ID | volc.service_type.10050 |
| X-Api-Connect-Id | 连接 UUID | 随机生成 |

## 请求参数（StartSession payload）

```json
{
  "input_id": "unique_identifier",
  "input_text": "对话文本...",
  "action": 0,
  "use_head_music": true,
  "use_tail_music": true,
  "input_info": {
    "input_url": "",
    "return_audio_url": false,
    "only_nlp_text": false
  },
  "speaker_info": {"random_order": false},
  "audio_config": {
    "format": "mp3",
    "sample_rate": 24000,
    "speech_rate": 0
  }
}
```

### action 类型
- `0` — 标准播客生成（输入文本，模型自动改写为对话）
- `3` — 直接使用 nlp_texts（已分好的对话列表）
- `4` — 带 prompt 的播客生成

### 其他可选参数
- `prompt_text` — action=4 时的提示词
- `nlp_texts` — action=3 时的对话列表
- `only_nlp_text` — 只返回文本不生成音频

## 注意事项

1. **模型会改写文本**: 输入的对话文本会被模型重新组织为自然对话，不是逐字朗读
2. **不可指定声音**: 说话人由模型自动分配，目前固定为 `大意先生`（男）+ `米在同学`（女）
3. **文本长度限制**: 通过 `input_metrics.input_text_truncated` 判断是否被截断
4. **生成时间**: EP3（~3000字）约 3-4 分钟生成完
5. **费用**: 按输出音频 token 计费（UsageResponse 事件返回）

## 与普通 TTS 的区别

| | 普通 TTS (bigmodel) | 播客模型 (podcasttts) |
|---|---|---|
| Endpoint | `/api/v3/tts/bigmodel` | `/api/v3/sami/podcasttts` |
| 输入 | 单段文本 | 完整对话/文章 |
| 输出 | 单人朗读 | 双人对话 + 背景音乐 |
| 角色控制 | 手动指定 voice | 模型自动分配 |
| 适用场景 | 旁白、单人播报 | 播客、访谈节目 |

## 官方参考

- API 文档: https://www.volcengine.com/docs/6561/1668014
- SDK 包: `~/volcengine.speech.volc_speech_python_sdk_1.0.0.25.tar.gz`
- PDF 文档: `~/播客API-websocket-v3协议--豆包语音-火山引擎.pdf`
- protocols.py 源码: SDK 中 `volcengine_podcasts_demo` 解压
