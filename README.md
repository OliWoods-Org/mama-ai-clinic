<p align="center">
  <img src="docs/images/mama-ai-clinic-banner.svg" alt="MAMA AI Clinic" width="800">
</p>

<h3 align="center">
  $170. Fully Offline. Solar-Powered. For the World's Most Underserved Clinics.
</h3>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://github.com/OliWoods-Org/mama-ai-clinic/actions"><img src="https://img.shields.io/github/actions/workflow/status/OliWoods-Org/mama-ai-clinic/ci.yml?label=safety%20eval" alt="CI"></a>
  <img src="https://img.shields.io/badge/runs_on-Raspberry_Pi_5-c51a4a?logo=raspberrypi" alt="Raspberry Pi">
  <img src="https://img.shields.io/badge/model-Gemma_4_E2B-4285F4?logo=google" alt="Gemma">
  <img src="https://img.shields.io/badge/internet-not_required-green" alt="Offline">
  <img src="https://img.shields.io/badge/cost-$170_per_site-orange" alt="Cost">
  <br>
  <a href="https://mama.oliwoods.ai"><img src="https://img.shields.io/badge/Built_with-MAMA-8b5cf6?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMCIgY3k9IjEwIiByPSI4IiBmaWxsPSIjOGI1Y2Y2Ii8+PC9zdmc+" alt="Built with MAMA"></a>
  <a href="https://cofounder.software"><img src="https://img.shields.io/badge/Powered_by-CoFounder-06b6d4?style=flat" alt="Powered by CoFounder"></a>
  <a href="https://mama.oliwoods.ai/foundation"><img src="https://img.shields.io/badge/OliWoods-Foundation-10b981?style=flat" alt="OliWoods Foundation"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#deploy-to-raspberry-pi">Deploy to Pi</a> &bull;
  <a href="#for-ngos">For NGOs</a> &bull;
  <a href="#safety-design">Safety</a> &bull;
  <a href="CONTRIBUTING.md">Contribute</a>
</p>

---

> **We are at the Raspberry Pi moment for humanitarian AI.** Gemma 4 E2B on a $35 Raspberry Pi 5 is frontier AI running offline in a remote village clinic. The window to define what responsible humanitarian AI on edge hardware looks like is 6-12 months wide. This is the reference design.

## The Problem

**862 million people** live more than 2 hours from the nearest hospital. Community health workers in these areas make life-or-death triage decisions with paper charts and no connectivity. Cloud-based AI requires what they don't have: internet, subscriptions, and infrastructure.

## The Solution

A complete, open-source AI health assistant that runs on hardware you can hold in one hand.

Any phone or tablet connects to the Pi's WiFi hotspot. No internet. No cloud. No subscriptions. No patient data stored.

<table>
<tr>
<td width="33%" align="center">
<h3>Triage</h3>
<p>WHO IMNCI symptom assessment.<br>Deterministic classification.<br>Color-coded urgency.</p>
<code>RED</code> = Refer urgently<br>
<code>YELLOW</code> = Treat at facility<br>
<code>GREEN</code> = Home care
</td>
<td width="33%" align="center">
<h3>Medicines</h3>
<p>WHO Essential Medicines List.<br>Weight-based dosing calculator.<br>Drug interaction warnings.</p>
<em>Doses come from lookup tables,<br>never from the AI.</em>
</td>
<td width="33%" align="center">
<h3>Training</h3>
<p>AI-tutored case studies.<br>Interactive quizzes.<br>Socratic method learning.</p>
<em>Practice clinical skills<br>with instant feedback.</em>
</td>
</tr>
</table>

## Architecture

```
  Any Phone/Tablet                         Raspberry Pi 5
 ┌──────────────┐                        ┌─────────────────────────────────────┐
 │              │    WiFi AP             │                                     │
 │   Browser    │◄──"AI-Clinic"─────────►│   Flask Web App (port 80)           │
 │              │    (no password)        │   │                                 │
 └──────────────┘                        │   ├─► Triage Engine                 │
                                         │   │   WHO IMNCI decision trees      │
                                         │   │   100% deterministic (JSON)     │
                                         │   │                                 │
                                         │   ├─► Dosing Engine                 │
                                         │   │   WHO EML lookup tables         │
                                         │   │   Zero LLM involvement          │
                                         │   │                                 │
                                         │   └─► llama-server (:8081)          │
                                         │       Gemma 4 E2B Q4_K_M           │
                                         │       ~10 tokens/sec                │
                                         │       Translates, never decides     │
                                         └─────────────────────────────────────┘
```

**The critical design choice:** The LLM is a **translator**, not a **decision-maker**. Medical classifications come from deterministic WHO guideline lookup tables that any doctor can audit in JSON. The AI converts between natural language and structured data. It never generates a diagnosis. It never calculates a dose.

## The $170 Bill of Materials

| Component | Spec | Cost |
|-----------|------|-----:|
| Raspberry Pi 5 | 8GB, Quad A76 @ 2.4GHz | $80 |
| microSD Card | 64GB, A2-rated | $10 |
| USB-C Power Supply | 27W (5V/5A) | $12 |
| Active Cooler | Heatsink + fan | $5 |
| Case | Pi 5 compatible | $8 |
| **Mains-powered total** | | **$115** |
| | | |
| Solar Panel | 20W monocrystalline | $25 |
| LiFePO4 Battery | 12V 7.5Ah (~8hr runtime) | $25 |
| Charge Controller | PWM 10A, 5V USB out | $5 |
| **Solar-equipped total** | | **$170** |

> For comparison: a single ChatGPT Plus subscription is $240/year and requires internet.

See [docs/HARDWARE_BOM.md](docs/HARDWARE_BOM.md) for full sourcing details and power budget analysis.

