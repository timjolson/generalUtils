from setuptools import setup, find_packages

name = 'generalUtils'

setup(
    name=name,
    version="0.5",
    packages = find_packages(),
    tests_require = ['pytest', 'PyQt5'],
)