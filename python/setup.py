#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="live-dev-integration",
    version="1.0.0",
    description="Integrated Python tools for Ableton Live and Max for Live development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ALSE Development Team",
    author_email="dev@example.com",
    url="https://github.com/2nist/Live-Dev-Workspace",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pylive>=0.4.0",
        "python-osc>=1.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-timeout>=2.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
        ],
        "audio": [
            "mido>=1.3.0",
            "numpy>=1.24.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ableton live max-for-live m4l osc midi audio music production",
)
