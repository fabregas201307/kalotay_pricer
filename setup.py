from setuptools import setup, find_packages, Extension
import os
import unittest
from KalotayNative import __version__, __kalotay_version__


setup(
    name='KalotayNative',
    version=__version__,
    packages=find_packages(include=["KalotayNative"]),
    python_requires='>=3.9.*',
    package_data={"KalotayNative": ["*.pyd", "*.dill", "*.so"]},
    include_package_data=True,
    url="",
    license="Internal",
    author="",
    author_email="",
    description="Kalotay pricer",
)

