import os
import sys
import re
import io

from setuptools import find_packages
from setuptools import setup

__version__ = '1.0'

REQUIRED_PACKAGES = [
]

setup(
    name='chp_look_up',
    version=__version__,
    author='Luke Veenhuis',
    author_email='luke.j.veenhuis@dartmouth.edu',
    description='Simple one hop database lookup service for NCATS Connections Hypothesis Provider',
    packages=       ['chp_look_up',
                    'chp_look_up.app'
                    'chp_look_up.migrations'],
    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.8',
    dependency_links=[
    ]
)

