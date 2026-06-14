#! /Users/albert/anaconda3/envs/sklearn-env/bin/python3.13
import setuptools  # noqa; we are using a setuptools namespace
# from numpy.distutils.core import setup
from setuptools import setup, Extension

descr = """SCA Replication"""

DISTNAME = 'sca-REPLICATION'
DESCRIPTION = descr
MAINTAINER = 'Albert Liang'
MAINTAINER_EMAIL = 'albert.liang.ca@gmail.com'
LICENSE = 'MIT License'
DOWNLOAD_URL = 'https://github.com/AlbertLiangca/sca_REPLICATION.git'
VERSION = '0.0.2.dev'


if __name__ == "__main__":
    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.md').read(),
          long_description_content_type= 'text/markdown',
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS',
          ],
          platforms='any',
          packages=['sca'],
          install_requires=['numpy','scipy','scikit-learn','matplotlib']
          )