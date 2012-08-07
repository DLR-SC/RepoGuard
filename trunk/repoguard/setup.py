# See the file "LICENSE" for the full license governing this code.


"""
Setup script for the RepoGuard distribution.
"""


from __future__ import with_statement
from distutils.command import clean as _clean
from distutils import core
import os
import subprocess
import shutil
import sys

from distribute_setup import use_setuptools
use_setuptools()
import setuptools


class clean(_clean.clean):
    """ Little clean extension: Cleans up a non-empty build directory. """
    
    def run(self):
        for path in ["build", "doc/html", "doc/doctrees", "dist", 
                     "src/repoguard.egg-info", ".coverage", "coverage.xml"]:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)


class _BaseCommandRunner(core.Command):
    """ Base class for encapsulating command line commands. """
    
    def run(self):
        self._create_build_dir()
        command = self._create_command()
        self._run_command(command)
        self._perform_post_actions()
    
    @staticmethod
    def _create_build_dir():
        if not os.path.exists("build"):
            os.mkdir("build")

    def _create_command(self):
        pass
    
    def _run_command(self, command):
        if self.verbose:
            print(command)
        subprocess.call(command, shell=True)
    
    def _perform_post_actions(self):
        pass


class pylint(_BaseCommandRunner):
    """ Runs the pylint command. """

    description = "Runs the pylint command."
    user_options = [
        ("command=", None, "Path and name of the command line tool."),
        ("out=", None, "Specifies the output type (html, parseable). Default: html")]

    def initialize_options(self):
        self.command = "pylint"
        if sys.platform == "win32":
            self.command += ".bat"
        self.out = "html"
        self.output_file_path = "build/pylint.html"

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        if self.out == "parseable":
            self.output_file_path = "build/pylint.txt"

    def _create_command(self):
        return (
            "%s --rcfile=dev/pylintrc --output-format=%s src/repoguard test/repoguard_test > %s"
            % (self.command, self.out, self.output_file_path))

    def _perform_post_actions(self):
        if self.out == "parseable" and sys.platform == "win32":
            with open(self.output_file_path, "rb") as file_object:
                content = file_object.read().replace("\\", "/")
            with open(self.output_file_path, "wb") as file_object:
                file_object.write(content)
                

class test(_BaseCommandRunner):
    """ Runs all unit tests. """
    
    description = "Runs all unit tests using py.test."
    user_options = [
        ("command=", None, "Path and name of the command line tool."),
        ("out=", None, "Specifies the output format of the test results." \
         + "Formats: xml, standard out. Default: standard out."),
        ("covout=", None, "Specifies the output format of the coverage report." \
         + "Formats: xml, html.")]

    def initialize_options(self):
        self.command = "py.test"
        if sys.platform == "win32":
            self.command += ".exe"
        self.out = None
        self.covout = None

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        
    def _create_command(self):
        options = " test"
        if self.out == "xml":
            options = "--junitxml=build/xunit.xml test"
        if not self.covout is None:
            options = (
                "--cov=src --cov-config=dev/coveragerc --cov-report=%s %s"
                % (self.covout, options))
        return "%s %s" % (self.command, options)


def _perform_setup():
    _set_pythonpath()
    config_home = _get_config_home()
    console_scripts = _get_console_scripts()
    install_requires, extras_require = _get_requirements()
    _run_setup(config_home, console_scripts, install_requires, extras_require)
    
def _set_pythonpath():
    python_path = [os.path.realpath(path) for path in ["src", "test"]]
    os.environ["PYTHONPATH"] = os.pathsep.join(python_path)

def _get_config_home():
    win32_config_home = os.path.join(os.path.expanduser("~"), ".repoguard")
    linux_config_home = "/usr/local/share/repoguard"
    config_home = win32_config_home if sys.platform == "win32" else linux_config_home
    config_home = os.getenv("REPOGUARD_CONFIG_HOME", config_home)
    return config_home

def _get_console_scripts():
    debug = os.getenv("REPOGUARD_DEBUG")
    console_scripts = "repoguard = repoguard.main:main"
    if debug: # Adds a debug prefix to allow test with a new version without de-activating the old one
        console_scripts = "repoguard-debug = repoguard.main:main"
    return console_scripts

