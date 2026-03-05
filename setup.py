from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openfinagent",
    version="0.1.0",
    author="OpenFinAgent Team",
    author_email="hi@openfinagent.ai",
    description="🧬 金融 AI Agent 操作系统 - 用自然语言构建量化策略",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bobipika2026/openfinagent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "openfinagent=openfinagent.core:main",
        ],
    },
)
