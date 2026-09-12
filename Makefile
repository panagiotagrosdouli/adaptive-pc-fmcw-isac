PYTHON ?= python3
ARTIFACT_DIR ?= artifacts/research
SEED_START ?= 10000
N_SEEDS ?= 100
COMM_BITS ?= 5000
SENSING_TRIALS ?= 1
ROBUST_DRAWS ?= 256
REFERENCE_DRAWS ?= 4096

.PHONY: setup setup-paper test validate-comm validate-sensing validate-physics pilot experiments analysis figures tables gate paper-results research-smoke research-calibration research-action-space research-distribution-shift research-qos-sensitivity

setup:
	$(PYTHON) -m pip install -e .[dev]

setup-paper:
	$(PYTHON) -m pip install -e .[all]

test:
	pytest -q

validate-comm:
	$(PYTHON) scripts/run_e1_e5_validation.py --output $(ARTIFACT_DIR)/e1_e5_validation.json

validate-sensing:
	$(PYTHON) scripts/run_stage7_validation.py --output $(ARTIFACT_DIR)/stage7_validation.json

validate-physics:
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment physics --n-seeds 1 --output $(ARTIFACT_DIR)/physics.json

pilot:
	mkdir -p $(ARTIFACT_DIR)/pilot
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment all-smoke --seed-start $(SEED_START) --n-seeds 2 --comm-bits 1000 --sensing-trials 1 --robust-draws 32 --reference-draws 128 --truth-draws 1 --bootstrap-resamples 200 --output $(ARTIFACT_DIR)/pilot/all-smoke.json

research-calibration:
	mkdir -p $(ARTIFACT_DIR)
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment reliability-calibration --seed-start $(SEED_START) --n-seeds $(N_SEEDS) --reference-draws $(REFERENCE_DRAWS) --output $(ARTIFACT_DIR)/reliability-calibration.json

research-action-space:
	mkdir -p $(ARTIFACT_DIR)
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment action-space --seed-start $(SEED_START) --n-seeds $(N_SEEDS) --comm-bits $(COMM_BITS) --sensing-trials $(SENSING_TRIALS) --robust-draws $(ROBUST_DRAWS) --output $(ARTIFACT_DIR)/action-space.json

research-distribution-shift:
	mkdir -p $(ARTIFACT_DIR)
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment distribution-shift --seed-start $(SEED_START) --n-seeds $(N_SEEDS) --comm-bits $(COMM_BITS) --sensing-trials $(SENSING_TRIALS) --robust-draws $(ROBUST_DRAWS) --truth-draws 4 --bootstrap-resamples 10000 --output $(ARTIFACT_DIR)/distribution-shift.json

research-qos-sensitivity:
	mkdir -p $(ARTIFACT_DIR)
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment qos-sensitivity --seed-start $(SEED_START) --n-seeds $(N_SEEDS) --comm-bits $(COMM_BITS) --sensing-trials $(SENSING_TRIALS) --robust-draws $(ROBUST_DRAWS) --output $(ARTIFACT_DIR)/qos-sensitivity.json

experiments:
	mkdir -p $(ARTIFACT_DIR)
	for exp in uncertainty stress pareto ablations mismatch full-metrics reliability-targets confidence-maps uncertainty-sources action-space qos-sensitivity; do \
		$(PYTHON) scripts/run_supplemental_v2_1.py --experiment $$exp --seed-start $(SEED_START) --n-seeds $(N_SEEDS) --comm-bits $(COMM_BITS) --sensing-trials $(SENSING_TRIALS) --robust-draws $(ROBUST_DRAWS) --output $(ARTIFACT_DIR)/$$exp.json || exit 1; \
	done
	$(MAKE) research-calibration
	$(MAKE) research-distribution-shift
	$(MAKE) validate-physics
	$(PYTHON) scripts/run_supplemental_v2_1.py --experiment runtime --seed-start $(SEED_START) --n-seeds 10 --output $(ARTIFACT_DIR)/runtime.json

analysis:
	$(PYTHON) scripts/generate_supplemental_v2_1_figures.py --input-dir $(ARTIFACT_DIR) --output-dir $(ARTIFACT_DIR)/figures

figures: analysis

tables:
	$(PYTHON) scripts/generate_research_tables.py --input-dir $(ARTIFACT_DIR) --output-dir $(ARTIFACT_DIR)/tables

gate:
	$(PYTHON) scripts/check_research_submission_gate.py --input-dir $(ARTIFACT_DIR) --output $(ARTIFACT_DIR)/submission-gate.json

paper-results: experiments gate figures tables

research-smoke:
	$(MAKE) test
	$(MAKE) pilot
