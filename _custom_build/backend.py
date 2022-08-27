import glob
import os
import subprocess  # nosec
import sys
import tempfile
from typing import Dict, Optional

from setuptools import build_meta as _orig

prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_sdist = _orig.build_sdist

VERSION = "3.20.1"


def get_requires_for_build_wheel(self, config_settings=None):  # type: ignore[no-untyped-def]
    return _orig.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(self, config_settings=None):  # type: ignore[no-untyped-def]
    return _orig.get_requires_for_build_sdist(config_settings)


def build_wheel(  # type: ignore[no-untyped-def]
    wheel_directory, config_settings, metadata_directory=None
):
    python_bin = sys.executable
    cpu_count = os.cpu_count() or 4
    wheel_directory = os.path.abspath(wheel_directory)
    with tempfile.TemporaryDirectory(dir=wheel_directory) as tmp_dist_dir:
        run_command(
            f"git clone --depth 1 --branch v{VERSION} https://github.com/protocolbuffers/protobuf {tmp_dist_dir}/protobuf"
        )
        run_command(f"cd {tmp_dist_dir}/protobuf && ./autogen.sh")
        run_command(f"cd {tmp_dist_dir}/protobuf && ./configure")
        run_command(f"cd {tmp_dist_dir}/protobuf && make -j{cpu_count}")
        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && MAKEFLAGS=-j{cpu_count} LD_LIBRARY_PATH=../src/.libs {python_bin} setup.py build --cpp_implementation"
        )
        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && MAKEFLAGS=-j{cpu_count} LD_LIBRARY_PATH=../src/.libs {python_bin} setup.py bdist_wheel --cpp_implementation"
        )
        wheels = glob.glob(f"{tmp_dist_dir}/protobuf/python/dist/*.whl")[0]
        wheel_file = wheels[0]
        result_basename = os.path.basename(wheel_file)
        target_dir = wheel_directory
        result_path = os.path.join(target_dir, result_basename)
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
