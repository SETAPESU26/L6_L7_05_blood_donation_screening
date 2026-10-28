"""
Code Coverage Test Suite for Blood Donation Screening Module.
Lab 6 - SE Lab
Student: Aarav Yuval B G (PES1UG24AM004)
Target Module: blood_donation_screening.py
"""

import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


class TestProcessDonorCohortCodeCoverage:
    """Tests covering all executable statements in process_donor_cohort."""

    def test_invalid_cohort_container_type_raises_value_error(self):
        """Verifies ValueError when cohorts argument is not a list."""
        with pytest.raises(ValueError, match="Invalid cohort list or volume"):
            process_donor_cohort("invalid_string_cohort", 450)

    def test_non_positive_volume_raises_value_error(self):
        """Verifies ValueError when standard volume is zero or negative."""
        with pytest.raises(ValueError, match="Invalid cohort list or volume"):
            process_donor_cohort([], 0)

        with pytest.raises(ValueError, match="Invalid cohort list or volume"):
            process_donor_cohort([], -100)

    def test_empty_cohort_list_returns_zero_yield(self):
        """Verifies return value when cohort list is empty."""
        result = process_donor_cohort([], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_unregistered_clinic_cohort_is_skipped(self):
        """Verifies unregistered clinic cohorts are skipped via continue statement."""
        cohorts = [
            {
                "clinic_registered": False,
                "type": "standard",
                "donors": [{"age": 30, "weight_kg": 70, "hb": 15.0}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_single_accepted_donor_standard_cohort(self):
        """Verifies accepted donor adds standard volume and returns ACCEPTED status."""
        cohorts = [
            {
                "clinic_registered": True,
                "type": "standard",
                "fast_track": False,
                "donors": [{"age": 28, "weight_kg": 65, "hb": 14.5}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    def test_underage_donor_is_deferred(self):
        """Verifies donor with age < 17 is deferred and volume is not added."""
        cohorts = [
            {
                "clinic_registered": True,
                "donors": [{"age": 16, "weight_kg": 60, "hb": 14.0}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_underweight_donor_is_deferred(self):
        """Verifies donor with weight < 50 is deferred."""
        cohorts = [
            {
                "clinic_registered": True,
                "donors": [{"age": 22, "weight_kg": 45, "hb": 14.0}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_low_hemoglobin_standard_cohort_deferred(self):
        """Verifies donor with hb < 12.5 in standard cohort is deferred without aborting cohort."""
        cohorts = [
            {
                "clinic_registered": True,
                "type": "standard",
                "donors": [
                    {"age": 25, "weight_kg": 60, "hb": 11.8},
                    {"age": 30, "weight_kg": 70, "hb": 14.0},
                ],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    def test_high_altitude_low_hemoglobin_resets_volume_and_breaks(self):
        """Verifies high altitude cohort with low hb donor resets collected volume and breaks loop."""
        cohorts = [
            {
                "clinic_registered": True,
                "type": "high_altitude",
                "donors": [
                    {"age": 30, "weight_kg": 70, "hb": 14.0},  # Accepted first (+450)
                    {"age": 25, "weight_kg": 60, "hb": 11.0},  # Triggers reset & break
                    {"age": 35, "weight_kg": 80, "hb": 15.0},  # Never reached
                ],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_high_hemoglobin_donor_is_deferred(self):
        """Verifies donor with hb > 18.0 is deferred via continue."""
        cohorts = [
            {
                "clinic_registered": True,
                "donors": [{"age": 30, "weight_kg": 75, "hb": 18.5}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_fast_track_adds_bonus_volume(self):
        """Verifies fast_track cohort adds 50 ml bonus to collected volume."""
        cohorts = [
            {
                "clinic_registered": True,
                "fast_track": True,
                "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result == {"collected_ml": 500, "status": "ACCEPTED"}

    def test_high_deferral_status_when_deferrals_exceed_four(self):
        """Verifies HIGH_DEFERRAL status when deferred_count > 4."""
        cohorts = [
            {
                "clinic_registered": True,
                "donors": [
                    {"age": 15, "weight_kg": 60, "hb": 14.0},  # Deferral 1
                    {"age": 16, "weight_kg": 60, "hb": 14.0},  # Deferral 2
                    {"age": 25, "weight_kg": 40, "hb": 14.0},  # Deferral 3
                    {"age": 25, "weight_kg": 60, "hb": 10.0},  # Deferral 4
                    {"age": 25, "weight_kg": 60, "hb": 19.0},  # Deferral 5
                    {"age": 25, "weight_kg": 65, "hb": 14.0},  # Accepted donor
                ],
            }
        ]
        result = process_donor_cohort(cohorts, 450)
        assert result["collected_ml"] == 450
        assert result["status"] == "HIGH_DEFERRAL"


class TestVerifyStorageCentrifugeCodeCoverage:
    """Tests covering all executable statements in verify_storage_centrifuge."""

    def test_empty_or_none_centrifuge_runs_returns_no_data(self):
        """Verifies NO_DATA returned when centrifuge_runs is empty or None."""
        assert verify_storage_centrifuge([]) == "NO_DATA"
        assert verify_storage_centrifuge(None) == "NO_DATA"

    def test_centrifuge_stable_spin(self):
        """Verifies STABLE status when all readings remain at or above 3000 RPM."""
        runs = [
            [3200, 3100, 3050, 3000],
            [3300, 3150],
        ]
        assert verify_storage_centrifuge(runs) == "STABLE"

    def test_centrifuge_abort_on_consecutive_drops(self):
        """Verifies ABORT_SPIN returned when RPM drops below 3000 twice consecutively."""
        runs = [
            [3100, 2800, 2900, 3200]
        ]
        assert verify_storage_centrifuge(runs) == "ABORT_SPIN"

    def test_centrifuge_streak_resets_on_recovery(self):
        """Verifies rpm_drop_streak resets to 0 when RPM recovers to >= 3000."""
        runs = [
            [2900, 3100, 2800]  # Isolated drops, never 2 consecutive
        ]
        assert verify_storage_centrifuge(runs) == "STABLE"
