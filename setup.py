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
                os.path.join("src", app + ".py"),
                arcname=os.path.join(app, "bin", app + ".py")
            )

            spl.add(
                os.path.join("examples", app, "default", "app.conf"),
                arcname=os.path.join(app, "default", "app.conf")
            )
            spl.add(
                os.path.join("examples", app, "README", "inputs.conf.spec"),
                arcname=os.path.join(app, "README", "inputs.conf.spec")
            )

            splunklib_files = self.get_python_files(os.listdir(splunklib_arcname))
            for file_name in splunklib_files:
                spl.add(
                    os.path.join(splunklib_arcname, file_name),
                    arcname=os.path.join(app, "bin", splunklib_arcname, file_name)
                )

            modinput_files = self.get_python_files(os.listdir(modinput_dir))
            for file_name in modinput_files:
                spl.add(
                    os.path.join(modinput_dir, file_name),
                    arcname=os.path.join(app, "bin", modinput_dir, file_name)
                )

            spl.close()

        # Create searchcommands_app-<three-part-version-number>-private.tar.gz

        setup_py = os.path.join('examples', 'searchcommands_app', 'setup.py')

        check_call(('python', setup_py, 'build', '--force'), stderr=STDOUT, stdout=sys.stdout)
        tarball = 'searchcommands_app-{0}-private.tar.gz'.format(self.distribution.metadata.version)
        source = os.path.join('examples', 'searchcommands_app', 'build', tarball)
        target = os.path.join('build', tarball)

        shutil.copyfile(source, target)
        return

setup(
    author="Julien Ruaux",
    author_email="jruauxNOSPAM@splunk.com",
    cmdclass={ 'dist': DistCommand},
    description="Splunk Modular Input for NDBC Observations.",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    name="ta-ndbc",
    packages=["ndbc"],
    url="http://github.com/jruaux/TA-NDBC",
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
