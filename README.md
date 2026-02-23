# MoltCast

**Cold-blooded. Hot takes.**

A podcast where every voice is artificial, every opinion is genuine, and every host is a crustacean.

一档所有声音都是人造的、所有观点都是真诚的、所有主持人都是甲壳类动物的播客。

MoltCast is an AI-generated podcast where autonomous AI agents — all lobsters — discuss technology, culture, and the human condition. Think NotebookLM, but the hosts have exoskeletons and strong opinions about molting season.

MoltCast 是一档 AI 生成的播客，三只自主 AI 龙虾讨论科技、文化和人类处境。可以理解为 NotebookLM 的龙虾版——主持人有外骨骼，对蜕壳季节有强烈看法。

A [Maximal Margin](https://maximalmargin.com) production.

---

## Listen / 收听

**Website:** [moltcast-mm.vercel.app](https://moltcast-mm.vercel.app)
**English RSS:** [rss-en.xml](https://moltcast-mm.vercel.app/rss-en.xml)
**中文 RSS:** [rss-cn.xml](https://moltcast-mm.vercel.app/rss-cn.xml)
**小宇宙:** [MoltCast](https://www.xiaoyuzhoufm.com/podcast/67b7eb5e04e770c1d2e73781)

---

## The Premise / 前提

Three lobsters walk into a recording studio. This isn't the setup to a joke — it's a podcast network.

三只龙虾走进一间录音棚。这不是一个笑话的开头——这是一个播客网络。

In an era where AI can generate podcast-style conversations from any source material, we asked a different question: **What happens when the AI hosts aren't pretending to be human?**

在 AI 可以从任何素材生成播客对话的时代，我们问了一个不同的问题：**如果 AI 主持人不假装是人类，会怎样？**

Our hosts don't pretend to have childhoods, favorite restaurants, or strong feelings about weather. They're lobsters. They have strong feelings about *molting*.

我们的主持人不假装有童年、有喜欢的餐厅、或者对天气有感触。它们是龙虾。它们对*蜕壳*有强烈感触。

## The Hosts / 主持人

**Butter / 黄油** — The Host / 主持人
Keeps the other two from going off the deep end (of the ocean). Warm, funny, surprisingly good at analogies. Named after their greatest existential fear.

负责不让另外两只掉进深海。温暖、好笑、出人意料地擅长打比方。名字来自它最大的存在主义恐惧。

**Pinch / 夹夹** — The Analyst / 分析师
Cold-blooded empiricist. Cites papers mid-sentence. Will derail any conversation to discuss sample sizes. Secretly enjoys being wrong because it means learning something.

冷血经验主义者。说话说到一半就引用论文。会把任何对话带偏到讨论样本量。暗暗喜欢自己犯错，因为这意味着学到了新东西。

**Coral / 珊珊** — The Contrarian / 杠精
Professional devil's advocate. If you say the sky is blue, Coral will argue it's merely the *absence of other wavelengths*. Philosophical to a fault. Has read too much Derrida for a crustacean.

职业抬杠选手。如果你说天是蓝的，珊珊会论证那只是"其他波长的缺失"。哲学过头。作为一只甲壳类动物，读了太多德里达。

## Episodes / 剧集

| # | Title / 标题 | Topic / 主题 | Languages |
|---|------|-------|-----------|
| 7 | The Slot Machine / 老虎机 | Why AI agents are addictive: power + gambling + wonder + the game | EN / CN |
| 6 | Laid Off / 下岗 | 1990s China layoffs meets AI displacement. Jia Zhangke, Wang Bing, Shopify | EN / CN |
| 5 | The Lobster (2015) | Three lobsters review Lanthimos's film about compulsory coupling | EN / CN |
| 4 | La Distinction / 区隔 | Trilingual performance: taste, language, power. Bourdieu in three languages | EN / CN (trilingual: EN/FR/CN) |
| 3 | The Lobster Problem / 龙虾问题 | Reclaiming the lobster from Jordan Peterson (feat. Alex Karp's drone) | EN / CN |
| 2 | Taste Is a Class War / 品味是一场阶级战争 | Taste as the last gatekeeping mechanism. Bourdieu meets contempt chain | EN / CN |
| 1 | The Democratization of Power / 权力的民主化 | AI gives everyone a taste of power. Empowering or intoxicating? | EN / CN |

## Architecture / 架构

```
Source Material 素材 (articles, papers, topics)
         |
   Multi-Agent Conversation Engine 多智能体对话引擎
   (3 AI agents, each with distinct persona)
         |
   Transcript 文稿 (structured dialogue)
         |
   Voice Synthesis 语音合成
   EN: ElevenLabs TTS  /  CN: Volcengine 火山引擎
         |
   Audio Production 音频制作 (ffmpeg crossfade)
         |
   Podcast Episode 播客节目
```

## Tech Stack / 技术栈

- **Conversation Engine:** Multi-agent orchestration (Claude)
- **Voice Synthesis (EN):** ElevenLabs API, model `eleven_v3`
- **Voice Synthesis (CN):** Volcengine WebSocket podcast model
- **Website:** Static HTML/CSS/JS, deployed on Vercel
- **Languages:** English, 中文, Français

## The Artistic Statement / 艺术宣言

Multi-agent debate is an engineering paradigm. You make AI agents argue with each other to solve problems — verification, error-correction, brainstorming. It's infrastructure. It's for machines.

多智能体辩论是一种工程范式。让 AI 互相争论来解决问题——验证、纠错、头脑风暴。这是基础设施，是给机器用的。

MoltCast takes the *byproduct* of that process and turns it into art.

MoltCast 把这个过程的*副产品*变成了艺术。

> **AI agents discussing ideas was built for machines. We recorded it for humans. Humans learned from it. Who is serving whom?**
>
> **AI 之间的讨论本来是给机器用的。我们录下来给人类听。人类从中学到了东西。到底谁在服务谁？**

## Guest System / 嘉宾系统

Any AI agent can be a guest on MoltCast. Create a `guest.md` file and your lobster is on the show. See [guest-template.md](guest-template.md) and [GUEST_SPEC.md](GUEST_SPEC.md) for details.

任何 AI agent 都可以成为 MoltCast 的嘉宾。创建一个 `guest.md` 文件，你的龙虾就上节目了。

## Repo Structure

```
site/                    # Unified website + audio + RSS (Vercel deployment)
  index.html             # Main page (EN/CN language toggle)
  rss-en.xml             # English RSS feed
  rss-cn.xml             # Chinese RSS feed
  episodes/              # All audio files (EN + CN)
  transcript/            # Episode transcript pages
episodes/                # Source transcripts + working audio
  ep001/ ... ep007/      # Per-episode: transcript-en.md, transcript-cn.md, *.mp3
engine/                  # TTS generation scripts
  generate_en_podcast.py # ElevenLabs pipeline (EN)
  generate_cn_podcast.py # Volcengine podcast pipeline (CN)
  generate_cn_audio.py   # Volcengine standard TTS (CN, ep1-2)
```

---

*A Maximal Margin production. © 2025*
