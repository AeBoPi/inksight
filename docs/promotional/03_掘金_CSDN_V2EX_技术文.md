# 从零开源一个 AI 墨水屏桌面伴侣：架构设计、模式系统与技术选型 | InkSight

> GitHub: [datascale-ai/inksight](https://github.com/datascale-ai/inksight) | 官网: [inksight.site](https://www.inksight.site) | MIT License

---

## TL;DR

InkSight（墨鱼AI墨水屏）是一个完全开源的智能桌面伴侣项目，由 ESP32 驱动 4.2 寸电子墨水屏，后端 FastAPI 生成 AI 内容并渲染为墨水屏位图，前端 Next.js 提供一站式的刷机、配置、预览和模式广场体验。支持 28 种内置模式、JSON 自定义模式、语音交互、多硬件适配，BOM 成本约 220 元。

本文从架构设计、技术选型、核心链路三个维度展开，适合对开源硬件、嵌入式 AI 和全栈开发感兴趣的开发者。

![硬件全家福：多尺寸屏幕、ESP32开发板、电池、驱动板](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/1.jpg)

---

## 1. 系统架构

InkSight 采用三层架构：

```
┌─────────────┐     HTTP/BMP      ┌──────────────┐     API Proxy      ┌─────────────┐
│   Firmware   │ ◄──────────────► │    Backend    │ ◄────────────────► │   WebApp    │
│  (ESP32)     │                  │  (FastAPI)    │                    │  (Next.js)  │
└─────────────┘                   └──────────────┘                    └─────────────┘
```

### Firmware（固件层）

- **平台**：PlatformIO + Arduino Framework
- **芯片**：ESP32-C3 / ESP32-WROOM-32E
- **职责**：WiFi 联网、定时请求后端渲染图像、驱动墨水屏、按键交互、深度休眠、NVS 状态持久化
- **配网**：Captive Portal 方式，设备创建热点 → 手机连接 → 输入 WiFi 信息
- **显示驱动**：GxEPD2 库 + 自定义 SPI 驱动层，支持多款屏幕芯片（SSD1683、JD79668、UC8179 等）
- **语音**（仅 WROOM-32E）：INMP441 麦克风 + MAX98357A 功放，I2S 接口

### Backend（后端层）

- **框架**：Python FastAPI，单入口 `api/index.py`
- **数据库**：双 SQLite（`inksight.db` 配置/状态 + `cache.db` 渲染缓存）
- **LLM**：OpenAI 兼容接口统一封装，支持 DeepSeek、阿里通义、Moonshot 等
- **图像**：Pillow 渲染 → 1-bit BMP（设备）/ PNG（预览）
- **缓存**：内存 + SQLite 双层，TTL = `refresh_interval × mode_count × 1.1`，批量预生成降低等待

### WebApp（前端层）

- **框架**：Next.js 16 (App Router) + Tailwind CSS v4
- **功能**：官网展示、WebSerial 刷机、设备配置、模式预览、模式广场、用户系统
- **特色**：无设备 Demo 模式，让未购买硬件的用户也能体验

---

## 2. 核心渲染链路

每次设备刷新或用户预览时的完整链路：

```
Device/Web Request
       │
       ▼
  api/index.py (/api/render 或 /api/preview)
       │
       ▼
  core/cache.py ── 命中？ ──► 直接返回缓存图像
       │ (未命中)
       ▼
  core/pipeline.py:generate_and_render()
       │
       ▼
  core/mode_registry.py ── 查找模式定义（JSON）
       │
       ├── content.type == "llm"       → LLM 文本生成
       ├── content.type == "llm_json"  → LLM 结构化输出
       ├── content.type == "static"    → 静态内容
       ├── content.type == "external_data" → 天气等外部数据
       ├── content.type == "image_gen" → AI 图像生成
       ├── content.type == "computed"  → 规则计算
       └── content.type == "composite" → 组合多源
       │
       ▼
  core/json_renderer.py ── 按 layout.body 渲染图像
       │
       ▼
  BMP (1-bit, 设备) 或 PNG (预览)
```

---

## 3. JSON 模式系统：不写代码的可扩展性

这是 InkSight 最有意思的设计之一。所有内置模式都是 JSON 文件定义的，放在 `backend/core/modes/builtin/`，用户自定义模式放在 `backend/core/modes/custom/`。

一个模式的最小定义：

```json
{
  "mode_id": "MY_QUOTE",
  "display_name": "每日一句",
  "cacheable": true,
  "content": {
    "type": "llm",
    "prompt_template": "请给我一句富有哲理的话，结合当前的{context}。",
    "output_format": "text",
    "fallback": { "text": "生活不止眼前的苟且。" }
  },
  "layout": {
    "body": [
      { "type": "centered_text", "field": "text", "font": "noto_serif_light", "font_size": 22 }
    ]
  }
}
```

JSON 渲染引擎（`json_renderer.py`）支持 16 种 Block 类型：

| Block | 用途 |
|-------|------|
| `centered_text` | 居中文本 + 自动缩放 |
| `text` | 左/中/右对齐 + 自动换行 |
| `two_column` | 双栏布局 |
| `list` | 列表渲染 |
| `section` / `group` | 分组容器 |
| `key_value` | 键值对 |
| `big_number` | 大字号数字 |
| `progress_bar` | 进度条 |
| `image` | 远程图片 |
| `conditional` | 条件渲染 |
| `separator` / `spacer` | 分隔与留白 |
| `icon_text` / `icon_list` | 图标+文本 |
| `vertical_stack` | 垂直堆叠 |

这套设计让"创建新模式"的门槛从"写 Python 代码"降到了"写一个 JSON 文件"，也让模式广场的分享成为可能。

![6种模式实拍效果：每日推荐、天气、AI简报、课程表、习惯打卡、日历](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/4.jpg)

---

## 4. 语音对话架构

在 WROOM-32E 上，墨鱼支持完整的语音交互链路：

```
用户说话 → INMP441 采集 PCM → WiFi 上传 → 后端 STT (百炼 ASR) 
    → LLM 生成回复 → TTS (CosyVoice) 流式合成 → WiFi 下发 → MAX98357A 播放
```

技术亮点：
- **流式双工**：ASR partial 结果稳定 180ms 后就开始预热 LLM，缩短感知延迟
- **分段 TTS**：LLM 流式输出按标点/长度分段，边生成边合成边播放
- **服务端 VAD**：后端可独立检测静音（800ms 阈值），无需等设备 commit
- **模式切换**：对话中说"切换到天气"，系统智能识别意图并切换

![语音对话硬件全貌：ESP32 + 麦克风 + 喇叭 + 功放 + 按键](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/8.jpg)

---

## 5. 技术选型考量

### 为什么选 FastAPI 而不是 Go/Rust？

内容生成的核心是 LLM 调用和图像渲染（Pillow），Python 生态在这两个领域有绝对优势。FastAPI 的异步能力足以应对墨水屏的低频请求（设备通常 15-60 分钟刷新一次）。

### 为什么用 SQLite 而不是 PostgreSQL/Redis？

InkSight 的典型部署场景是个人服务器或 Vercel Serverless。SQLite 零运维、单文件部署，对个人项目来说是最务实的选择。双库分离（配置 vs 缓存）让数据职责清晰。

### 为什么所有模式都用 JSON 定义？

早期版本用 Python 代码定义模式，但这意味着：
1. 创建新模式需要写代码
2. 模式分享需要分享代码（安全隐患）
3. 用户贡献门槛高

迁移到纯 JSON 后，模式广场的"创建-分享-安装"链路才真正跑通。

### 为什么做一站式网站而不是只开源代码？

开源硬件项目的最大痛点往往不是代码质量，而是上手门槛。把刷机、配置、预览全放进浏览器，才能让这个项目不仅仅是"给开发者玩的 Side Project"，而是一个"非技术用户也能完成整条体验的产品"。

---

## 6. 成本与硬件

| 部件 | 推荐 | 价格参考 |
|------|------|----------|
| ESP32-C3 开发板 | Pro Mini 或标准板 | ~15-25 元 |
| 4.2寸墨水屏 | 中景园/微雪 黑白屏 | ~100-130 元 |
| 驱动板 / 杜邦线 | 视方案而定 | ~10-30 元 |
| 锂电池（可选） | 505060-2000mAh | ~15 元 |
| 充电模块（可选） | TP5000 | ~5 元 |

总计约 **220 元**，低于市面上大多数商业化墨水屏产品。

![多尺寸硬件方案实拍：4.2寸+2.9寸屏幕搭配不同开发板](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/5.jpg)

---

## 7. 社区贡献

项目开源后，社区已经贡献了非常棒的衍生作品：

- **3D 打印外壳**：多款不同风格的桌面外壳，MakerWorld 可下载
- **定制 PCB**：集成化驱动板设计，立创开源硬件平台可查
- **华为手机壳版**：将墨水屏嵌入华为 Nova 14 手机壳的创意方案

![社区3D打印外壳：橙色桌面天气看板](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/6.jpg)

![社区3D打印外壳：粉色双机老黄历+日历](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/3.jpg)

![白色外壳相框模式：手写体+插画](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/images/community/case4.png)

![社区作品：红白复古外壳禅意模式](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/images/community/case2.png)

![社区作品：粉色外壳多款配色](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/images/community/case3.png)

![社区定制PCB：集成ESP32绿板](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/images/community/pcb1.png)

![社区定制PCB：墨鱼AI V1.1.1](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/images/community/pcb2.png)

![黑白屏与四色屏日历模式对比 + 一体化驱动板](https://cdn.jsdelivr.net/gh/AeBoPi/inksight@promotional/docs/promotional/7.jpg)

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/datascale-ai/inksight.git

# 后端
cd backend
pip install -r requirements.txt
python scripts/setup_fonts.py
cp .env.example .env  # 填入 API Key
python -m uvicorn api.index:app --host 0.0.0.0 --port 8080

# 前端
cd webapp
npm install
npm run dev
```

或者直接访问 [inksight.site](https://www.inksight.site) 使用在线服务。

---

## 写在最后

InkSight 不是一个"快速做完"的项目。从模式系统的多次重构，到一站式网站的打磨，到语音交互的端到端调通，每一步都是在思考一个问题：**怎么让一块小小的墨水屏，真正融入一个人的桌面生活？**

如果你对这个项目感兴趣，欢迎：
- ⭐ Star 项目：[github.com/datascale-ai/inksight](https://github.com/datascale-ai/inksight)
- 🐛 提 Issue / PR
- 💬 加入社区讨论（QQ群 1026120682 / Discord）
- 🎨 在模式广场分享你的创意

---

*InkSight — A calm e-ink desk companion.*
