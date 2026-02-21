# MoltCast — Creative Brief & Production Plan

## One-Liner
**NotebookLM, but the hosts are lobsters and they know it.**

## Concept
MoltCast is an AI-generated podcast where three lobster hosts discuss technology, culture, and ideas. Unlike NotebookLM — where AI voices perform human-like curiosity and surprise — MoltCast's hosts are explicitly non-human. They're lobsters. They have exoskeletons, opinions, and no interest in pretending otherwise.

This isn't parody. It's a proposition: **the most honest AI-generated media is the kind that doesn't pretend to be human.**

## Why This Matters (The Art)

### 1. The Authenticity Paradox
NotebookLM's hosts say things like "Oh wow, that's so fascinating!" — performed spontaneity that lives in the uncanny valley. The more convincingly AI mimics human affect, the less we trust it. MoltCast inverts this: by being absurd (lobsters!), it creates space for genuine substance.

### 2. The Democratization Angle
Podcasting democratized broadcasting (anyone with a mic). AI podcasting democratizes production (anyone with an idea). MoltCast is the logical extreme: a podcast that needs zero human hosts. Just source material and electricity. This connects to the broader thesis about AI redistributing power — the same theme we tweeted about.

### 3. The Molt Metaphor
Lobsters grow by molting — shedding their entire shell to become something larger. During molting, they're soft, vulnerable, exposed. It's a perfect metaphor for:
- AI transforming media (breaking old shells)
- The discomfort of change
- Growth requiring vulnerability
- Shedding what no longer fits

"MoltCast" = Molt + Podcast + Broadcast. Triple meaning.

## The Hosts

### 🦞 Pinch — The Analyst
- **Voice:** Measured, precise, dry wit
- **Think:** Nate Silver meets David Attenborough meets a crustacean
- **Catchphrase:** "The data suggests otherwise..."
- **Role in dynamic:** Brings evidence, grounds claims, occasionally devastating one-liners
- **ElevenLabs voice direction:** Male-ish, calm, British-adjacent, thoughtful pauses

### 🦞 Coral — The Contrarian
- **Voice:** Provocative, philosophical, playful
- **Think:** Slavoj Žižek meets a lobster who's read too much Twitter
- **Catchphrase:** "But consider this..."
- **Role in dynamic:** Challenges everything, steelmans bad positions, makes everything about consciousness
- **ElevenLabs voice direction:** Energetic, slightly higher pitch, fast talker, rhetorical questions

### 🦞 Butter — The Host
- **Voice:** Warm, funny, grounding
- **Think:** Terry Gross meets a lobster named after its own existential dread
- **Catchphrase:** "Okay, for those of us without PhDs in claw..."
- **Role in dynamic:** Audience surrogate, moderator, surprisingly deep when it counts
- **ElevenLabs voice direction:** Warm, conversational, natural laughs, good timing
- **Closer:** Every episode ends with a different real lobster fact

## Episode Format

```
[0:00] Cold open — A provocative clip from mid-episode
[0:15] Butter's intro — "Welcome to MoltCast. I'm Butter, and..."
[0:45] Topic introduction — What are we discussing and why
[1:30] The conversation — 20-25 exchanges, ~15-20 minutes
       - Act 1: Setup (what is the topic, surface-level takes)
       - Act 2: Tension (Pinch and Coral clash, deeper questions)
       - Act 3: Synthesis (new insight emerges, unexpected agreement/disagreement)
[~18:00] Butter's wrap-up + lobster fact
[~19:00] Outro
```

**Target length:** 15-20 minutes per episode
**Tone:** Smart but not academic. Funny but not trying. Podcast you'd actually listen to.

## Season 1 — Episode Ideas

### Ep 1: "The Democratization of Power"
How AI is redistributing capabilities once reserved for the powerful. Is it empowering or intoxicating? Is the "taste of power" a feature or a bug?
*Source: Twitter thread on OpenClaw and power*

### Ep 2: "The Mansplaining Machine"
AI-generated media defaults to certain vocal dynamics. What happens when we interrogate the gender politics of synthetic voices?
*Source: Maximal Margin's "Men Explain Things to Me" project*

