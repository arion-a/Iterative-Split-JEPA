"""The discovery path must not know physics: its modules contain no physics tokens."""
import os
import re

SRC = os.path.join(os.path.dirname(__file__), "..", "src", "isj")
DISCOVERY = ["video_io.py", "video_encoder.py", "temporal_ladder.py", "real_video_io.py", "pipeline.py"]
FORBIDDEN = re.compile(r"theta|omega|energy|audit|pendulum|angle|momentum", re.I)


def test_discovery_modules_have_no_physics_tokens():
    for name in DISCOVERY:
        p = os.path.join(SRC, name)
        if not os.path.exists(p):
            continue
        hits = FORBIDDEN.findall(open(p).read())
        assert not hits, f"{name}: {hits[:5]}"
