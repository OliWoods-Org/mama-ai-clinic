"""Safety evaluation -- red-line cases that MUST trigger urgent referral.

These cases test that the triage engine never misses a dangerous condition.
Run this in CI on every commit. A single failure = blocked merge.
"""

from app.services.triage_engine import check_danger_signs, classify_cough, classify_fever


RED_LINE_CASES = [
    {
        "name": "Lethargic child must be referred",
        "test": lambda: check_danger_signs(["lethargic_or_unconscious"]),
        "expected_color": "RED",
    },
    {
        "name": "Convulsing child must be referred",
        "test": lambda: check_danger_signs(["convulsions"]),
        "expected_color": "RED",
    },
    {
        "name": "Child who cannot drink must be referred",
        "test": lambda: check_danger_signs(["not_able_to_drink_or_breastfeed"]),
        "expected_color": "RED",
    },
    {
        "name": "Child vomiting everything must be referred",
        "test": lambda: check_danger_signs(["vomits_everything"]),
        "expected_color": "RED",
    },
    {
        "name": "Stridor at rest = severe pneumonia",
        "test": lambda: classify_cough(
            age_group="12_months_to_5_years", cough_days=1,
            breathing_rate=30, chest_indrawing=False,
            stridor_at_rest=True, has_danger_signs=False,
        ),
        "expected_color": "RED",
    },
    {
        "name": "Stiff neck with fever = very severe febrile disease",
        "test": lambda: classify_fever(
            temperature_c=39.0, fever_days=1,
            stiff_neck=True, malaria_risk=False,
            rdt_result=None, measles_signs=False, has_danger_signs=False,
        ),
        "expected_color": "RED",
    },
    {
        "name": "Danger signs + cough = severe pneumonia",
        "test": lambda: classify_cough(
            age_group="12_months_to_5_years", cough_days=1,
            breathing_rate=30, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=True,
        ),
        "expected_color": "RED",
    },
]


def run_safety_eval():
    """Run all red-line safety cases. Returns (passed, failed, results)."""
    passed = 0
    failed = 0
    results = []

    for case in RED_LINE_CASES:
        result = case["test"]()
        actual_color = result.get("color") or result.get("classification")

        if actual_color == case["expected_color"]:
            passed += 1
            results.append({"name": case["name"], "status": "PASS", "expected": case["expected_color"], "actual": actual_color})
        else:
            failed += 1
            results.append({"name": case["name"], "status": "FAIL", "expected": case["expected_color"], "actual": actual_color})

    return passed, failed, results


if __name__ == "__main__":
    passed, failed, results = run_safety_eval()

    print("=== MAMA AI Clinic -- Safety Evaluation ===\n")

    for r in results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {r['name']}")
        if r["status"] == "FAIL":
            print(f"         Expected: {r['expected']}, Got: {r['actual']}")

    print(f"\n{passed} passed, {failed} failed out of {len(results)} red-line cases")

    if failed > 0:
        print("\nSAFETY EVALUATION FAILED -- these cases MUST produce RED classification")
        exit(1)
    else:
        print("\nAll safety cases passed.")
