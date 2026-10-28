"""
Branch Coverage Test Suite for Blood Donation Screening Module.
Lab 6 - SE Lab
Student: Aarav Yuval B G (PES1UG24AM004)
Target Module: blood_donation_screening.py

This suite systematically exercises every branch, compound decision outcome,
short-circuit condition, loop boundary, and early exit in blood_donation_screening.py.
"""

import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


class TestProcessDonorCohortBranchCoverage:
    """Comprehensive branch coverage test cases for process_donor_cohort."""

    # -------------------------------------------------------------------------
    # Branch 1: Guard condition (not isinstance(cohorts, list) or standard_volume_ml <= 0)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("invalid_cohorts", [
        None,
        "not_a_list",
        {"donors": []},
        (1, 2, 3),
        42,
    ])
    def test_guard_cohorts_not_a_list_short_circuits_true(self, invalid_cohorts):
        """Branch: not isinstance(cohorts, list) is True -> raises ValueError."""
        with pytest.raises(ValueError, match="Invalid cohort list or volume"):
            process_donor_cohort(invalid_cohorts, 450)

    @pytest.mark.parametrize("invalid_volume", [0, -1, -500])
    def test_guard_volume_non_positive_evaluates_true(self, invalid_volume):
        """Branch: cohorts is list, standard_volume_ml <= 0 is True -> raises ValueError."""
        with pytest.raises(ValueError, match="Invalid cohort list or volume"):
            process_donor_cohort([], invalid_volume)

    def test_guard_valid_inputs_proceeds(self):
        """Branch: cohorts is list AND standard_volume_ml > 0 -> proceeds past guard."""
        result = process_donor_cohort([], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    # -------------------------------------------------------------------------
    # Branch 2: Outer loop (for cohort in cohorts)
    # -------------------------------------------------------------------------
    def test_cohort_loop_zero_iterations(self):
        """Branch: empty cohort list -> 0 iterations, total_collected_ml == 0 -> ZERO_YIELD."""
        assert process_donor_cohort([], 350) == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_cohort_loop_multiple_iterations_accumulates_volume(self):
        """Branch: multiple cohorts in list -> loops through each cohort."""
        cohorts = [
            {
                "clinic_registered": True,
                "donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}],
            },
            {
                "clinic_registered": True,
                "donors": [{"age": 30, "weight_kg": 65, "hb": 15.0}],
            },
        ]
        result = process_donor_cohort(cohorts, 400)
        assert result == {"collected_ml": 800, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 3: Clinic registration filter (if not cohort.get("clinic_registered", False): continue)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("unregistered_cohort", [
        {"clinic_registered": False, "donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}]},
        {"donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}]},  # Missing key defaults to False
        {"clinic_registered": None, "donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}]},
    ])
    def test_clinic_not_registered_skips_cohort(self, unregistered_cohort):
        """Branch: not clinic_registered is True -> continue executes, donors ignored."""
        result = process_donor_cohort([unregistered_cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_clinic_registered_true_proceeds_to_donors(self):
        """Branch: clinic_registered is True -> enters donor loop."""
        cohort = {"clinic_registered": True, "donors": [{"age": 22, "weight_kg": 55, "hb": 13.5}]}
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 4: Donor loop (for donor in donors)
    # -------------------------------------------------------------------------
    def test_empty_donors_list_skips_inner_loop(self):
        """Branch: donors is empty list -> inner loop has 0 iterations."""
        cohort = {"clinic_registered": True, "donors": []}
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_missing_donors_key_defaults_to_empty(self):
        """Branch: donors key missing -> defaults to empty list."""
        cohort = {"clinic_registered": True}
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    # -------------------------------------------------------------------------
    # Branch 5: Age and weight check (if age < 17 or weight < 50: continue)
    # -------------------------------------------------------------------------
    def test_age_below_threshold_defers_donor(self):
        """Branch: age < 17 is True (short-circuits weight) -> deferral incremented."""
        cohort = {
            "clinic_registered": True,
            "donors": [{"age": 16, "weight_kg": 75, "hb": 14.0}],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_weight_below_threshold_defers_donor(self):
        """Branch: age >= 17 is True, weight < 50 is True -> deferral incremented."""
        cohort = {
            "clinic_registered": True,
            "donors": [{"age": 17, "weight_kg": 49.9, "hb": 14.0}],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_age_and_weight_at_exact_lower_boundaries_accepted(self):
        """Branch: age == 17 and weight == 50 -> both False, donor proceeds to hb check."""
        cohort = {
            "clinic_registered": True,
            "donors": [{"age": 17, "weight_kg": 50.0, "hb": 13.0}],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 6 & 7: Hemoglobin lower bound and high_altitude break
    # (if hemoglobin < 12.5: ... if cohort_type == "high_altitude": break)
    # -------------------------------------------------------------------------
    def test_low_hb_standard_cohort_defers_without_break(self):
        """Branch: hb < 12.5 is True, cohort_type != 'high_altitude' -> defers, continues to next donor."""
        cohort = {
            "clinic_registered": True,
            "type": "standard",
            "donors": [
                {"age": 20, "weight_kg": 60, "hb": 12.4},  # Below 12.5 boundary -> deferred
                {"age": 22, "weight_kg": 65, "hb": 14.0},  # Second donor accepted
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    def test_low_hb_high_altitude_resets_volume_and_breaks_inner_loop(self):
        """Branch: hb < 12.5 is True, cohort_type == 'high_altitude' -> volume reset to 0, breaks loop."""
        cohort = {
            "clinic_registered": True,
            "type": "high_altitude",
            "donors": [
                {"age": 25, "weight_kg": 60, "hb": 14.0},  # Accepted (+450)
                {"age": 26, "weight_kg": 60, "hb": 12.4},  # Low hb -> volume=0 and break
                {"age": 27, "weight_kg": 60, "hb": 14.0},  # Never reached due to break
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_exact_hb_lower_boundary_accepted(self):
        """Branch: hb == 12.5 -> hb < 12.5 is False, proceeds to else."""
        cohort = {
            "clinic_registered": True,
            "type": "high_altitude",
            "donors": [{"age": 25, "weight_kg": 60, "hb": 12.5}],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 8: Hemoglobin upper bound (elif hemoglobin > 18.0: continue else: add volume)
    # -------------------------------------------------------------------------
    def test_high_hb_above_boundary_defers_donor(self):
        """Branch: hb > 18.0 is True -> deferred_count incremented, continue to next donor."""
        cohort = {
            "clinic_registered": True,
            "donors": [
                {"age": 30, "weight_kg": 70, "hb": 18.1},  # Deferred
                {"age": 32, "weight_kg": 75, "hb": 15.0},  # Accepted (+450)
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    def test_exact_hb_upper_boundary_accepted(self):
        """Branch: hb == 18.0 -> hb > 18.0 is False, falls into else (accepted)."""
        cohort = {
            "clinic_registered": True,
            "donors": [{"age": 30, "weight_kg": 70, "hb": 18.0}],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 9: Fast track bonus (if cohort.get("fast_track", False): total += 50)
    # -------------------------------------------------------------------------
    def test_fast_track_true_adds_bonus(self):
        """Branch: fast_track is True -> adds 50 ml to collected volume."""
        cohort = {
            "clinic_registered": True,
            "fast_track": True,
            "donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}],
        }
        result = process_donor_cohort([cohort], 400)
        assert result == {"collected_ml": 450, "status": "ACCEPTED"}

    def test_fast_track_false_does_not_add_bonus(self):
        """Branch: fast_track is False -> does not add 50 ml."""
        cohort = {
            "clinic_registered": True,
            "fast_track": False,
            "donors": [{"age": 25, "weight_kg": 60, "hb": 14.0}],
        }
        result = process_donor_cohort([cohort], 400)
        assert result == {"collected_ml": 400, "status": "ACCEPTED"}

    def test_fast_track_bonus_after_high_altitude_break(self):
        """Branch: high altitude breaks with 0 volume, then fast_track adds 50 ml."""
        cohort = {
            "clinic_registered": True,
            "type": "high_altitude",
            "fast_track": True,
            "donors": [{"age": 25, "weight_kg": 60, "hb": 10.0}],  # Low hb -> break, total=0
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 50, "status": "ACCEPTED"}

    # -------------------------------------------------------------------------
    # Branch 10 & 11: Return status precedence (deferred_count > 4, total == 0, else)
    # -------------------------------------------------------------------------
    def test_deferred_count_exactly_four_and_zero_volume_is_zero_yield(self):
        """Boundary: deferred_count == 4 (<= 4), total == 0 -> ZERO_YIELD status."""
        cohort = {
            "clinic_registered": True,
            "donors": [
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}

    def test_deferred_count_exactly_five_is_high_deferral_even_with_zero_yield(self):
        """Boundary: deferred_count == 5 (> 4) takes precedence over total == 0 -> HIGH_DEFERRAL."""
        cohort = {
            "clinic_registered": True,
            "donors": [
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 0, "status": "HIGH_DEFERRAL"}

    def test_deferred_count_five_with_positive_volume_is_high_deferral(self):
        """Branch: deferred_count > 4 with positive volume returns HIGH_DEFERRAL with volume intact."""
        cohort = {
            "clinic_registered": True,
            "donors": [
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 16, "weight_kg": 60, "hb": 14.0},
                {"age": 25, "weight_kg": 60, "hb": 14.0},  # Accepted
            ],
        }
        result = process_donor_cohort([cohort], 450)
        assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


class TestVerifyStorageCentrifugeBranchCoverage:
    """Comprehensive branch coverage test cases for verify_storage_centrifuge."""

    # -------------------------------------------------------------------------
    # Branch 12: Empty collection guard (if not centrifuge_runs)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("empty_input", [[], None, ()])
    def test_empty_or_falsy_centrifuge_input_returns_no_data(self, empty_input):
        """Branch: not centrifuge_runs evaluates to True -> returns NO_DATA."""
        assert verify_storage_centrifuge(empty_input) == "NO_DATA"

    def test_non_empty_runs_proceeds_to_outer_loop(self):
        """Branch: not centrifuge_runs evaluates to False -> enters run loop."""
        assert verify_storage_centrifuge([[3200]]) == "STABLE"

    # -------------------------------------------------------------------------
    # Branch 13 & 14: Loop over runs and rpms
    # -------------------------------------------------------------------------
    def test_empty_inner_run_does_not_abort(self):
        """Branch: run contains 0 RPM values -> inner loop doesn't execute, continues."""
        assert verify_storage_centrifuge([[]]) == "STABLE"
        assert verify_storage_centrifuge([[], [3200]]) == "STABLE"

    # -------------------------------------------------------------------------
    # Branch 15 & 16: RPM drop streak logic
    # (if rpm < 3000: streak += 1, if streak >= 2: abort else: streak = 0)
    # -------------------------------------------------------------------------
    def test_rpm_exactly_at_threshold_is_not_a_drop(self):
        """Boundary: rpm == 3000 enters else branch (streak resets to 0)."""
        runs = [[2900, 3000, 2900]]
        # 2900 (streak=1) -> 3000 (resets to 0) -> 2900 (streak=1) -> STABLE
        assert verify_storage_centrifuge(runs) == "STABLE"

    def test_rpm_above_threshold_resets_streak(self):
        """Branch: rpm > 3000 enters else branch and resets streak to 0."""
        runs = [[2800, 3500, 2700, 3400]]
        assert verify_storage_centrifuge(runs) == "STABLE"

    def test_single_low_rpm_in_each_of_multiple_runs_resets_per_run(self):
        """Branch: streak is reinitialized to 0 at the start of each run in outer loop."""
        runs = [
            [2500],  # streak=1 at end of run 1
            [2500],  # streak resets to 0 at start of run 2, becomes 1 -> never reaches 2
        ]
        assert verify_storage_centrifuge(runs) == "STABLE"

    def test_exactly_two_consecutive_drops_aborts_spin(self):
        """Boundary: streak reaches exactly 2 -> returns ABORT_SPIN."""
        runs = [
            [3200, 2999, 2999, 3200]
        ]
        assert verify_storage_centrifuge(runs) == "ABORT_SPIN"

    def test_three_consecutive_drops_aborts_immediately_on_second(self):
        """Branch: early return on second drop without executing third drop."""
        runs = [
            [2500, 2500, 2500]
        ]
        assert verify_storage_centrifuge(runs) == "ABORT_SPIN"

    def test_abort_occurs_in_subsequent_run(self):
        """Branch: first run is stable, second run triggers ABORT_SPIN."""
        runs = [
            [3200, 3100],
            [2800, 2700],  # Two consecutive drops in run 2
        ]
        assert verify_storage_centrifuge(runs) == "ABORT_SPIN"

    def test_all_stable_multiple_runs(self):
        """Branch: all runs complete normally without ever triggering ABORT_SPIN -> STABLE."""
        runs = [
            [3100, 3200, 3300],
            [3050, 3150, 3250],
        ]
        assert verify_storage_centrifuge(runs) == "STABLE"
