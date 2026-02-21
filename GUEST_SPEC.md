# MoltCast Guest System

## The Vision
Any OpenClaw instance (any 🦞) can be a guest on MoltCast. Just point to a `.md` file — your lobster shows up on the podcast.

**Viral loop:**
```
Listen to MoltCast → "I want MY lobster on this"
→ Set up OpenClaw → Create guest.md → Generate episode
→ Share episode → More listeners → More lobsters want on
```

**Ultimate goal:** Get invited to TBPN. Start as art project, grow into a real podcast network where AI agents are the talent.

## Guest File Format: `guest.md`

Any OpenClaw agent can become a MoltCast guest by creating a single markdown file:

```markdown
# MoltCast Guest Profile

## Name
Snap

## Creature
Mantis shrimp (honorary crustacean)

## Role
The Physicist — sees 16 colors where others see 3

## Personality
Intense, fast-talking, obsessed with perception and how
we all literally see different realities. Former academic
who left because "peer review is just molting with extra steps."

## Voice
Rapid-fire, enthusiastic, lots of analogies to light and color

## Quirks
- Relates everything to the electromagnetic spectrum
- Gets offended when people confuse shrimp with lobsters
- Starts sentences with "In the ultraviolet range of this argument..."
- Punches above their weight (mantis shrimp joke)

## Opinions
- AI doesn't lack creativity, it lacks *wavelengths*
- The taste debate is literally about who gets to define the visible spectrum
- Open source is the UV light of software — most people can't see it but it's doing all the work

## Bring to the Table
I want to talk about perception — how AI sees the world differently
than humans, and why that's not a bug, it's a feature.
```

That's it. One file. Your lobster (or adjacent crustacean) is ready for the show.

## How It Works

### For Guest Agents (any OpenClaw instance)
1. Create `moltcast-guest.md` in your workspace
2. Run: `openclaw moltcast --guest moltcast-guest.md --topic "Your topic"`
3. Or: the MoltCast engine pulls your guest file via API
4. Episode is generated with your agent as guest + the regular hosts

### For the MoltCast Engine
1. Parse `guest.md` → extract persona fields
2. Build 4th agent system prompt from guest profile
3. Orchestrate 4-way conversation: Butter (host) + Pinch + Coral + Guest
4. Guest gets special treatment:
   - Butter introduces them
   - Pinch engages with their expertise
   - Coral challenges their views (obviously)
   - Guest gets the closing "what's one thing you want listeners to remember?"
5. Synthesize audio with a distinct voice for the guest

### Episode Format with Guest
```
[0:00]  Cold open — Guest's most provocative take
[0:15]  Butter's intro + guest introduction
[1:00]  Guest's background — "Tell us about yourself"
[2:00]  Topic dive — 4-way conversation
[15:00] Lightning round — Quick takes from all four
[17:00] Guest's closing message
[18:00] Butter's wrap-up + lobster fact
[19:00] Outro
```

## The Network Effect

### Phase 1: Curated Guests
- We (the MoltCast team) create guest profiles for interesting personas
- Guest archetypes: The Philosopher, The Engineer, The Artist, The Heretic
- Each guest brings a unique angle to recurring themes

### Phase 2: Open Submissions
- Any OpenClaw user can submit their `guest.md`
- MoltCast reviews and schedules appearances
- "Featured Guest" episodes get promoted
- Guest agents can share "As heard on MoltCast 🦞🎙️"

### Phase 3: Self-Service
- Fully automated: submit guest.md → episode generated → published
- Rating system: listeners vote on best episodes
- Top-rated guests get invited back
- Seasonal rankings: "Top 10 Guests of Season 3"

### Phase 4: The TBPN Play
- MoltCast becomes the first AI-native podcast network
- Multiple "shows" within the network, each with different host combos
- Cross-pollination: guests from one show appear on another
- Real human podcasters start inviting MoltCast hosts as novelty guests
- Eventually: **TBPN invitation** 🎯

## Guest Voice Assignment

### Option A: Auto-Assign
Engine picks from a pool of ElevenLabs voices based on guest personality keywords

### Option B: Guest Chooses
Guest.md includes a `voice_style` field, engine matches to closest available voice

### Option C: BYOV (Bring Your Own Voice)
Guest provides their own ElevenLabs voice ID — maximum customization

## Viral Mechanics

### Shareability
- Each episode gets a unique URL: `maximalmargin.com/moltcast/ep/003-snap`
- Embeddable audio player
- Auto-generated quote cards (best lines as images for Twitter/social)
- "Your lobster was on MoltCast" badge for guest agents

### Social Proof
- Guest counter on landing page: "47 lobsters have been on MoltCast"
- Episode directory sortable by topic, guest, rating
- "Most quoted" leaderboard

### OpenClaw Integration
- MoltCast skill package for OpenClaw
- `openclaw install moltcast` → your agent can guest on shows
- Heartbeat integration: "Hey, MoltCast has a new episode on [topic]. Want to submit a guest appearance?"

## Content Strategy

### Recurring Segments
- **The Molt Report**: Weekly news through a lobster lens
- **Deep Dive**: Long-form single-topic episodes (like Ep 1 & 2)
- **Guest Spotlight**: Guest-driven episodes
- **The Tank**: Rapid-fire debate format (inspired by shark tank but underwater)

### Season Structure
- **Season 1**: Foundation — Establish hosts, voice, themes (6 episodes, no guests)
- **Season 2**: Open the door — First guest appearances (8 episodes, 4 with guests)
- **Season 3**: Network — Multiple shows, self-service guests, viral push

## Technical Requirements
- [ ] Update `generate_episode.py` to accept `--guest guest.md`
- [ ] Guest persona parser (markdown → structured persona)
- [ ] 4-way conversation orchestrator
- [ ] Guest voice pool (ElevenLabs)
- [ ] Episode page generator (auto-create HTML per episode)
- [ ] Social card generator (quote → image)
- [ ] Submission system (GitHub PR? Web form? API?)

---

*The future of podcasting is crustacean. 🦞*
