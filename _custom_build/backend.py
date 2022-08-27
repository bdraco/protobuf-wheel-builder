import glob
import os
import re
import subprocess  # nosec
import sys
import tempfile
from typing import Dict, Optional

from setuptools import build_meta as _orig

prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_sdist = _orig.build_sdist


def get_requires_for_build_wheel(self, config_settings=None):  # type: ignore[no-untyped-def]
    return _orig.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(self, config_settings=None):  # type: ignore[no-untyped-def]
    return _orig.get_requires_for_build_sdist(config_settings)


def build_wheel(  # type: ignore[no-untyped-def]
    wheel_directory, config_settings, metadata_directory=None
):
    python_bin = sys.executable
    cpu_count = os.cpu_count() or 4
    version = os.environ.get("PROTOBUF_VERSION")
    if not version:
        import google.protobuf  # type: ignore[import]

        version = google.protobuf.__version__
    print(f"*** Building protobuf wheel for {version}")
    wheel_directory = os.path.abspath(wheel_directory)
    with tempfile.TemporaryDirectory(
        dir=os.path.expanduser("~")  # /tmp may be nonexecutable
    ) as tmp_dist_dir:
        run_command(
            f"git clone --depth 1 --branch v{version} https://github.com/protocolbuffers/protobuf {tmp_dist_dir}/protobuf"
        )
        run_command(f"cd {tmp_dist_dir}/protobuf && /bin/sh ./autogen.sh")
        run_command(f"cd {tmp_dist_dir}/protobuf && /bin/sh ./configure")
        run_command(f"cd {tmp_dist_dir}/protobuf && make -j{cpu_count}")
        with open(f"{tmp_dist_dir}/protobuf/python/setup.py", "r+") as f:
            text = f.read()
            text = re.sub("name='protobuf'", "name='protobuf-wheel-builder'", text)
            f.seek(0)
            f.write(text)
            f.close()

        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && MAKEFLAGS=-j{cpu_count} LD_LIBRARY_PATH=../src/.libs {python_bin} setup.py build --cpp_implementation --compile_static_extension"
        )
        run_command(
            f"cd {tmp_dist_dir}/protobuf/python && MAKEFLAGS=-j{cpu_count} LD_LIBRARY_PATH=../src/.libs {python_bin} setup.py bdist_wheel --cpp_implementation --compile_static_extension"
        )
        wheel_file = glob.glob(f"{tmp_dist_dir}/protobuf/python/dist/*.whl")[0]
        result_basename = os.path.basename(wheel_file)
        mutated_result_basename = result_basename.replace(
            "protobuf-", "protobuf-wheel-builder-"
        )
        target_dir = wheel_directory
        result_path = os.path.join(target_dir, mutated_result_basename)
        os.rename(wheel_file, result_path)
        print(f"*** Moved into file: {result_path}")
    print(f"*** Finished building wheel: {mutated_result_basename}")
    return mutated_result_basename


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
