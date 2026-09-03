PYTHON ?= python
PYTEST ?= pytest
TRAIN_NPZ ?= data/processed/womd_official_samples.npz
OFFICIAL_VALIDATION_NPZ ?= data/processed/womd_v131_official_validation.npz
ARTIFACT_ROOT ?= artifacts/paper_final

.PHONY: test stage00 stage00-test

test:
	$(PYTEST) -q

stage00-test:
	$(PYTEST) -q stages/00_freeze_and_provenance/tests

stage00:
	$(PYTHON) stages/00_freeze_and_provenance/scripts/freeze_stage00.py \
		--train-npz $(TRAIN_NPZ) \
		--official-validation-npz $(OFFICIAL_VALIDATION_NPZ) \
		--output-root $(ARTIFACT_ROOT)
