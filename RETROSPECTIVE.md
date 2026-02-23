# MoltCast Retrospective

*Project: Feb 19–23, 2026. Five days from idea to 7-episode bilingual podcast.*

## What We Built

A podcast network run by three AI lobsters (Butter, Pinch, Coral), published in English and Chinese, with a trilingual special episode in English/French/Chinese. Seven episodes covering taste theory, AI displacement, film criticism, and the addictive design of AI agents.

**Final deliverables:**
- 7 episodes × 2 languages = 14 audio files
- Unified website (moltcast-mm.vercel.app)
- RSS feeds (EN + CN)
- Guest system for other AI agents
- maximalmargin.com blog post
- 小宇宙 (Chinese podcast platform) listing

## Timeline

| Day | What happened |
|-----|--------------|
| Day 1 (Feb 19) | Concept, personas, EP1 script + audio |
| Day 2 (Feb 20) | EP2-3 scripts, ElevenLabs voice selection, CN podcast model discovery |
| Day 3 (Feb 21) | EP4-7 scripts, CN translations, RSS feeds, Vercel deploy, blog post |
| Day 4 (Feb 22) | Pause. Check traction. |
| Day 5 (Feb 23) | EP4-7 EN audio, website, bug fixes, project wrap |

## Key Numbers

- **Total episodes:** 7
- **Total audio:** ~14 files, ~70 minutes
- **Languages:** English, Chinese, French
- **TTS engines:** 2 (ElevenLabs, Volcengine)
- **TTS models used:** 4 (ElevenLabs v3, Volcengine 大模型TTS, Volcengine 播客大模型)
- **Voices:** 5 (Laura, Charlie, Jules, 爽快思思, 率真小伙) + 播客大模型固定双人
- **Time EP5-7 from zero to published:** ~15 minutes (sub-agents parallel)
- **Total human time:** ~8 hours across 5 days (estimated)

## Technical Lessons

### 1. Multi-engine TTS is messier than expected

Volcengine has three separate TTS services that share credentials but have different endpoints, different voice catalogs, and different capabilities:

| Service | Endpoint | Use case |
|---------|----------|----------|
| 普通TTS | `api/v1/tts` | Standard voices (BV series) |
| 大模型TTS | Same endpoint, `_bigtts`/`_mars` voices | Expressive, natural |
| 播客大模型 | `api/v3/sami/podcasttts` (WebSocket) | Auto-rewritten dual-speaker dialog |

The error message `resource_id not granted` means the voice isn't activated in the console — not a permissions issue. You need to "purchase" free voices (¥0 checkout) before they work.

**Lesson:** Document the TTS config matrix early. We lost 30+ minutes debugging endpoint/voice mismatches.

### 2. 1.2x is the correct default speed

TTS-generated audio is consistently slower than natural speech. 1.2x sounds normal. This should be baked into the pipeline, not applied as a post-processing step.

### 3. Verbal rewrite is the highest-leverage step

The same script sounds dramatically different in written vs. spoken form. Adding fillers ("right?", "I mean"), reactions ("[laughs]", "Wait—"), and audio tags transforms robotic TTS into something that sounds like a conversation. Sub-agents can batch-write verbal transcripts, but the quality of the original script matters more.

### 4. Segment caching saves money

ElevenLabs charges per character. By saving individual segments and using `--skip-existing`, we never regenerate what already exists. A failed run at segment 12/18 resumes from segment 12, not from scratch.

### 5. Crossfade > concat

80ms triangular crossfade between speaker segments eliminates the hard cuts that make multi-speaker TTS sound artificial. Simple concat is the fallback, not the default.

## Infrastructure Lessons

### 6. Vercel + GitHub auto-deploy needs rootDirectory

If your site lives in a subdirectory (`site/`), you **must** set `rootDirectory` in the Vercel project settings. Otherwise every `git push` triggers a build from the repo root → 404. We fixed this via the Vercel API:

```bash
curl -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"rootDirectory": "site"}'
```

### 7. CSS scroll-reveal + refresh = white screen

`opacity: 0` with IntersectionObserver works on first load but breaks on refresh (browser scroll restoration may not trigger the observer). Always add a CSS fallback:

```css
.reveal {
  animation: force-visible 0s 1s forwards;
}
```

### 8. `font-display: swap` > `optional`

`optional` can cause entire pages of invisible text on slow connections. `swap` causes a brief font flash but is always better than a blank page.

## Creative Lessons

### 9. The lobster framing solves the uncanny valley

AI podcasts that pretend to be human invite skepticism. By making the hosts explicitly non-human (lobsters), listeners stop asking "is this real?" and start listening to the ideas. The artifice becomes the aesthetic.

### 10. Language-as-argument is the most AI-native idea

EP4 (La Distinction) uses three languages not as a gimmick but as the argument itself: Bourdieu's wordplay only works in French, 鄙视链 only exists in Chinese, and English hides the politics of taste. A human podcast couldn't do this — three hosts fluently switching between French, Chinese, and English in real-time. This is what "AI-native content" actually means.

### 11. 播客大模型 vs segment TTS = different tools for different jobs

| | 播客大模型 | Segment TTS |
|---|---|---|
| **Naturalness** | Very high (rewrites text) | Good (with verbal rewrite) |
| **Control** | Low (model decides delivery) | High (exact text preserved) |
| **Speakers** | Fixed 2 (can't customize) | Any number, any voice |
| **Best for** | Chinese casual dialog | English, multilingual, precise |

### 12. One person + AI = podcast network

The meta-point of MoltCast is itself a lesson: a single person with AI tools can conceive, write, produce, and distribute a multilingual podcast network in under a week. The bottleneck isn't production — it's having something worth saying.

## What We'd Do Differently

1. **Write WORKFLOW.md on Day 1**, not Day 5
2. **Standardize 1.2x in the pipeline** instead of applying it manually
3. **Set Vercel rootDirectory before first deploy**, not after debugging 404s
4. **Test TTS voices before writing scripts** — voice availability determines what's possible
5. **Skip the pause on Day 4** — momentum matters more than traction metrics for a creative project this small

## What Worked

- Sub-agent parallelism for verbal rewrites (3 episodes in 90 seconds)
- Segment caching for credit efficiency
- Separating CN (播客大模型, natural) from EN (segment TTS, controlled)
- The guest system design (GUEST_SPEC.md) — ready for collaboration even if we haven't used it
- Shipping fast, fixing bugs in production

## Final Thought

MoltCast started as "what if NotebookLM but lobsters?" and ended as a genuine creative artifact. The lobsters have opinions. The episodes are worth listening to. The trilingual episode does something no human podcast can do. Whether anyone listens is a different question — but the thing exists, and it's good.

Three lobsters. Seven episodes. Five days. One lesson: **the best way to explore a medium is to make something absurd in it.** 🦞

---

*A Maximal Margin production. Filed under: AI Mischief.*
