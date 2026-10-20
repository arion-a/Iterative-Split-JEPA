"""Load a pickled object array from an untrusted .npy without executing arbitrary code: the pickle may only reference numpy's array
reconstruction classes; anything else raises."""

from __future__ import annotations

import io
import pickle

import numpy as np
import numpy.lib.format as fmt

_ALLOWED = {("numpy.core.multiarray", "_reconstruct"): np._core.multiarray._reconstruct, ("numpy._core.multiarray", "_reconstruct"): np._core.multiarray._reconstruct,
            ("numpy", "ndarray"): np.ndarray, ("numpy", "dtype"): np.dtype}


class _Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in _ALLOWED:
            return _ALLOWED[(module, name)]
        raise pickle.UnpicklingError(f"blocked global {module}.{name}")


def load_object_npy(raw: bytes):
    """raw = the bytes of a .npy file holding a 0-d object array. Returns the contained Python object."""
    f = io.BytesIO(raw)
    version = fmt.read_magic(f)
    shape, _, dtype = fmt.read_array_header_1_0(f) if version == (1, 0) else fmt.read_array_header_2_0(f)
    if dtype != np.dtype("O"):
        return np.load(io.BytesIO(raw), allow_pickle=False)
    out = _Restricted(f).load()
    return out.item() if isinstance(out, np.ndarray) and out.shape == () else out