## Quick Start

### Development (any machine)

```bash
git clone https://github.com/OliWoods-Org/mama-ai-clinic.git
cd mama-ai-clinic
make setup             # Create venv, install deps
make download-model    # Download Gemma 4 E2B GGUF (~1.5GB)
make dev               # Start Flask dev server on :5000
```

### With LLM inference

```bash
# In terminal 1: start llama-server
llama-server \
  -m inference/models/gemma-4-e2b-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8081 -t 4 -c 2048

# In terminal 2: start the web app
make dev
```

Open `http://localhost:5000` -- the triage engine, dosing calculator, and training modules all work without the LLM. The AI features activate when llama-server is running.

## Deploy to Raspberry Pi

```bash
make build    # Build complete SD card image (requires Docker)
make flash    # Flash to SD card (auto-detects removable media)
```

Insert SD card. Power on Pi. Connect any device to **"AI-Clinic"** WiFi. Done.

The Pi broadcasts an open WiFi network with captive portal -- any phone that connects is automatically redirected to the clinic interface. Same UX as hotel WiFi.

## Safety Design

This is a medical tool. Safety is not a feature, it's the architecture.

| Layer | Approach |
|-------|----------|
| **Triage logic** | Deterministic IMNCI decision trees in auditable JSON. No LLM involvement. |
| **Dosing math** | Weight/age lookup tables from WHO EML. Never LLM-generated. |
| **Red-line tests** | 7 safety-critical cases tested in CI. Any danger sign = RED. Always. |
| **Disclaimers** | Persistent banner on every screen. Every response includes safety notice. |
| **Patient data** | Zero persistence. Session lives in browser tab only. Nothing stored. |
| **Prompt guardrails** | All system prompts enforce referral-first behavior. Uncertainty = refer. |

```bash
make safety-eval    # Run red-line safety test suite
make test           # Run full test suite (22 triage + dosing tests)
```

See [DISCLAIMER.md](DISCLAIMER.md) -- this is a decision-support tool, not a medical device.

## For NGOs

**You don't need to be technical to deploy this.**

| Document | What it covers |
|----------|---------------|
| [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | Step-by-step field deployment for non-technical staff |
| [Hardware BOM](docs/HARDWARE_BOM.md) | What to buy, where to buy it, bulk procurement |
| [Solar Setup](docs/SOLAR_SETUP.md) | Off-grid power wiring, panel sizing, battery selection |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common field issues and fixes |

### Target deployment partners

| Organization | Why |
|-------------|-----|
| **IRC** (International Rescue Committee) | 40+ country presence, health programming |
| **UNICEF** | Supply chain reaching every country on earth |
| **DNDi** (Drugs for Neglected Diseases) | Clinical expertise in resource-limited settings |
| **MSF** (Doctors Without Borders) | Field deployment experience |
| **WHO** Digital Health Division | Standards-setting authority |

## Model Compatibility

| Model | GGUF Size | RAM | Speed (Pi 5) | Status |
|-------|----------|-----|-------------|--------|
| **Gemma 4 E2B** | ~1.5GB | ~2GB | ~10 tok/s | **Default** |
| Gemma 3 1B | ~700MB | ~1GB | ~15 tok/s | Fallback |
| Gemma 4 E4B | ~3GB | ~4GB | ~5 tok/s | Forward-compatible |

Swap models with a single line in `inference/config.yaml`. The architecture is model-agnostic -- any GGUF-compatible model works via llama.cpp.

## Contributing

We need **clinicians**, **developers**, **translators**, and **field workers**. See [CONTRIBUTING.md](CONTRIBUTING.md).

**Priority areas:**
- Clinical review of IMNCI decision trees (`app/knowledge/imnci/`)
- Translation to deployment languages (French, Spanish, Swahili, Arabic, Hindi)
- Real-world field testing and feedback
- Additional WHO Essential Medicines (currently 6 of ~400)

## Project Structure

```
mama-ai-clinic/
├── app/                    # Flask web application
│   ├── services/           # Core engines (triage, dosing, LLM client)
│   ├── knowledge/          # WHO medical knowledge bases (JSON)
│   ├── templates/          # Mobile-first Jinja2 HTML
│   └── static/             # CSS + vanilla JS (no build step)
├── inference/              # Model config, download, benchmark
├── image/                  # SD card image builder
├── networking/             # WiFi hotspot (hostapd/dnsmasq)
├── eval/                   # Clinical safety evaluation suite
├── tests/                  # Unit tests for safety-critical code
├── docs/                   # Deployment guides, BOM, thesis
└── hardware/               # 3D-printable case STL, wiring diagrams
```

---

<p align="center">
  <br>
  <strong>An <a href="https://mama.oliwoods.ai/foundation">OliWoods Foundation</a> Project</strong>
  <br>
  <em>Open-source AI infrastructure for humanitarian impact</em>
  <br><br>
  <a href="https://github.com/OliWoods-Org">GitHub</a> &bull;
  <a href="https://mama.oliwoods.ai/foundation">Foundation</a> &bull;
  <a href="https://mama.oliwoods.com">MAMA</a> &bull;
  <a href="https://cofounder.oliwoods.com">CoFounder</a>
  <br><br>
  <sub>
    The OliWoods Foundation builds open-source AI tools for humanitarian and public good.
    <br>
    Our commercial products — <a href="https://mama.oliwoods.com">MAMA</a> (autonomous AI operating system)
    and <a href="https://cofounder.oliwoods.com">CoFounder</a> (AI agent command center) —
    fund the foundation's open-source work.
    <br><br>
    <strong>Apache 2.0</strong> &mdash; Fork it. Deploy it. Save lives.
  </sub>
</p>
