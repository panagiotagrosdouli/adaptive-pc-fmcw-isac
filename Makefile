PYTHON ?= python
PYTEST ?= pytest
TRAIN_NPZ ?= data/processed/womd_official_samples.npz
OFFICIAL_VALIDATION_NPZ ?= data/processed/womd_v131_official_validation.npz
WOMD_TRAIN_TFRECORDS ?= data/raw/womd/training
WOMD_VALIDATION_TFRECORDS ?= data/raw/womd/validation
ARTIFACT_ROOT ?= artifacts/paper_final

.PHONY: test stage00 stage00-test stage01 stage01-test stage01-export-train stage01-export-validation stage05-test stage06-test stage07-test

test:
	$(PYTEST) -q

stage00-test:
	$(PYTEST) -q stages/00_freeze_and_provenance/tests

stage00:
	$(PYTHON) stages/00_freeze_and_provenance/scripts/freeze_stage00.py \
		--train-npz $(TRAIN_NPZ) \
		--official-validation-npz $(OFFICIAL_VALIDATION_NPZ) \
		--output-root $(ARTIFACT_ROOT)

stage01-test:
	$(PYTEST) -q stages/01_womd_data_pipeline/test_audit_corpus.py stages/01_womd_data_pipeline/test_export_contract.py

stage01-export-train:
	$(PYTHON) stages/01_womd_data_pipeline/export_womd_tfrecord.py \
		--input $(WOMD_TRAIN_TFRECORDS) --output $(TRAIN_NPZ) \
		--report $(ARTIFACT_ROOT)/data_audit/training_export.json

stage01-export-validation:
	$(PYTHON) stages/01_womd_data_pipeline/export_womd_tfrecord.py \
		--input $(WOMD_VALIDATION_TFRECORDS) --output $(OFFICIAL_VALIDATION_NPZ) \
		--fixed-split official_validation \
		--report $(ARTIFACT_ROOT)/data_audit/official_validation_export.json

stage01:
	$(PYTHON) stages/01_womd_data_pipeline/audit_corpus.py $(TRAIN_NPZ) \
		--output $(ARTIFACT_ROOT)/data_audit/training_audit.json
	$(PYTHON) stages/01_womd_data_pipeline/audit_corpus.py $(OFFICIAL_VALIDATION_NPZ) \
		--expected-split official_validation \
		--output $(ARTIFACT_ROOT)/data_audit/official_validation_audit.json
	$(PYTHON) stages/01_womd_data_pipeline/audit_split_ownership.py \
		$(TRAIN_NPZ) $(OFFICIAL_VALIDATION_NPZ) \
		--output $(ARTIFACT_ROOT)/data_audit/stage01_split_ownership.json

stage05-test:
	$(PYTEST) -q stages/05_official_predictor_evaluation

stage06-test:
	$(PYTEST) -q stages/06_packet_scheduling

stage07-test:
	$(PYTEST) -q stages/07_statistics_and_figures
