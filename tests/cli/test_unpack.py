from __future__ import annotations

from wheel._cli.unpack import unpack


def test_unpack(wheel_paths, tmp_path):
    """
    Make sure 'wheel unpack' works.
    This also verifies the integrity of our testing wheel files.
    """
    for wheel_path in wheel_paths:
        unpack(wheel_path, str(tmp_path))
