# Hardware Bill of Materials

## Core System ($115)

| # | Component | Specification | Est. Cost | Notes |
|---|-----------|--------------|-----------|-------|
| 1 | Raspberry Pi 5 | 8GB LPDDR4X, BCM2712 Quad A76 @ 2.4GHz | $80 | 8GB is mandatory -- 4GB will not run the model + OS + app |
| 2 | microSD Card | 64GB, SanDisk Extreme A2 (or equivalent) | $10 | A2 rated for fast random I/O; important for model loading |
| 3 | Power Supply | Official Pi 5 PSU, 27W USB-C PD (5V/5A) | $12 | Must be 5A capable; standard phone chargers are insufficient |
| 4 | Active Cooler | Official Pi 5 active cooler (heatsink + fan) | $5 | Non-negotiable for sustained LLM inference |
| 5 | Case | Pi 5 compatible case with cooler cutout | $8 | Or 3D print from `hardware/case/` STL files |

## Solar Add-on ($55)

| # | Component | Specification | Est. Cost | Notes |
|---|-----------|--------------|-----------|-------|
| 6 | Solar Panel | 20W monocrystalline, 18V output | $25 | Sufficient for equatorial regions; 30W recommended for higher latitudes |
| 7 | Battery | 12V 7.5Ah LiFePO4 | $25 | ~8 hours runtime at 7W average draw; LiFePO4 preferred for heat tolerance |
| 8 | Charge Controller | PWM 10A with 5V/3A USB output | $5 | Must provide regulated 5V USB; or use separate buck converter |

## Optional Accessories

| Component | Specification | Est. Cost | When Needed |
|-----------|--------------|-----------|-------------|
| USB WiFi Adapter | Dual-band with external antenna | $8 | When built-in WiFi range (~30m) is insufficient |
| NVMe SSD + HAT | 128GB NVMe M.2 + Pi 5 M.2 HAT | $25 | Faster model loading; more durable than SD card for heavy writes |
| USB Microphone | Basic USB condenser mic | $8 | Future: voice input for audio-capable models |
| Pi Camera Module 3 | 12MP Sony IMX708 | $25 | Future: wound assessment with multimodal models |

## Power Budget

| Component | Idle | Active (LLM inference) |
|-----------|------|----------------------|
| Pi 5 (CPU) | 3W | 7W |
| Active Cooler | 0.5W | 0.5W |
| WiFi AP | 0.3W | 0.5W |
| **Total** | **~4W** | **~8W** |

With a 12V 7.5Ah battery (90Wh):
- Idle: ~22 hours
- Active inference: ~11 hours
- Mixed (10% active): ~18 hours

A 20W solar panel in equatorial sun (~5 peak sun hours) produces ~100Wh/day, exceeding the daily power budget.

## Sourcing

All components are available through standard electronics distributors worldwide:
- Raspberry Pi: rpilocator.com for stock tracking
- Solar components: common in off-grid solar markets globally
- SD cards: any electronics retailer

For bulk NGO procurement (100+ units), contact Raspberry Pi Foundation directly for volume pricing.
