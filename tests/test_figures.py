"""Figure data must reproduce the registered run: FIG 2's |Spearman| equals the handshake seed-0 value, FIG 3 has both curves."""
import json
import os

import pytest


@pytest.mark.skipif(not os.path.exists("results/figures/fig_data.json"), reason="figures not built")
def test_figure_numbers_match_registered_run():
    d = json.load(open("results/figures/fig_data.json"))
    h = json.load(open("results/handshake/main/0.json"))["arms"]["main"]["naming_abs_spearman"]
    assert abs(d["fig2_abs_spearman_seed0"] - h) < 0.005
    assert len(d["fig3_psi"]) == len(d["fig3_variant"]) == 6
    assert d["fig3_psi"][-1] < d["fig3_variant"][-1]          # psi stays predictable at the longest horizon, the fast block does not
    svg3 = open("results/figures/fig3_reach.svg").read()
    assert svg3.count("<polyline") == 2
