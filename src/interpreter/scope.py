from setuptools import setup, find_packages

setup(
    name="boubel",
    version="2.0.0",
    description="Bou.Bel - Tunisian Arabic Programming Language",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'boubel=main:main',
        ],
    },
)