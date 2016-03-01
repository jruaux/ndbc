#!/usr/bin/env python

from setuptools import setup, Command
from contextlib import closing
from subprocess import check_call, STDOUT

import os
import sys
import shutil
import tarfile

import splunklib


class DistCommand(Command):
    """setup.py command to create .spl file for modular input"""
    description = "Build NDBC modular input tarballs."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def get_python_files(files):
        """Utility function to get .py files from a list"""
        python_files = []
        for file_name in files:
            if file_name.endswith(".py"):
                python_files.append(file_name)
        return python_files

    def run(self):
        app = 'ndbc'
        splunklib_arcname = "splunklib"
        modinput_dir = os.path.join(splunklib_arcname, "modularinput")

        if not os.path.exists("build"):
            os.makedirs("build")

        with closing(tarfile.open(os.path.join("build", app + ".spl"), "w")) as spl:

            spl.add(
                "src",
                arcname=os.path.join(app, "bin")
            )

            spl.add(
                "default",
                arcname=os.path.join(app, "default")
            )

            spl.add(
                "README",
                arcname=os.path.join(app, "README")
            )
            spl.add(
                "static",
                arcname=os.path.join(app, "static")
            )

            spl.close()

        return

setup(
    author="Julien Ruaux",
    author_email="jruauxNOSPAM@splunk.com",
    cmdclass={ 'dist': DistCommand},
    description="Splunk Modular Input for NDBC Observations.",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    name="ta-ndbc",
    packages=["ndbc"],
    url="http://github.com/jruaux/ndbc",
    version=1.0,
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Splunk Users",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)
