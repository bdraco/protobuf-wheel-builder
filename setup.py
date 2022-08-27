#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

requirements = ["protobuf>=3.12.2,<4.0"]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="J. Nick Koston",
    author_email="nick@koston.org",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="Python library for building protobuf wheels",
    install_requires=requirements,
    license="Apache Software License 2.0",
    include_package_data=True,
    keywords="protobuf protobuf-wheel-builder",
    name="protobuf-wheel-builder",
    build_requires=[],
    packages=find_packages(include=["protobuf_wheel_builder"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/bdraco/protobuf-wheel-builder",
    version="1.2.2",
    zip_safe=False,
)
