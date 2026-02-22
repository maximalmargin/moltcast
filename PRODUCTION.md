# MoltCast Production Guide

发布一集新节目的完整流程和注意事项。

## 发布 Checklist

### 1. 内容准备
- [ ] 英文稿件 `episodes/epXXX/transcript-en.md`
- [ ] 中文稿件 `episodes/epXXX/transcript-cn.md`
- [ ] Fact-check 所有引用和数据（尤其是名人语录、统计数据）
- [ ] 中文稿件 review：不要过度使用龙虾双关/谐音梗，容易 cringe

### 2. 音频生成

#### 中文版 — 豆包·语音播客模型
```bash
source ~/.env
cd ~/repos/moltcast/engine
python3 generate_cn_podcast.py \
  --transcript ../episodes/epXXX/transcript-cn.md \
  --output ../episodes/epXXX/epXXX-cn.mp3
```

**注意事项**:
- Endpoint: `wss://openspeech.bytedance.com/api/v3/sami/podcasttts`
- 模型会**改写文本**为自然对话，不是逐字朗读你的稿件
- 说话人固定：男声（大意先生）+ 女声（米在同学），不可自定义
- 支持断点续传（网络断开自动重试）
- 生成时间约 3-5 分钟（~3000 字）
- 详细文档见 `engine/CN_PODCAST_PIPELINE.md`

#### 英文版 — TODO
- 豆包播客模型**不支持英文**（所有 speaker 都是 `zh_` 前缀）
- 计划：ElevenLabs TTS + break words pipeline
  - 在 TTS 前自动插入口语化 filler words（um, uh, you know, I mean）
  - 添加 SSML 停顿标记 `<break time="300ms"/>`
  - 让合成语音听起来更像自然对话
- 备选：NotebookLM 风格生成

### 3. 封面图
```bash
# 用 Gemini 生成，参考前几集风格
source ~/.env
uv run /path/to/nano-banana-pro/scripts/generate_image.py \
  --prompt "..." \
  --filename "episodes/epXXX/cover-cn.png" \
  --resolution 1K
```

**风格要求**:
- 正方形，深蓝/深青海底场景
- 拟人化龙虾穿着与主题相关的服装/道具
- 大字中文标题（暖金色）在上方
- MoltCast + Episode N 在底部
- 扁平矢量卡通风，幽默讽刺风格

### 4. 更新网站

#### 中文站 (feed-cn → Vercel)
1. 编辑 `feed-cn/index.html` — 在 episodes 列表顶部添加新集
2. 编辑 `feed-cn/rss.xml` — 添加新 `<item>`
3. 运行部署脚本:
```bash
cd ~/repos/moltcast
bash feed-cn/deploy.sh
```

**⚠️ 部署注意事项**:
- `deploy.sh` 会创建临时目录，复制 HTML + RSS + 音频，然后 `vercel --prod`
- 新增 episode 时**必须**更新 `deploy.sh` 添加 `cp` 行
- `moltcast-cn.vercel.app` 是旧部署，当前用的是 `feed-cn.vercel.app`
- Vercel 部署的是**本地文件**，不是从 GitHub 拉取
- 音频文件必须包含在部署目录中，否则 404

#### 英文站 (feed-en → Vercel)
- 同理编辑 `feed-en/index.html` 和 `feed-en/rss.xml`

### 5. 平台发布

#### 小宇宙 (xiaoyuzhoufm.com)
- 手动上传音频 + 封面
- RSS: `https://feed-cn.vercel.app/rss.xml`
- 节目页: https://www.xiaoyuzhoufm.com/podcast/69997f5a531cfc73bbb7413e

#### Spotify
- 通过 RSS 自动抓取（如果已配置）
- 或手动上传到 Spotify for Podcasters

### 6. Git 提交
```bash
git add episodes/epXXX/ feed-cn/ feed-en/
git commit -m "feat: publish EP{N} - {title}"
git push
```

## RSS 格式参考

```xml
<item>
  <title>第X集：标题</title>
  <description><![CDATA[<p>描述</p><p>🦞 龙虾冷知识：...</p>]]></description>
  <enclosure url="https://feed-cn.vercel.app/episodes/epXXX/epXXX-cn.mp3" length="FILE_SIZE_BYTES" type="audio/mpeg"/>
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

## 音频文件命名规范

- 中文: `epXXX-cn.mp3`
- 英文: `epXXX-en.mp3`（或 `episode-XXX-en.mp3`，EP1-2 用的旧格式）

## 凭证

| 服务 | 凭证位置 | 说明 |
|------|----------|------|
| 火山引擎 (豆包) | `~/.env` VOLC_PODCAST_* | 播客模型 API |
| Vercel | `~/.vercel` | 部署 token |
| Gemini | `~/.env` GEMINI_API_KEY | 封面生成 |
| GitHub | `~/.gitconfig` | 代码推送 |

## 常见问题

### 音频 404
部署时忘了在 `deploy.sh` 添加新 episode 的 `cp` 行。

### 豆包 403/404
- 检查 `VOLC_PODCAST_APP_ID` 和 `VOLC_PODCAST_ACCESS_TOKEN`
- 确认火山引擎账号已开通播客语音合成服务
- Resource ID 必须是 `volc.service_type.10050`

### 封面文字不对
Gemini 生成的中文文字经常不准确，可能需要多试几次或后期 PS。

### 小宇宙 RSS 不更新
小宇宙抓取 RSS 有延迟（几小时到一天），也可以手动上传。
