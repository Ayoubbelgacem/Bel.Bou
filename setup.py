from setuptools import setup, find_packages

setup(
    name="boubel-lang",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "llvmlite",
        "toml",
    ],
    entry_points={
        'console_scripts': [
            'boubel=main:main',
        ],
    },
    author="Bou.Bel Team",
    description="Bou.Bel - Tunisian Arabic Programming Language",
    license="MIT",
    python_requires=">=3.8",
)