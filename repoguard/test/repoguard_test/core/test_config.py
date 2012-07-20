# pylint: disable=E1101
# E1101: py.test.raises is callable
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


from __future__ import with_statement


import os

import mock
import py.test

from repoguard.core import constants
from repoguard.core.config import ProjectConfig, RepoGuardConfig, Process
from repoguard.core import config


_REPOGUARD_CONFIG = """
template_dirs = %s,
validate = False

[projects]
    [[RepoGuard]]
    path = 
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
"""


class TestRepoGuardConfig(object):
    
    @classmethod
    def setup_class(cls):
        cls._default_template_path = "/cfg/templates"
        cls._additional_template_path = "/path/to/other/templates"
        
        root_config = _REPOGUARD_CONFIG % cls._additional_template_path
        config.Requirement = mock.Mock()
        config.resource_filename = mock.Mock(return_value=cls._default_template_path)
        cls.config = RepoGuardConfig(root_config.splitlines())

    def test_projects(self):
        assert self.config.projects["RepoGuard"].name == "RepoGuard"
        
    def test_templates(self):
        with mock.patch("repoguard.core.config.os") as os_mock:
            os_mock.listdir.return_value = ["default.tpl.conf", "python.tpl.conf"]
            assert [u"default", u"python"] == self.config.templates.keys()
    
    def test_template_dirs(self):
        assert self.config.template_dirs == [
            os.path.normpath(self._additional_template_path), self._default_template_path]
        
    def test_validate(self):
        assert not self.config.validate


class TestProjectConfig(object):
    
    @classmethod
    def setup_class(cls):
        with mock.patch("repoguard.core.config.os") as os_mock:
            os_mock.path.exists.return_value = True
            # Dirty hack: "misusing" the template file path to avoid usage of temporary file objects 
            os_mock.path.join.side_effect = [_PYTHON_CONFIG.splitlines(), _DEFAULT_CONFIG.splitlines()]
            cls.config = ProjectConfig(_PROJECT_CONFIG.splitlines(), "hooks", ["template_path"])
    
    def test_extended(self):
        assert "python" in self.config.extended.keys()
        
    def test_vcs(self):
        assert self.config.vcs == "svn"

    def test_hook(self):
        assert self.config["DEFAULT"].get("hooks") == "hooks"
        
        path = self.config["handlers"]["File"]["default"]["file"]
        assert path == "hooks/default.log"
        
    def test_properties(self):
        assert self.config.properties["pythonhome"] == "D:/python25"
        
    def test_profiles(self):
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
        default, test = self.config.profiles
        
        assert len(test.precommit.checks) == 2
        
        process = default.precommit
        name, config_, interp = process.checks[0]
        assert name == "PyLint"
        assert config_["check_files"] == [".*\\.py"]
        assert interp == constants.ABORTONERROR
                
        assert default.postcommit is None
        
    def test_set_process(self):
        # pylint: disable=W0212
        # Access to protected is required for test
        profile = self.config.profile("default")
        process = Process(profile, profile.depth, self.config)
        process.checks = [("PyLint", "default", constants.DELAYONERROR),
                          ("PyLint", "default", None),
                          ("PyLint", None, constants.WARNING),
                          ("PyLint", None, None)]
        process.success = [("File", "default"), ("File", None)]
        
        profile.precommit = process
        checks = self.config["profiles"]["default"]["precommit"]["checks"]
        assert checks == ["PyLint.default." + constants.DELAYONERROR, 
                          "PyLint.default", 
                          "PyLint.." + constants.WARNING, 
                          "PyLint"]
        
        success = self.config["profiles"]["default"]["precommit"]["success"]
        assert success == ["File.default", "File"]
        
        process = Process(profile, profile.depth, self.config)
        py.test.raises(KeyError, process._set_checks, 
                       [("PyLint", "notexists", None)])
        py.test.raises(KeyError, process._set_success_handlers,
                       [("File", "notexists")])


def test_no_extension_template_found():
    with py.test.raises(ValueError):
        ProjectConfig(_PROJECT_CONFIG.splitlines(), "hooks", ["template_path"])
