# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Setup script for the RepoGuard distribution.
"""


from distutils import core
import os
import sys
import subprocess

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, command


_WIN32_CONFIG_HOME = os.path.join(os.path.expanduser("~"), ".repoguard")
_LINUX_CONFIG_HOME = "/usr/local/share/repoguard"
CONFIG_HOME = _WIN32_CONFIG_HOME if sys.platform == "win32" else _LINUX_CONFIG_HOME
CONFIG_HOME = os.getenv("REPOGUARD_CONFIG_HOME", CONFIG_HOME)
DEBUG = os.getenv("REPOGUARD_DEBUG")
_CONSOLE_SCRIPTS = "repoguard = repoguard.main:main"
if DEBUG: # Adds a debug prefix to allow test with new version without de-activating the old one
    _CONSOLE_SCRIPTS = "repoguard-debug = repoguard.main:main"


class doc(core.Command):
    """ Creates the developer documentation. """
    
    description = "Creates the developer documentation."
    user_options = [("command=", None, "Path and name of 'sphinx-build' command. Default: sphinx-build"),
                     ("destdir=", None, "Path to directory which should contain the documentation.")]
    _COMMAND_TEMPLATE = "{0} doc/source doc/html"

    
    def __init__(self, distribution):
        self.verbose = None
        self.command = None

        core.Command.__init__(self, distribution)

    def initialize_options(self):
        self.verbose = False
        self.command = "sphinx-build"
        if sys.platform == "win32":
            self.command += ".exe"

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        
    def run(self):
        command = self._COMMAND_TEMPLATE.format(self.command )
        if self.verbose:
            print(command)
        subprocess.call(command)

setup(
    name="repoguard", 
    version="0.3.0-dev",
    cmdclass={"doc": doc},
    description="RepoGuard is a framework for Subversion hook scripts.",
    long_description="RepoGuard is a framework for Subversion pre-commit hooks in order to implement checks of the to be commited files before they are commited. For example, you can check for the code style or unit tests. The output of the checks can be send by mail or be written into a file or simply print to the console..",
    author="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
    author_email="Malte.Legenhausen@dlr.de",
    maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
    maintainer_email="tobias.schlauch@dlr.de",
    url="http://repoguard.tigris.org",
    classifiers=[
        "Development Status :: 1 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Version Control",
    ],
    namespace_packages=[
        "repoguard",
        "repoguard.checks",
        "repoguard.handlers",
        "repoguard.modules",
        "repoguard.tools"
    ],
    packages=find_packages("src", exclude=["*.tests", "*.testutil"]),
    package_dir={
        "" : "src"
    },
    data_files=[
        (CONFIG_HOME, [
            "cfg/repoguard.conf",
            "cfg/logger.conf"
        ]),
        ("cfg/templates", [
            "cfg/templates/default.tpl.conf",
            "cfg/templates/python.tpl.conf"
        ])
    ],
    install_requires=[
        "configobj>=4.6.0",
        "setuptools"
    ],
    extras_require={
        "dev" : [
            "Sphinx>=1.1.2",
            "pylint>=0.18.1",
            "pytest>=2.2.3"
        ],
        "pylint" : [
            "pylint>=0.18.1"
        ],
        "mantis" : [
            "suds-jurko>=0.4.1"
        ],
        "buildbot" : [
            "twisted>=8.1.0"
        ]
    },
    entry_points={
        "console_scripts": [
            _CONSOLE_SCRIPTS
        ],
        "repoguard.checks" : [
            "AccessRights = repoguard.checks.accessrights:AccessRights",
            "ASCIIEncoded = repoguard.checks.asciiencoded:ASCIIEncoded",
            "CaseInsensitiveFilenameClash = repoguard.checks.caseinsensitivefilenameclash:CaseInsensitiveFilenameClash",
            "Checkout = repoguard.checks.checkout:Checkout",
            "Checkstyle = repoguard.checks.checkstyle:Checkstyle",
            "Keywords = repoguard.checks.keywords:Keywords",
            "Log = repoguard.checks.log:Log",
            "Mantis = repoguard.checks.mantis [mantis]",
            "PyLint = repoguard.checks.pylint_:PyLint [pylint]",
            "RejectTabs = repoguard.checks.rejecttabs:RejectTabs",
            "UnitTests = repoguard.checks.unittests:UnitTests",
            "XMLValidator = repoguard.checks.xmlvalidator:XMLValidator"
        ],
        "repoguard.handlers" : [
            "Mail = repoguard.handlers.mail:Mail",
            "Console = repoguard.handlers.console:Console",
            "File = repoguard.handlers.file:File",
            "Mantis = repoguard.handlers.mantis:Mantis [mantis]",
            "BuildBot = repoguard.handlers.buildbot:BuildBot [buildbot]",
            "Hudson = repoguard.handlers.hudson:Hudson",
            "ViewVC = repoguard.handlers.viewvc:ViewVC"
        ],
        "repoguard.tools" : [
            "Checker = repoguard.tools.checker:Checker",
            "Configuration = repoguard.tools.config:Configuration",
            "Repository = repoguard.tools.repository:Repository"
        ]
    }
)
