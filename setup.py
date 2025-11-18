"""Setup script for Tandem Mobi Insulin Pump Simulator."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    """Read a file and return its contents."""
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements from requirements.txt
def read_requirements(filename):
    """Read requirements from a file."""
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="tandem-simulator",
    version="0.1.0",
    author="Tandem Simulator Project",
    description="BLE simulator for Tandem Mobi insulin pump",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/jwoglom/tandem-simulator",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "tandem-simulator=simulator:main",
        ],
    },
    include_package_data=True,
)
