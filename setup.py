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
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.8',
    data_files=[
        ('',
            [
                'chp_look_up/app_meta_data/conflation_map.json',
                'chp_look_up/app_meta_data/curies.json',
                'chp_look_up/app_meta_data/meta_knowledge_graph.json',
                ]
            )
        ],
    package_data={'chp_look_up': ['app_meta_data/conflation_map.json', 'app_meta_data/curies.json', 'app_meta_data/meta_knowledge_graph.json']},
    dependency_links=[
    ]
)

