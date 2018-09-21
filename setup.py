from setuptools import setup, find_packages
import logging

name = 'generalUtils'

import logging
logging.basicConfig(filename=f'.\install-{name}.log', level=logging.DEBUG)
logging.debug(find_packages())

setup(
    name=name,
    version="0.5",
    packages = find_packages(),
    install_requires = ['PyQt5'],
    tests_require = ['pytest'],
)