def _get_requirements():
    extras_require = dict()
    install_requires = list()
    for name in os.listdir("requires"):
        if name == "requires.txt":
            install_requires = (_read_requirements_from_file("requires/" + name))
        elif name.startswith("requires"):
            extras_name = name[9:-4]
            extras_require[extras_name] = _read_requirements_from_file("requires/" + name)
    return install_requires, extras_require

def _read_requirements_from_file(path):
    with open(path, "rb") as file_object:
        return file_object.read().splitlines()

def _run_setup(config_home, console_scripts, install_requires, extras_require):
    _write_config_home_constant(config_home)
    setuptools.setup(
        name="repoguard", 
        version="0.3.0",
        cmdclass={"clean": clean, "test": test, "pylint": pylint},
        description="RepoGuard is a framework for Subversion hook scripts.",
        long_description=("RepoGuard is a framework for Subversion pre-commit hooks " 
            + "in order to implement checks of the to be commited files before they are committed."
            + " For example, you can check for the code style or unit tests. The output of the checks" 
            + " can be send by mail or be written into a file or simply print to the console."),
        author="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        author_email="Malte.Legenhausen@dlr.de",
        maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        maintainer_email="tobias.schlauch@dlr.de",
        license="Apache License Version 2.0",
        url="http://repoguard.tigris.org",
        platforms=["Linux", "Unix", "Windows"],
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
        packages=setuptools.find_packages("src"),
        package_dir={"" : "src"},
        data_files=[
            (config_home, [
                "cfg/repoguard.conf",
                "cfg/logger.conf"
            ]),
            (config_home, [
                "cfg/templates/default.tpl.conf",
                "cfg/templates/python.tpl.conf"
            ])
        ],
        install_requires=install_requires,
        extras_require=extras_require,
        entry_points={
            "console_scripts": [
                console_scripts
            ],
            "repoguard.checks": [
                "AccessRights = repoguard.checks.accessrights:AccessRights",
                "ASCIIEncoded = repoguard.checks.asciiencoded:ASCIIEncoded",
                "CaseInsensitiveFilenameClash = repoguard.checks.caseinsensitivefilenameclash:CaseInsensitiveFilenameClash",
                "Checkout = repoguard.checks.checkout:Checkout",
                "Checkstyle = repoguard.checks.checkstyle:Checkstyle",
                "Keywords = repoguard.checks.keywords:Keywords",
                "Log = repoguard.checks.log:Log",
                "Mantis = repoguard.checks.mantis:Mantis [mantis]",
                "PyLint = repoguard.checks.pylint_:PyLint [pylint]",
                "RejectTabs = repoguard.checks.rejecttabs:RejectTabs",
                "UnitTests = repoguard.checks.unittests:UnitTests",
                "XMLValidator = repoguard.checks.xmlvalidator:XMLValidator"
            ],
            "repoguard.handlers": [
                "Mail = repoguard.handlers.mail:Mail",
                "Console = repoguard.handlers.console:Console",
                "File = repoguard.handlers.file:File",
                "Mantis = repoguard.handlers.mantis:Mantis [mantis]",
                "BuildBot = repoguard.handlers.buildbot:BuildBot [buildbot]",
                "Hudson = repoguard.handlers.hudson:Hudson",
                "ViewVC = repoguard.handlers.viewvc:ViewVC"
            ],
            "repoguard.tools": [
                "Checker = repoguard.tools.checker:Checker",
                "Configuration = repoguard.tools.config:Configuration",
                "Repository = repoguard.tools.repository:Repository"
            ]
        }
    )

def _write_config_home_constant(config_home):
    constants_file_path = "src/repoguard/core/constants.py"
    with open(constants_file_path, "rb") as file_object:
        content = list()
        for line in file_object.readlines():
            if line.startswith("CONFIG_HOME ="):
                content.append("CONFIG_HOME = \"%s\"\n" % config_home)
            else:
                content.append(line)
    with open(constants_file_path, "wb") as file_object:
        file_object.write("".join(content))


if __name__ == "__main__":
    _perform_setup()
