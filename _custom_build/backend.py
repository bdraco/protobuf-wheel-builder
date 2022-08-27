import glob
import os
import subprocess  # nosec
import sys
import tempfile
from typing import Dict, Optional

from setuptools import build_meta as _orig

prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_sdist = _orig.build_sdist
get_requires_for_build_wheel = _orig.get_requires_for_build_wheel
get_requires_for_build_sdist = _orig.get_requires_for_build_sdist


def build_wheel(  # type: ignore[no-untyped-def]
    self, wheel_directory, config_settings, metadata_directory=None
):
    with tempfile.TemporaryDirectory(dir=wheel_directory) as tmp_dist_dir:
        run_command(
            f"git clone --depth 1 --branch v3.20.1 https://github.com/protocolbuffers/protobuf {tmp_dist_dir}/protobuf"
        )
        run_command(f"cd {tmp_dist_dir}/protobuf && ./autogen.sh")
        run_command(f"cd {tmp_dist_dir}/protobuf && ./configure")
        run_command(f"cd {tmp_dist_dir}/protobuf && make -j4")
        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && LD_LIBRARY_PATH=../src/.libs python setup.py build --cpp_implementation"
        )
        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && LD_LIBRARY_PATH=../src/.libs python setup.py bdist_wheel --cpp_implementation"
        )
        wheel_file = glob.glob(f"{tmp_dist_dir}/protobuf/python/dist/*.whl")[0]
        result_basename = os.path.basename(wheel_file)
        result_path = os.path.join(wheel_directory, result_basename)
        os.rename(wheel_file, result_path)
        return result_basename


def run_command(
    cmd: str, env: Optional[Dict[str, str]] = None, timeout: Optional[int] = None
) -> None:
    """Implement subprocess.run but handle timeout different."""
    subprocess.run(
        cmd,
        shell=True,  # nosec
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
        timeout=timeout,
    )