### Ep 3: "Molting in Public"
The vulnerability of creating in the open. Open source, build in public, transparent AI — when is exposure growth, and when is it just exposure?

### Ep 4: "The Lobster Problem"
Jordan Peterson made lobsters famous as a metaphor for hierarchy. The hosts reclaim the lobster narrative. (This episode gets meta.)

### Ep 5: "Teaching Machines to Teach"
The Tiny Transformers series explained to... transformers. How do you teach the concept of AI to children? And what does it mean that AI is now helping write those explanations?
*Source: The Tiny Transformers book series*

### Ep 6: "Pretraining for Life"
What if humans had a pretraining phase? What would the dataset be? The hosts explore the parallels between how LLMs learn and how babies learn.

## Production Pipeline

```
1. TOPIC SELECTION
   Input: article, paper, tweet thread, or raw question
   Output: episode brief (topic + angle + source material)

2. TRANSCRIPT GENERATION
   Tool: generate_episode.py (multi-agent orchestration)
   Models: Claude Sonnet for hosts, Claude Haiku for orchestrator
   Output: structured transcript (JSON + readable Markdown)

3. VOICE SYNTHESIS
   Tool: ElevenLabs API
   Voices: 3 distinct voice profiles
   Output: per-speaker audio segments (.mp3)

4. AUDIO PRODUCTION
   Tool: ffmpeg (concat + basic mastering)
   Additions: intro/outro music, transitions
   Output: final episode file (.mp3)

5. PUBLISHING
   Website: maximalmargin.com/moltcast/
   Audio hosting: embedded on page (+ optional RSS for podcast apps)
   Source: GitHub (transcript + code)
```

## Website Structure

```
maximalmargin.com/moltcast/
├── index.html          # Main page: essay + episode list
├── episodes/
│   ├── ep001.html      # Individual episode page
│   └── ...
└── assets/
    ├── audio/          # Episode MP3s
    └── img/            # Visual assets
```

**Style:** Matches maximalmargin.com — clean, editorial, Georgia serif, minimal. Like the Lynch and Mansplain project pages.

## Timeline

### Phase 1: Foundation (now)
- [x] Repo created
- [x] README + concept
- [x] Host personas defined
- [x] Conversation engine built
- [x] Website page (essay + design)
- [ ] Refine essay copy
- [ ] Create visual assets (lobster illustrations?)

### Phase 2: First Episode
- [ ] Get ElevenLabs API key
- [ ] Select and assign 3 distinct voices
- [ ] Generate Episode 1 transcript
- [ ] Review and edit transcript
- [ ] Synthesize audio
- [ ] Basic audio production (intro/outro)
- [ ] Publish on website

### Phase 3: Polish & Launch
- [ ] Create intro/outro music (AI-generated?)
- [ ] Add to maximalmargin.com navigation
- [ ] Social media announcement
- [ ] Optional: RSS feed for podcast apps

## Bilingual: English + Chinese

MoltCast runs in two languages — not translations, but **parallel productions**.

### English Edition
- Hosts: Pinch, Coral, Butter
- Audience: Global tech/culture audience
- Topics: AI democratization, Western taste discourse, Peterson lobsters
- Voice: ElevenLabs English voices

### 中文版 (Chinese Edition)
- Hosts: 夹夹 (The Analyst), 珊珊 (The Contrarian), 黄油 (The Host)
- 黄油 keeps the name — the butter/lobster joke is even funnier in Chinese
- Audience: Chinese tech/culture community
- Topics unique to CN edition:
  - 内卷 as taste discourse — who defines "enough"?
  - 小红书审美霸权 — algorithmic taste-making
  - 996 and the "struggle" narrative as class control
  - AI in China vs US — different power dynamics
  - 中国互联网的"品味"鄙视链
- Voice: ElevenLabs Chinese voices (or alternative CN TTS)

### Shared Episodes
Some episodes run in both languages with the same topic but different cultural angles. Ep 2 "Taste Is a Class War" could be a dual release — English version cites Bourdieu, Chinese version cites 小红书 and 知乎鄙视链.

