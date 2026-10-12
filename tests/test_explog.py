import json

from isj import explog


def make(tmp_path, n=3):
    p = str(tmp_path / "chain.jsonl")
    for i in range(n):
        explog.append("note", f"event {i}", stage="A", path=p)
    return p


def test_chain_links_and_verifies(tmp_path):
    p = make(tmp_path)
    es = explog.read_all(p)
    assert es[0]["prev_hash"] == explog.GENESIS_PREV
    assert all(es[i]["prev_hash"] == es[i - 1]["hash"] for i in (1, 2))
    assert explog.verify(p)[0]


def test_edit_is_detected(tmp_path):
    p = make(tmp_path)
    lines = open(p).read().splitlines()
    e = json.loads(lines[1]); e["what"] = "rewritten"
    lines[1] = explog.canonical(e)
    open(p, "w").write("\n".join(lines) + "\n")
    ok, msg = explog.verify(p)
    assert not ok and "entry 1" in msg


def test_deletion_and_reorder_are_detected(tmp_path):
    p = make(tmp_path, 4)
    lines = open(p).read().splitlines()
    open(p, "w").write("\n".join(lines[:1] + lines[2:]) + "\n")
    assert not explog.verify(p)[0]


def test_artifact_change_is_detected(tmp_path):
    art = tmp_path / "result.json"; art.write_text("{}")
    p = str(tmp_path / "c.jsonl")
    explog.append("run", "x", artifact_paths=[str(art)], path=p)
    assert explog.verify(p)[0]
    art.write_text('{"edited": 1}')
    ok, msg = explog.verify(p)
    assert not ok and "changed" in msg
    assert explog.verify(p, check_artifacts=False)[0]   # the chain itself is still intact


def test_concurrent_appends_keep_chain(tmp_path):
    import multiprocessing as mp
    p = str(tmp_path / "c.jsonl")
    with mp.get_context("fork").Pool(4) as pool:
        pool.starmap(_app, [(p, i) for i in range(12)])
    assert len(explog.read_all(p)) == 12 and explog.verify(p)[0]


def _app(p, i):
    explog.append("note", f"w{i}", path=p)
