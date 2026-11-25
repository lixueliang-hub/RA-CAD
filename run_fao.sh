#!/usr/bin/env bash
set -euo pipefail

export HYDRA_FULL_ERROR=1
export TOKENIZERS_PARALLELISM=false

MODEL_PATH=${MODEL_PATH:-/models/racad_ccb}
PROJECT_ROOT=${PROJECT_ROOT:-/workspace/racad_fao}

python -m verl.trainer.main_ppo \
  --config-path="${PROJECT_ROOT}/configs" \
  --config-name=fao \
  actor_rollout_ref.model.path="${MODEL_PATH}" \
  data.train_files="${PROJECT_ROOT}/data/train.jsonl" \
  data.val_files="${PROJECT_ROOT}/data/val.jsonl" \
  trainer.n_gpus_per_node=2 \
  trainer.nnodes=1 \
  trainer.total_epochs=1