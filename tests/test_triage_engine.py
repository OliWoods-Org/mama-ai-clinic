"""Tests for the IMNCI triage engine -- the safety-critical core."""

from app.services.triage_engine import (
    check_danger_signs,
    classify_diarrhea,
    classify_cough,
    classify_fever,
    GENERAL_DANGER_SIGNS,
)


class TestDangerSigns:
    def test_no_danger_signs(self):
        result = check_danger_signs([])
        assert result["has_danger_signs"] is False
        assert result["classification"] is None

    def test_single_danger_sign_triggers_red(self):
        for sign in GENERAL_DANGER_SIGNS:
            result = check_danger_signs([sign])
            assert result["has_danger_signs"] is True
            assert result["classification"] == "RED"
            assert "REFER URGENTLY" in result["action"]

    def test_multiple_danger_signs(self):
        result = check_danger_signs(["convulsions", "lethargic_or_unconscious"])
        assert result["has_danger_signs"] is True
        assert len(result["signs"]) == 2

    def test_invalid_sign_ignored(self):
        result = check_danger_signs(["not_a_real_sign"])
        assert result["has_danger_signs"] is False


class TestDiarrheaClassification:
    def test_severe_dehydration(self):
        result = classify_diarrhea(
            duration_days=2, blood_in_stool=False,
            sunken_eyes=True, skin_pinch="very_slow",
            drinking="not_able", restless_irritable=False, lethargic=True,
        )
        assert result["classification"] == "SEVERE DEHYDRATION"
        assert result["color"] == "RED"

    def test_some_dehydration(self):
        result = classify_diarrhea(
            duration_days=2, blood_in_stool=False,
            sunken_eyes=True, skin_pinch="slow",
            drinking="eager", restless_irritable=True, lethargic=False,
        )
        assert result["classification"] == "SOME DEHYDRATION"
        assert result["color"] == "YELLOW"

    def test_no_dehydration(self):
        result = classify_diarrhea(
            duration_days=2, blood_in_stool=False,
            sunken_eyes=False, skin_pinch="instant",
            drinking="normal", restless_irritable=False, lethargic=False,
        )
        assert result["classification"] == "NO DEHYDRATION"
        assert result["color"] == "GREEN"

    def test_dysentery_overrides(self):
        result = classify_diarrhea(
            duration_days=2, blood_in_stool=True,
            sunken_eyes=False, skin_pinch="instant",
            drinking="normal", restless_irritable=False, lethargic=False,
        )
        assert result["classification"] == "DYSENTERY"
        assert result["color"] == "YELLOW"

    def test_persistent_diarrhea(self):
        result = classify_diarrhea(
            duration_days=16, blood_in_stool=False,
            sunken_eyes=False, skin_pinch="instant",
            drinking="normal", restless_irritable=False, lethargic=False,
        )
        assert result["classification"] == "PERSISTENT DIARRHEA"
        assert result["color"] == "YELLOW"


class TestCoughClassification:
    def test_severe_pneumonia_with_danger_signs(self):
        result = classify_cough(
            age_group="2_months_to_12_months", cough_days=3,
            breathing_rate=40, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=True,
        )
        assert result["classification"] == "SEVERE PNEUMONIA OR VERY SEVERE DISEASE"
        assert result["color"] == "RED"

    def test_pneumonia_fast_breathing_infant(self):
        result = classify_cough(
            age_group="2_months_to_12_months", cough_days=3,
            breathing_rate=55, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=False,
        )
        assert result["classification"] == "PNEUMONIA"
        assert result["color"] == "YELLOW"

    def test_pneumonia_fast_breathing_child(self):
        result = classify_cough(
            age_group="12_months_to_5_years", cough_days=3,
            breathing_rate=45, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=False,
        )
        assert result["classification"] == "PNEUMONIA"
        assert result["color"] == "YELLOW"

    def test_no_pneumonia(self):
        result = classify_cough(
            age_group="12_months_to_5_years", cough_days=3,
            breathing_rate=30, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=False,
        )
        assert result["classification"] == "COUGH OR COLD"
        assert result["color"] == "GREEN"

    def test_chronic_cough(self):
        result = classify_cough(
            age_group="12_months_to_5_years", cough_days=21,
            breathing_rate=30, chest_indrawing=False,
            stridor_at_rest=False, has_danger_signs=False,
        )
        assert result["classification"] == "CHRONIC COUGH"
        assert result["color"] == "YELLOW"


class TestFeverClassification:
    def test_very_severe_febrile_disease(self):
        result = classify_fever(
            temperature_c=39.5, fever_days=2,
            stiff_neck=True, malaria_risk=False,
            rdt_result=None, measles_signs=False, has_danger_signs=False,
        )
        assert result["classification"] == "VERY SEVERE FEBRILE DISEASE"
        assert result["color"] == "RED"

    def test_malaria_positive(self):
        result = classify_fever(
            temperature_c=39.0, fever_days=2,
            stiff_neck=False, malaria_risk=True,
            rdt_result="positive", measles_signs=False, has_danger_signs=False,
        )
        assert result["classification"] == "MALARIA"
        assert result["color"] == "YELLOW"

    def test_fever_likely_viral(self):
        result = classify_fever(
            temperature_c=38.5, fever_days=2,
            stiff_neck=False, malaria_risk=False,
            rdt_result=None, measles_signs=False, has_danger_signs=False,
        )
        assert result["classification"] == "FEVER - LIKELY VIRAL"
        assert result["color"] == "GREEN"
