# The Raspberry Pi Moment for Humanitarian AI

## The Window

We are at the Raspberry Pi moment for humanitarian AI.

Gemma 4 E2B on a $35 Raspberry Pi 5 is frontier AI running offline in a remote village clinic or school. Not a toy. Not a demo. A system that can run WHO IMNCI triage, calculate essential medicine dosing, and train community health workers -- all without an internet connection, a cloud subscription, or a server room.

The window to define what responsible humanitarian AI on edge hardware looks like is 6-12 months wide. After that, the patterns will be set -- either by thoughtful open-source design, or by vendor lock-in and surveillance-by-default.

## The Numbers

**$170 per site.** That's the fully-loaded cost for a solar-powered, offline AI health assistant:
- $80: Raspberry Pi 5 (8GB)
- $35: Solar panel + battery + charge controller
- $55: SD card, case, cooler, power supply

Compare that to:
- A single ChatGPT Plus subscription: $240/year (requires internet)
- A basic telemedicine tablet: $300-800 (requires internet)
- An mHealth deployment per site: $500-2,000 (requires infrastructure)

**$170 once, no recurring costs, no internet, no vendor.**

## The Architecture Decision

The critical design choice: **the LLM is a translator, not a decision-maker.**

Medical classifications come from deterministic decision trees derived from WHO IMNCI guidelines. Dosing comes from lookup tables. The AI translates between human language and structured medical knowledge. It never generates a diagnosis. It never calculates a dose.

This is not a limitation -- it is the feature. It means:
1. Every clinical pathway is auditable by a doctor who doesn't understand AI
2. The system can be tested with conventional software testing
3. A regulatory body can review the decision logic in JSON, not in 2.3 billion parameters
4. If the model is wrong, the patient still gets the right classification

## The Target Partners

This reference design is built to hand to organizations that deploy health infrastructure at scale:

- **IRC** (International Rescue Committee) -- operates in 40+ countries
- **UNICEF** -- supply chain reaches every country on earth
- **DNDi** (Drugs for Neglected Diseases initiative) -- clinical expertise in resource-limited settings
- **MSF** (Doctors Without Borders) -- field deployment experience
- **WHO** Digital Health Division -- standards-setting authority

The goal is not to build a product. It is to build a **reference design** -- a blueprint that any organization can fork, adapt, and deploy. Apache 2.0 means no permission needed.

## The Standard We're Setting

By publishing this reference design, we're defining:
- What responsible offline AI in healthcare looks like
- How to safely combine LLMs with deterministic medical logic
- What the minimum viable hardware is for frontier AI in the field
- How to deploy AI without internet, without cloud, without surveillance

This is the standard for the next decade. Build it right. Open-source it. Hand it to the people who need it.