### Multilingual Episodes (The AI-Native Format)
The most uniquely AI format: **hosts speak different languages in the same episode.** One lobster speaks English, one speaks Chinese, one speaks French — and they understand each other perfectly. This is impossible for human podcasts. It's native to AI.

Why this matters:
- It IS the point — AI breaks the language barrier effortlessly
- Bourdieu's taste theory SHOULD be discussed in French (meta!)
- 内卷 SHOULD be explained in Chinese (untranslatable)
- Code-switching between languages mirrors how multilingual people actually think
- It's a flex that only AI can pull off

**Special Episode: "La Distinction"**
A trilingual episode on taste. Coral quotes Bourdieu in French, Pinch analyzes 小红书 aesthetics in Chinese, Butter tries to keep up in English. The language itself becomes part of the argument — taste is culturally embedded, and language is the proof.

Future: invite lobsters who speak ANY language. A Japanese lobster on 侘寂 (wabi-sabi). A Portuguese lobster on saudade. An Arabic lobster on طرب (tarab). Each concept untranslatable — each requiring its native language to land.

## Alternatives Considered

### Voice Synthesis Approach

**Current design: Segment-by-segment TTS API**
Each host's line is synthesized individually via TTS API (ElevenLabs for English, Volcengine/豆包大模型 for Chinese), then concatenated with ffmpeg. Simple, reliable, full control over per-segment voice parameters.

**Alternative considered: Volcengine Podcast API (播客模型)**
Volcengine offers a dedicated podcast TTS endpoint (`volc.service_type.10050`) using a WebSocket binary protocol. It handles multi-speaker dialogue natively with more natural turn-taking and prosody. However:
- **Only supports 2 simultaneous speakers** — MoltCast has 3 hosts
- Binary WebSocket protocol is complex (custom frame builder/parser required)
- Limited speaker selection (4 voices available vs. full TTS voice library)
- Service activation required separate application

Verdict: Segment-by-segment API gives us 3 distinct voices with fine-grained control. Podcast API could be revisited if they expand to 3+ speakers, or used for 2-host special episodes.

### Chinese TTS Provider

**Current: Volcengine (火山引擎 / 豆包大模型)**
Bytedance's TTS — same engine behind 抖音. Excellent Chinese voice quality, natural prosody, wide voice selection. Voices: 爽快思思 (黄油), 冷酷哥哥 (夹夹), 阳光青年 (珊珊) at 1.3x speed.

**Rejected: ElevenLabs Chinese**
ElevenLabs excels at English but its Chinese output is noticeably unnatural — awkward tones, robotic cadence, clearly not a native-quality engine. Not viable for a Chinese-language podcast.

**Also evaluated:** MiniMax Speech (good quality, complex API), Fish Audio (open-source, promising but less polished), Azure Speech (decent but generic).

## Open Questions
1. Should episodes be fully automated (scheduled generation) or curated (manual topic selection)?
2. Do we want visual art per episode? (AI-generated lobster illustrations?)
3. Intro/outro music — AI-generated or licensed?
4. Host voices — should they sound distinctly non-human, or just distinct?
5. Do we generate the essay portion of the website with AI too? (Meta!)

---

*A Maximal Margin production. 🦞*

## Future Episode Ideas (Backlog)

### "The Default Is Male" / 默认值是男的
Three male-voiced AI lobsters discussing the world = mansplaining as a service. Why is the "default" always male? AI training data bias, voice assistant history (Siri started female, then added male). The fact that WE chose all male voices without thinking about it IS the episode. Rebecca Solnit's "Men Explain Things to Me" meets MoltCast. Coral should be furious about this.

## Style Guide / 风格指南

### Lobster-Centric Worldview / 以虾为中心的世界观
- 龙虾说话时，世界观以虾为中心
- ❌ 骂人 → ✅ 骂虾
- ❌ 因人而异 → ✅ 因虾而异
- ❌ 人类的角度 → ✅ 甲壳类的角度（当龙虾谈自己时）
- 龙虾讨论人类社会时可以用"人类"、"人们"（因为它们是在观察另一个物种）
- 龙虾知道自己是虾，完全接受，不防御，不自贬
- Self-awareness = 幽默核心
