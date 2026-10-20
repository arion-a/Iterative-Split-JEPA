import io
import pickle

import numpy as np
import pytest

from isj import safe_npy


def _npy(obj):
    buf = io.BytesIO()
    a = np.empty((), dtype=object); a[()] = obj
    np.save(buf, a, allow_pickle=True)
    return buf.getvalue()


def test_loads_dict_of_arrays():
    d = {"energy": np.arange(6.0).reshape(2, 3), "reject": np.zeros((2, 3), bool)}
    out = safe_npy.load_object_npy(_npy(d))
    assert set(out) == {"energy", "reject"} and np.array_equal(out["energy"], d["energy"])


def test_blocks_code_execution():
    class Evil:
        def __reduce__(self):
            import os
            return (os.system, ("echo pwned > /tmp/should_not_exist_isj",))
    raw = _npy({"x": 1})
    head, _ = raw[:128], raw[128:]
    evil = head + pickle.dumps(Evil())
    with pytest.raises(pickle.UnpicklingError):
        safe_npy.load_object_npy(evil)
    import os
    assert not os.path.exists("/tmp/should_not_exist_isj")
