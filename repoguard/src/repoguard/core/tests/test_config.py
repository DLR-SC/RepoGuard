#
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
Test methods of the C{Config} class.
"""


import os
import tempfile

import py.test

from repoguard.core import config
from repoguard.core import constants
from repoguard.core.config import ProjectConfig, RepoGuardConfig, Process


_REPOGUARD_CONFIG = """
template_dirs = %s,
validate = False

[projects]
    [[RepoGuard]]
    path = %s
    editors = lege_ma,
"""


_DEFAULT_CONFIG = """
[profiles]
    [[default]]
        [[[precommit]]]
        success = Console,
        error = Console,
"""


_PYTHON_CONFIG = """
extends = default

[DEFAULT]
    pythonhome = C:/Python25

[profiles]
    [[default]]
        [[[precommit]]]
        checks = PyLint.default.delayonerror,
        
[checks]
    [[PyLint]]
        [[[default]]]
        check_files = .*\.py,
"""


_PROJECT_CONFIG = """
extends = python
vcs = svn

[DEFAULT]
    pythonhome = D:/python25

[profiles]
    [[test]]
        regex = ^.*/test/.*$
        [[[precommit]]]
            default = abortonerror
            checks = PyLint.default.delayonerror, PyLint.default
            success = Console.default,
            error = Console.default,
    
    [[default]]
        [[[precommit]]]
            default = abortonerror
            checks = PyLint.default,
            success = Console,
            error = Console, File.default

[handlers]
    [[File]]
        [[[default]]]
            file = ${hooks}/default.log
    [[Mail]]
        [[[default]]]
            addresses = all@test.com,
[checks]
    [[PyLint]]
        [[[default]]]
            ignore_files = .*test_[\w]+\.py,
""".splitlines()


class _RequirementMock(object):
    """ Mocks the class L{Requirement<pkg_resources.Requirement>} """
    
    def __init__(self):
        """ Simple constructor which dies effectively nothing at all. """
    
        self.path = None
    
    @classmethod
    def parse(cls, name):
        """ Mocks the parse method and just returns the given argument. """
        
        cls.path = name
        return cls


def _resource_filename_mock(requirement, path):
    """ 
    Mocks the function he class L{resource_filename<pkg_resources.resource_filename>}.
    Joins the C{path} property of C{RequirementMock} with C{path} using the "/" character. 
    """
    
    return requirement.path + "/"  + path

# Activates the mocks for pkg_resources functions.
config.Requirement = _RequirementMock
config.resource_filename = _resource_filename_mock
os.listdir = lambda _: [u"default.tpl.conf", u"python.tpl.conf"] # Required to make _get_templates work


class TestRepoGuardConfig(object):
    """ Tests the repo guard specfic configuration. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          "default.tpl.conf")
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          "python.tpl.conf")
        fp = open(cls.defaulttplfile, "w")
        fp.write(_DEFAULT_CONFIG)
        fp.close()
        
        fp = open(cls.pythontplfile, "w")
        fp.write(_PYTHON_CONFIG)
        fp.close()
        
        cls.projectdir = tempfile.mkdtemp()
        cls.hooksdir = os.path.join(cls.projectdir, "hooks")
        os.mkdir(cls.hooksdir)
        
        cls.configfile = os.path.join(cls.hooksdir, constants.CONFIG_FILENAME)
        config = (_REPOGUARD_CONFIG % (cls.templatedir, cls.projectdir))
        
        cls.config = RepoGuardConfig(config.splitlines())
        
    def test_projects(self):
        """ Tests C{projects} property. """
        
        assert self.config.projects["RepoGuard"].name == "RepoGuard"
        
    def test_templates(self):
        """ Tests C{templates} property. """
        
        assert [u"default", u"python"] == self.config.templates.keys()
    
    def test_template_dirs(self):
        """ Tests C{template_dirs} property. """
        
        assert self.config.template_dirs == [self.templatedir, "repoguard/cfg/templates"]
        
    def test_validate(self):
        """ Tests validation method. """
        
        assert not self.config.validate


