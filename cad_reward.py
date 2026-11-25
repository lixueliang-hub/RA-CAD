import json
import math
import os
from pathlib import Path

import numpy as np

from racad.tools.cad_executor import (
    chamfer_distance,
    extract_cad_tokens,
    extract_final_code,
    run_cad,
    token_f1,
)

# 论文只给了符号，这三个值需要按你的数据尺度调
LAMBDA_F1 = 1.0
LAMBDA_CD = 1.0
GAMMA_CD = 10.0


def _load_json(value):
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, str):
        path = Path(value)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return json.loads(value)
    return None


def _load_points(value):
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return value.astype(np.float64)
    if isinstance(value, str) and Path(value).exists():
        return np.load(value).astype(np.float64)
    return None


def _zero(reason: str) -> dict:
    return {
        "score": 0.0,
        "extra_info": {
            "valid": 0.0,
            "f1": 0.0,
            "cd": 0.0,
            "reason": reason,
        },
    }


def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    extra_info = extra_info or {}

    code = extract_final_code(solution_str)
    if not code:
        return _zero("no executable code found")

    result = run_cad(code)
    if not result.ok:
        return _zero(result.error[:2000])

    gt_tokens = _load_json(extra_info.get("gt_tokens"))
    if gt_tokens is None:
        return _zero("missing gt_tokens")

    pred_tokens = extract_cad_tokens(code)
    f1 = token_f1(pred_tokens, list(gt_tokens))

    gt_points = _load_points(extra_info.get("gt_points"))
    if gt_points is None:
        return _zero("missing gt_points")

    cd = chamfer_distance(result.points, gt_points)
    cd = min(cd, 1e6)

    score = LAMBDA_F1 * f1 + LAMBDA_CD * math.exp(-GAMMA_CD * cd)

    return {
        "score": float(score),
        "extra_info": {
            "valid": 1.0,
            "f1": float(f1),
            "cd": float(cd),
            "reason": "",
        },
    }