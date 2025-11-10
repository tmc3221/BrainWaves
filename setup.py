"""Setup configuration for BrainWaves."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="brainwaves",
    version="0.1.0",
    author="BrainWaves",
    description="Semantic word search to YouTube video discovery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmc3221/BrainWaves",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "brainwaves=brainwaves.cli:main",
        ],
    },
)
