import hashlib
import json

import yaml


def test_criteria_hash_matches():
    cfg = yaml.safe_load(open("configs/handshake.yaml"))
    h = hashlib.sha256(json.dumps(cfg["criteria"], sort_keys=True).encode()).hexdigest()
    assert h == open("configs/handshake.criteria.sha256").read().strip()


def test_registered_thresholds_present():
    c = yaml.safe_load(open("configs/handshake.yaml"))["criteria"]
    assert c["naming"]["spearman_min"] == 0.99 and c["certificate"]["L_max"] == 1.02
    assert c["ladder"]["gamma_min"] == 2.0 and c["certificate"]["horizon_K"] == 8