class TestProjectConfig(object):
    """ Tests the project-specific configuration. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          "default.tpl.conf")
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          "python.tpl.conf")
        fp = open(cls.defaulttplfile, "w")
        fp.write(_DEFAULT_CONFIG)
        fp.close()
        
        fp = open(cls.pythontplfile, "w")
        fp.write(_PYTHON_CONFIG)
        fp.close()
        
        cls.config = ProjectConfig(_PROJECT_CONFIG, "hooks", [cls.templatedir])
        
    def test_extended(self):
        """ Tests C{extended} property. """
        
        assert "python" in self.config.extended.keys()
        
    def test_vcs(self):
        """ Tests C{vcs} property. """
        
        assert self.config.vcs == "svn"

    def test_hook(self):
        """ Tests C{hooks} property. """
                
        assert self.config["DEFAULT"].get("hooks") == "hooks"
        
        path = self.config["handlers"]["File"]["default"]["file"]
        assert path == "hooks/default.log"
        
    def test_properties(self):
        """ Tests C{properties} property. """
        
        assert self.config.properties["pythonhome"] == "D:/python25"
        
    def test_profiles(self):
        """ Tests C{profiles} property. """
        
        default, test = self.config.profiles
        
        assert default.name == "default"
        assert default.regex is None
        assert default.precommit is not None
        assert default.postcommit is None
        
        assert test.name == "test"
        assert test.regex == "^.*/test/.*$"
        assert test.precommit is not None
        assert test.postcommit is None
        
        precommit = self.config["profiles"]["default"]["precommit"]
        assert precommit["checks"][0] == "PyLint.default"
        assert precommit["success"][0] == "Console"
        
    def test_process(self):
        """ Tests configuration processing. """
        
        default, test = self.config.profiles
        
        assert len(test.precommit.checks) == 2
        
        process = default.precommit
        name, config, interp = process.checks[0]
        assert name == "PyLint"
        assert config["check_files"] == [".*\\.py"]
        assert interp == constants.ABORTONERROR
                
        assert default.postcommit is None


class TestProcess(object):
    """ Checks process section of the configuration. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          "default.tpl.conf")
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          "python.tpl.conf")
        fp = open(cls.defaulttplfile, "w")
        fp.write(_DEFAULT_CONFIG)
        fp.close()
        
        fp = open(cls.pythontplfile, "w")
        fp.write(_PYTHON_CONFIG)
        fp.close()
        
        cls.projectdir = tempfile.mkdtemp()
        cls.hooksdir = os.path.join(cls.projectdir, "hooks")
        os.mkdir(cls.hooksdir)
        
        cls.configfile = os.path.join(cls.hooksdir, constants.CONFIG_FILENAME)
        
        cls.config = ProjectConfig(_PROJECT_CONFIG, "hooks", [cls.templatedir])
        cls._profile = cls.config.profile("default")
        
    def test_set_process(self):
        """ Tests setting the process section. """
        
        process = Process(self._profile, self._profile.depth, self.config)
        process.checks = [("PyLint", "default", constants.DELAYONERROR),
                          ("PyLint", "default", None),
                          ("PyLint", None, constants.WARNING),
                          ("PyLint", None, None)]
        process.success = [("File", "default"), ("File", None)]
        
        self._profile.precommit = process
        checks = self.config["profiles"]["default"]["precommit"]["checks"]
        assert checks == ["PyLint.default." + constants.DELAYONERROR, 
                          "PyLint.default", 
                          "PyLint.." + constants.WARNING, 
                          "PyLint"]
        
        success = self.config["profiles"]["default"]["precommit"]["success"]
        assert success == ["File.default", "File"]
        
        process = Process(self._profile, self._profile.depth, self.config)
        py.test.raises(KeyError, process._set_checks, 
                       [("PyLint", "notexists", None)])
        py.test.raises(KeyError, process._set_success_handlers,
                       [("File", "notexists")])
