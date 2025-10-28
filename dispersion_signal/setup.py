"""
Dispersion Signal 데이터 수집기 설치 스크립트
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dispersion-signal-collector",
    version="1.0.0",
    author="Dispersion Signal Team",
    author_email="team@dispersionsignal.com",
    description="암호화폐 온체인 데이터 수집기",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/dispersion-signal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
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
            "dispersion-collector=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
