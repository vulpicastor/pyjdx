"""A setuptools based pyjdx setup module.

Author: Lizhou Sha <slz@mit.edu>
"""

from setuptools import setup, find_packages

setup(
    name="pyjdx",
    version="0.0.0",

    description="A reader of JCAMP-DX spectral data files",
    keywords="spectroscopy chemistry astronomy atmospheric planetary science",
    url="https://github.com/vulpicastor/pyjdx",

    author="Lizhou Sha",
    author_email="slz@mit.edu",
    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4"
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=["numpy"]
)
