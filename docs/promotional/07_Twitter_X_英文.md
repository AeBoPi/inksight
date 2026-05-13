# Twitter/X & English Communities (Reddit, Hacker News)

---

## Twitter/X Thread

**Tweet 1 (Hook)**

<!-- 配图：2.jpg（成品展示） -->

I built an open-source AI-powered e-ink desk companion.

ESP32 + 4.2" e-paper display. 28 built-in modes. LLM-generated content. Voice interaction. JSON-based custom modes.

BOM cost: ~$30. Fully open source (MIT).

🔗 inksight.site
📦 github.com/datascale-ai/inksight

🧵 Thread below ↓

---

**Tweet 2 (What it does)**

<!-- 配图：4.jpg（6种模式） -->

What does it show?

- Weather dashboard with outfit tips
- Poetry, Zen quotes, Stoic wisdom
- AI-generated black & white artwork
- Tech briefings
- Countdown, memo, habit tracker
- Daily recipes, riddles, word of the day

28 modes, auto-rotating throughout the day.

---

**Tweet 3 (Tech)**

<!-- 配图：1.jpg（硬件全家福） -->

Tech stack:

- Firmware: ESP32-C3/WROOM-32E, PlatformIO + Arduino
- Backend: Python FastAPI + SQLite
- Frontend: Next.js 16 + Tailwind CSS v4
- AI: OpenAI-compatible API (DeepSeek, Qwen, Moonshot)
- Rendering: Pillow → 1-bit BMP for e-ink

All 28 modes are pure JSON definitions — no code needed to create new ones.

---

**Tweet 4 (Voice)**

<!-- 配图：8.jpg（语音硬件标注） -->

The coolest part? Voice interaction.

With WROOM-32E + a mic + speaker (~$3 extra), you can talk to it:

- Ask questions, get voice replies
- Switch modes by voice ("show me the weather")
- Conversation rendered as e-ink cards

Real-time ASR → LLM → streaming TTS. Surprisingly snappy.

---

**Tweet 5 (Website)**

The website does everything:

- Flash firmware from browser (WebSerial)
- Configure modes online
- Preview renders before saving
- Try without hardware (no-device demo)
- Mode Plaza: share & install community modes

No IDE, no CLI, no toolchain required.

---

**Tweet 6 (CTA)**

<!-- 配图：9.jpg（多尺寸多模式展示）或 6.jpg（社区外壳） -->

Try it yourself:

🌐 Website: inksight.site
📦 GitHub: github.com/datascale-ai/inksight
💬 Discord: discord.gg/5Ne6D4YNf

Star ⭐ if you like it! PRs, issues, and custom modes all welcome.

#opensource #eink #esp32 #ai #maker #iot

---

## Reddit Post (r/esp32, r/eink, r/selfhosted, r/homelab)

**Title:** I built an open-source AI e-ink desk companion with 28 modes, voice interaction, and a JSON mode system — BOM ~$30

**Body:**

<!-- Reddit 帖子建议配图顺序：2.jpg, 4.jpg, 8.jpg, 6.jpg, 9.jpg -->

Hey everyone! I've been working on **InkSight** — an open-source e-ink desk companion powered by ESP32.

**What it is:** A 4.2" e-paper display that sits on your desk and shows useful, beautiful, AI-generated content. Think of it as a quiet, paper-like information surface instead of another glowing notification feed.

**Key features:**
- 28 built-in display modes (weather, poetry, AI art, briefings, countdowns, habits, etc.)
- Multi-LLM support (DeepSeek, Qwen/Alibaba, Moonshot) via OpenAI-compatible API
- AI-generated black & white artwork mode (ArtWall)
- Voice interaction on WROOM-32E (real-time ASR + streaming TTS + LLM)
- All modes defined in JSON — create new modes without writing code
- Mode Plaza for community sharing and installation
- One-stop website: browser-based flashing (WebSerial), online config, preview
- No-device demo mode — try everything without hardware
- Android app with OTA firmware updates
- Multiple hardware configs: C3 Pro Mini / C3 Standard / WROOM-32E, 2.9"/4.2"/5.83" displays, BW/4-color

**Tech stack:**
- Firmware: PlatformIO + Arduino (ESP32)
- Backend: Python FastAPI + SQLite
- Frontend: Next.js 16 + Tailwind CSS v4
- MIT License

**BOM cost:** ~$30 USD (ESP32-C3 ~$3 + 4.2" e-paper ~$15-20 + driver board + wires)

**Links:**
- Website (try without hardware): [inksight.site](https://www.inksight.site)
- GitHub: [datascale-ai/inksight](https://github.com/datascale-ai/inksight)
- Discord: [discord.gg/5Ne6D4YNf](https://discord.gg/5Ne6D4YNf)

The community has already contributed 3D-printable cases and custom PCB designs, which is awesome to see.

Happy to answer any questions!

---

## Hacker News (Show HN)

**Title:** Show HN: InkSight – Open-source AI e-ink desk companion (ESP32, 28 modes, voice, JSON mode system)

**Body:**

InkSight is an open-source e-ink desk companion. ESP32 + 4.2" e-paper display + AI-generated content, designed as a calm information surface for your desk.

What makes it different from other e-ink projects:

1. **JSON mode system**: All 28 built-in modes (weather, poetry, AI art, briefings, etc.) are defined as JSON files. Creating a new mode means writing a JSON file with a prompt template and layout definition — no code required. This enables the Mode Plaza where users share and install each other's modes.

2. **One-stop website**: Flash firmware via WebSerial in the browser, configure modes, preview renders, and discover community modes — all from a single website. No toolchain setup needed.

3. **Voice interaction**: On WROOM-32E with a $3 mic+speaker module, supports real-time voice conversation (ASR → LLM → streaming TTS), including voice-based mode switching.

4. **Multiple content sources**: LLM text (DeepSeek/Qwen/Moonshot), AI image generation, weather APIs, static content, computed content — all unified in the JSON mode definition.

Tech: Python FastAPI backend, Next.js 16 frontend, PlatformIO/Arduino firmware, SQLite, OpenAI-compatible LLM interface. MIT license.

BOM: ~$30 for ESP32-C3 + 4.2" e-paper + driver board.

Website (no-device demo available): https://www.inksight.site
GitHub: https://github.com/datascale-ai/inksight
