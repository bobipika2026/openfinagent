#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenFinAgent 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取依赖
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="tradeflow-ai",
    version="0.1.0",
    author="OpenFinAgent Team",
    author_email="tradeflow@example.com",
    description="AI 量化交易助手 - 用自然语言写量化策略",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/tradeflow-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tradeflow=tradeflow.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
