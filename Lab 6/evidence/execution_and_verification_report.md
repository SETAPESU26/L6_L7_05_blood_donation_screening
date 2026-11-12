# Lab 6: Code and Branch Coverage Analysis Report

**Course:** Software Engineering Lab (CS305)  
**Student Name:** Aarav Yuval B G  
**SRN:** PES1UG24AM004  
**Date:** 2026-10-28  
**Target Module:** `Lab 6/blood_donation_screening.py`  
**Repository:** `https://github.com/SETAPESU26/L6_L7_05_blood_donation_screening.git`

---

## 1. Executive Summary

This report documents the rigorous test engineering and coverage analysis performed for **Lab 6: Code and Branch Coverage Analysis** on the `blood_donation_screening` module.

- **Baseline Coverage:** 47% statement coverage, 43% branch coverage (1 starter test).
- **Stage 1 (Code Coverage):** **100% statement coverage** (45/45 statements executed across 16 test cases).
- **Stage 2 (Branch Coverage):** **100% branch coverage** (32/32 branches executed across 43 test cases).
- **All 60 tests** pass cleanly with zero failures and zero warnings.

---

## 2. Test Execution & Coverage Metrics

### 2.1 Baseline Coverage
- **Command:** `coverage run --branch --source=blood_donation_screening -m pytest test_blood_donation.py`
- **Result:**
  ```text
  Name                          Stmts   Miss Branch BrPart  Cover   Missing
  -------------------------------------------------------------------------
  blood_donation_screening.py      45     24     32      8    43%   3, 10, 21-22, 25-28, 30-31, 36, 39, 41, 46-58
  ```

### 2.2 Stage 1: Statement Coverage (`CodeCoverageTest_blood_donation_screening.py`)
- **Command:** `coverage run --source=blood_donation_screening -m pytest CodeCoverageTest_blood_donation_screening.py`
- **Metric:** **100% Statement Coverage** (0 missing statements)
- **Result:**
  ```text
  Name                          Stmts   Miss  Cover   Missing
  -----------------------------------------------------------
  blood_donation_screening.py      45      0   100%
  ```
- **Tests Passed:** 16 passed in 0.08s.

### 2.3 Stage 2: Branch Coverage (`BranchCoverageTest_blood_donation_screening.py`)
- **Command:** `coverage run --branch --source=blood_donation_screening -m pytest BranchCoverageTest_blood_donation_screening.py`
- **Metric:** **100% Branch Coverage** (32/32 branches, 0 partial branches)
- **Result:**
  ```text
  Name                          Stmts   Miss Branch BrPart  Cover   Missing
  -------------------------------------------------------------------------
  blood_donation_screening.py      45      0     32      0   100%
  -------------------------------------------------------------------------
  TOTAL                            45      0     32      0   100%
  ```
- **Tests Passed:** 43 passed in 0.12s.

---

## 3. Coverage Analysis & Test Architecture

### 3.1 `process_donor_cohort(cohorts, standard_volume_ml)`
1. **Input Guard:**
   - Evaluates short-circuit condition `not isinstance(cohorts, list)` (tested with `None`, `dict`, `str`, `int`, `tuple`).
   - Evaluates second operand `standard_volume_ml <= 0` (tested with `0`, `-1`, `-500`).
   - Evaluates valid input path (`[]`, positive standard volume).
2. **Cohort Loop & Clinic Registration:**
   - Loop non-entry (empty list `[]`).
   - `clinic_registered` missing or `False` skips cohort via `continue`.
   - `clinic_registered` is `True` enters donor processing.
3. **Donor Screening Criteria:**
   - Age `< 17` triggers deferral and continues.
   - Weight `< 50` triggers deferral and continues.
   - Boundary `age == 17` and `weight == 50.0` accepted.
   - Hemoglobin `< 12.5`:
     - Standard cohort: deferral count incremented, loop continues.
     - `high_altitude` cohort: volume reset to 0 and loop broken via `break`.
   - Hemoglobin `> 18.0`: deferral count incremented and loop continues.
   - Boundary `hb == 12.5` and `hb == 18.0` accepted into `else:` branch.
4. **Fast-Track Bonus:**
   - `fast_track: True` adds 50 ml bonus (tested both standalone and after a high-altitude break).
   - `fast_track: False` or omitted bypasses bonus.
5. **Yield & Deferral Precedence:**
   - `deferred_count > 4`: returns `HIGH_DEFERRAL` (takes precedence over `total_collected_ml == 0`).
   - `total_collected_ml == 0` (with `deferred_count <= 4`): returns `ZERO_YIELD`.
   - Positive yield with `deferred_count <= 4`: returns `ACCEPTED`.

### 3.2 `verify_storage_centrifuge(centrifuge_runs)`
1. **Empty Input Guard:**
   - `[]`, `None`, and `()` return `"NO_DATA"`.
2. **Run Iteration & Streak Reset:**
   - Empty inner run `[]` skips inner loop without crashing.
   - `rpm_drop_streak` initialized to 0 at the start of each run (verified with isolated drops across distinct runs).
3. **RPM Threshold & Abort:**
   - `rpm < 3000` increments `rpm_drop_streak`.
   - Boundary `rpm == 3000` does not increment drop streak; triggers `else: rpm_drop_streak = 0`.
   - `rpm_drop_streak >= 2` returns `"ABORT_SPIN"` immediately.
   - All stable runs return `"STABLE"`.

---

## 4. Deliverables and Evidence Inventory

| Deliverable | File Path | Status |
|-------------|-----------|--------|
| Statement Test Suite | `Lab 6/CodeCoverageTest_blood_donation_screening.py` | Verified (100% Stmts) |
| Branch Test Suite | `Lab 6/BranchCoverageTest_blood_donation_screening.py` | Verified (100% Branch) |
| Starter Test Suite | `Lab 6/test_blood_donation.py` | Preserved unmodified |
| Baseline Raw Report | `Lab 6/evidence/baseline_coverage_report.txt` | Captured |
| Stage 1 Raw Report | `Lab 6/evidence/code_coverage_report.txt` | Captured |
| Stage 1 Terminal Screenshot | `Lab 6/evidence/code_coverage_terminal.png` | Captured (PNG) |
| Stage 2 Raw Report | `Lab 6/evidence/branch_coverage_report.txt` | Captured |
| Stage 2 Terminal Screenshot | `Lab 6/evidence/branch_coverage_terminal.png` | Captured (PNG) |

---

## 5. Commit History

1. **Commit 1 (Stage 1 - Statement Coverage):**
   - SHA: `1672ea0`
   - Message: `test(lab6): add code coverage tests for blood donation screening`
2. **Commit 2 (Stage 2 - Branch Coverage):**
   - SHA: `7758380`
   - Message: `test(lab6): add branch coverage tests for blood donation screening`
