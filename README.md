# Pi AI Clinic

**Frontier AI on a $35 Raspberry Pi. Fully offline. For the world's most underserved clinics.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

> We are at the Raspberry Pi moment for humanitarian AI. A Gemma model on a $35 Raspberry Pi 5 is frontier AI running offline in a remote village clinic or school. The window to define what responsible humanitarian AI on edge hardware looks like is 6-12 months wide.

## What This Is

A complete, open-source reference design for deploying an AI health assistant on a Raspberry Pi 5. **$170 per site. Fully offline. Apache 2.0 licensed.**

Any phone or tablet connects to the Pi's WiFi hotspot and gets:

- **Clinic Triage** -- WHO IMNCI-based symptom assessment with AI-assisted classification
- **Medicines Dosing** -- Essential medicines lookup with weight/age-based dosing calculator
- **Health Worker Training** -- Interactive case studies, quizzes, and AI-tutored learning

No internet. No cloud. No subscriptions. No patient data stored.

## The $170 Bill of Materials

| Component | Cost |
|-----------|------|
| Raspberry Pi 5 (8GB) | $80 |
| 64GB microSD (A2) | $10 |
| USB-C power supply | $12 |
| Active cooler | $5 |
| Case | $8 |
| **Mains-powered total** | **$115** |
| 20W solar panel | $25 |
| LiFePO4 battery | $25 |
| Charge controller | $5 |
| **Solar-equipped total** | **$170** |

## Architecture

```
Phone/Tablet                    Raspberry Pi 5
+-----------+     WiFi AP      +---------------------------+
|  Browser  | <-- "AI-Clinic" --> |  Flask Web App (port 80) |
+-----------+                  |    |                       |
                               |    +-> Triage Engine       |
                               |    |   (IMNCI decision     |
                               |    |    trees - JSON)       |
                               |    |                       |
                               |    +-> Dosing Engine       |
                               |    |   (WHO EML tables)     |
                               |    |                       |
                               |    +-> llama-server :8081  |
                               |        (Gemma 4 E2B Q4)    |
                               +---------------------------+
```

**Key design principle:** The LLM is a *translator*, not a *decision-maker*. Medical decisions come from deterministic WHO guideline lookup tables. The LLM converts between natural language and structured data. Dosing math is never delegated to the AI.

## Quick Start (Development)

```bash
# Clone and set up
git clone https://github.com/oliwoods/pi-ai-clinic.git
cd pi-ai-clinic
./scripts/setup_dev.sh

# Download the model (requires internet, ~1.5GB)
./inference/download_model.sh

# Start llama-server
./inference/start_server.sh

# Start the web app
cd app && flask run --host=0.0.0.0 --port=5000
```

## Deploy to Pi (SD Card Image)

```bash
# Build the complete SD card image
./image/build.sh

# Flash to SD card
./image/flash.sh /dev/sdX  # replace with your SD card device
```

Insert the SD card, power on the Pi, connect any device to "AI-Clinic" WiFi. Done.

## Safety Design

This project takes medical safety seriously:

1. **Structured decision trees** for all triage classifications -- deterministic, auditable, no LLM involvement in the decision path
2. **Dosing calculations from lookup tables** -- never LLM-generated
3. **Red-line safety tests** in CI -- cases that MUST trigger urgent referral are tested on every commit
4. **Prominent disclaimers** on every screen -- "This is not a substitute for professional medical care"
5. **No patient data persistence** -- session data lives only in the browser tab

See [DISCLAIMER.md](DISCLAIMER.md) for full medical disclaimer.

## For NGOs

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for step-by-step field deployment instructions written for non-technical staff.

See [docs/SOLAR_SETUP.md](docs/SOLAR_SETUP.md) for off-grid power configuration.

## Contributing

We welcome contributions from developers, clinicians, translators, and field workers. See [CONTRIBUTING.md](CONTRIBUTING.md).

Priority areas:
- Clinical review of IMNCI decision trees
- Translation to deployment languages (French, Spanish, Swahili, Arabic, Hindi)
- Field testing and feedback
- Solar power optimization

## Target Partners

This reference design is built to hand to:
- **IRC** (International Rescue Committee)
- **UNICEF**
- **DNDi** (Drugs for Neglected Diseases initiative)
- **MSF** (Doctors Without Borders)
- **WHO** Digital Health Division

## License

Apache 2.0. See [LICENSE](LICENSE).

The medical knowledge bases are sourced from WHO open-access publications. See [app/knowledge/README.md](app/knowledge/README.md) for data provenance and licensing details.
