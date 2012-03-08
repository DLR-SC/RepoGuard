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
import setuptools


_WIN32_CONFIG_HOME = os.path.join(os.path.expanduser("~"), ".repoguard")
_LINUX_CONFIG_HOME = "/usr/local/share/repoguard"
CONFIG_HOME = _WIN32_CONFIG_HOME if sys.platform == "win32" else _LINUX_CONFIG_HOME
CONFIG_HOME = os.getenv("REPOGUARD_CONFIG_HOME", CONFIG_HOME)
DEBUG = os.getenv("REPOGUARD_DEBUG")
_CONSOLE_SCRIPTS = "repoguard = repoguard.main:main"
if DEBUG: # Adds a debug prefix to allow test with new version without de-activating the old one
    _CONSOLE_SCRIPTS = "repoguard-debug = repoguard.main:main"


class _pylint(core.Command):
    """ Runs the pylint command. """

    _COMMAND_TEMPLATE = "{0} --rcfile=pylintrc --output-format={1} src/repoguard test/repoguard_test > {2}"

    description = "Runs the pylint command."
    user_options = [
        ("command=", None, "Path and name of the pylint command line tool. Default: pylint"),
        ("out=", None, "Specifies the output type (html or parseable). Default: html")]

    def initialize_options(self):
        self.verbose = False
        self.command = "pylint"
        if sys.platform == "win32":
            self.command += ".bat"
        self.out = "html"
        self.output_file_path = "pylint.html"
        python_path = [os.path.realpath(path) for path in ["src", "test"]]
        os.environ["PYTHONPATH"] = os.pathsep.join(python_path)

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        if self.out != "html":
            self.output_file_path = "pylint.txt"

    def run(self):
        command = self._COMMAND_TEMPLATE.format(self.command, self.out, self.output_file_path)
        if self.verbose:
            print(command)
        subprocess.call(command)
        
        self._correct_path_delimiter()

    def _correct_path_delimiter(self):
        if self.out != "html" and sys.platform == "win32":
            with open(self.output_file_path, "rb") as file_object:
                content = file_object.read().replace("\\", "/")
            with open(self.output_file_path, "wb") as file_object:
                file_object.write(content)


class test(core.Command):
    """ Runs all unit tests. """
    
    description = "Runs all unit tests using py.test."
    user_options = [
        ("command=", None, "Path and name of the pytest command line tool. Default: py.test"),
        ("out=", None, "Specifies the output format of the test results." \
         + "Formats: xml, standard out. Default: standard out."),
        ("covout=", None, "Specifies the output format of the coverage report." \
         + "Formats: xml, html.")]


    def __init__(self, distribution):
        core.Command.__init__(self, distribution)

    def initialize_options(self):
        self.command = "py.test"
        self.out = None
        if sys.platform == "win32":
            self.command += ".exe"
        self.covout = None
        self.verbose = False

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        
    def run(self):
        if self.out == "xml":
            options = "--junitxml=./xunit.xml test"
        else:
            options = " test"
        
        if not self.covout is None:
            options = "--cov=src --cov-report={0} {1}".format(self.covout, options)

        command = "{0} {1}".format(self.command, options)
        if self.verbose:
            print(command)
        subprocess.call(command)


class audit(core.Command):
    """ Runs pylint for coding standards compliance check 
    and determines the code coverage. """

    description = "Runs pylint for coding standards compliance check and determines the code coverage."
    user_options = [("out=", None, "Specifies the output type (user readable or ci). Default: user readable")]
    sub_commands = [("_pylint", None), ("test", None)]

    def __init__(self, distribution):
        core.Command.__init__(self, distribution)
        
    def initialize_options(self):
        self.verbose = False
        self.out = None
    
    def finalize_options(self):
        self.verbose = self.distribution.verbose

    def run(self):
        self._set_sub_command_options()
        for command_name in self.get_sub_commands():
            self.run_command(command_name)
    
    def _set_sub_command_options(self):
        test_options = self.distribution.get_option_dict("test")
        pylint_options = self.distribution.get_option_dict("_pylint")
        if self.out is None:
            test_options["out"] = ("", None)
            test_options["covout"] = ("", "html")
            pylint_options["out"] = ("", "html")
        else:
            test_options["out"] = ("", "xml")
            test_options["covout"] = ("", "xml")
            pylint_options["out"] = ("", "parseable")
    

class doc(core.Command):
    """ Creates the developer documentation. """
    
    description = "Creates the developer documentation."
    user_options = [("command=", None, "Path and name of 'sphinx-build' command. Default: sphinx-build"),
                     ("destdir=", None, "Path to directory which should contain the documentation.")]
    _COMMAND_TEMPLATE = "{0} doc/source doc/html"

    
    def __init__(self, distribution):
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

setuptools.setup(
    name="repoguard", 
    version="0.3.0-dev",
    cmdclass={"doc": doc, "test": test, "_pylint": _pylint, "audit": audit},
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
    packages=setuptools.find_packages("src", exclude=["*.tests", "*.testutil"]),
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
            "pytest>=2.2.3",
            "pytest-cov>=1.5" 
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
