import os
import sys
import re
import io

from setuptools import find_packages
from setuptools import setup

__version__ = re.search(r'__version__\s*=\s*[\'"]([0-9]*\.[0-9]*\.[0-9]*)[\'"]',
                        io.open('chp_look_up/_version.py', encoding='utf_8_sig').read()).group(1)

REQUIRED_PACKAGES = [
]

setup(
    name='chp_look_up',
    version='1.0',
    author='Luke Veenhuis',
    author_email='luke.j.veenhuis@dartmouth.edu',
    description='Simple one hop database lookup service for NCATS Connections Hypothesis Provider',
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.8',
    dependency_links=[
    ]
)

