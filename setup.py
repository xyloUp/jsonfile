from setuptools import setup, find_packages

setup(
    name='jsonfile',
    version='0.1.0',
    packages=find_packages(include=["jsonfile", 'jsonfile.*']),
    test_suite="tests"
)