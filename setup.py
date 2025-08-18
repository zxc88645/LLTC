"""Setup script for SSH AI Assistant."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ssh-ai-assistant",
    version="1.0.0",
    author="SSH AI Team",
    author_email="team@ssh-ai.com",
    description="A natural language SSH command execution assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ssh-ai/ssh-ai-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ssh-ai=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)