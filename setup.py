#!/usr/bin/env python3
"""
Setup configuration for Personal SSH/SCP CLI System Manager
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="personal-ssh-cli",
    version="1.0.0",
    author="Personal Use",
    description="Advanced Personal SSH/SCP CLI System Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elliotttmiller/System-Manager",
    packages=find_packages(where="personal-ssh-cli"),
    package_dir={"": "personal-ssh-cli"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pssh=core.cli_engine:main",
            "personal-ssh=core.cli_engine:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
