# pylint: disable-msg=W0232, E1102
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
Test methods for the Config class.
"""

import os
import tempfile

import py.test

from pkg_resources import resource_filename, Requirement

from repoguard.core import constants
from repoguard.core.config import ProjectConfig, RepoGuardConfig, Process

repoguard_config = """
template_dirs = %s,
validate = False

[projects]
    [[RepoGuard]]
    path = %s
    editors = lege_ma,
"""

default_config = """
[profiles]
    [[default]]
        [[[precommit]]]
        success = Console,
        error = Console,
"""

python_config = """
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

project_config = """
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

class TestRepoGuardConfig(object):
    
    @classmethod
    def setup_class(cls):
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          'default.tpl.conf')
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          'python.tpl.conf')
        fp = open(cls.defaulttplfile, 'w')
        fp.write(default_config)
        fp.close()
        
        fp = open(cls.pythontplfile, 'w')
        fp.write(python_config)
        fp.close()
        
        cls.projectdir = tempfile.mkdtemp()
        cls.hooksdir = os.path.join(cls.projectdir, "hooks")
        os.mkdir(cls.hooksdir)
        
        cls.configfile = os.path.join(cls.hooksdir, constants.CONFIG_FILENAME)
        config = (repoguard_config % (cls.templatedir, cls.projectdir))
        
        cls.config = RepoGuardConfig(config.splitlines())
        
    def test_projects(self):
        assert self.config.projects['RepoGuard'].name == 'RepoGuard'
        
    def test_templates(self):
        assert [u'default', u'python'] == self.config.templates.keys()
    
    def test_template_dirs(self):
        requirement = Requirement.parse(constants.NAME)
        buildin = resource_filename(
            requirement, os.path.join('..', constants.BUILDIN_TPL_PATH)
        )
        assert self.config.template_dirs == [self.templatedir, buildin]
        
    def test_validate(self):
        assert not self.config.validate

class TestProjectConfig(object):
    
    @classmethod
    def setup_class(cls):
        """ create example configurations. """
        
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          'default.tpl.conf')
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          'python.tpl.conf')
        fp = open(cls.defaulttplfile, 'w')
        fp.write(default_config)
        fp.close()
        
        fp = open(cls.pythontplfile, 'w')
        fp.write(python_config)
        fp.close()
        
        cls.config = ProjectConfig(project_config, "hooks", [cls.templatedir])
        
    def test_extended(self):
        assert 'python' in self.config.extended.keys()
        
    def test_vcs(self):
        assert self.config.vcs == "svn"

    def test_hook(self):           
        assert self.config['DEFAULT'].get("hooks") == "hooks"
        
        path = self.config['handlers']['File']['default']['file']
        assert path == "hooks/default.log"
        
    def test_properties(self):
        assert self.config.properties['pythonhome'] == "D:/python25"
        
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
        
        precommit = self.config['profiles']['default']['precommit']
        assert precommit['checks'][0] == "PyLint.default"
        assert precommit['success'][0] == "Console"
        
    def test_process(self):
        default, test = self.config.profiles
        
        assert len(test.precommit.checks) == 2
        
        process = default.precommit
        name, config, interp = process.checks[0]
        assert name == 'PyLint'
        assert config['check_files'] == [".*\\.py"]
        assert interp == constants.ABORTONERROR
                
        assert default.postcommit is None
        
class TestProcess(object):
    
    @classmethod
    def setup_class(cls):
        cls.templatedir = tempfile.mkdtemp()
        cls.defaulttplfile = os.path.join(cls.templatedir, 
                                          'default.tpl.conf')
        cls.pythontplfile  = os.path.join(cls.templatedir, 
                                          'python.tpl.conf')
        fp = open(cls.defaulttplfile, 'w')
        fp.write(default_config)
        fp.close()
        
        fp = open(cls.pythontplfile, 'w')
        fp.write(python_config)
        fp.close()
        
        cls.projectdir = tempfile.mkdtemp()
        cls.hooksdir = os.path.join(cls.projectdir, "hooks")
        os.mkdir(cls.hooksdir)
        
        cls.configfile = os.path.join(cls.hooksdir, constants.CONFIG_FILENAME)
        
        cls.config = ProjectConfig(project_config, "hooks", [cls.templatedir])
        cls._profile = cls.config.profile("default")
        
    def test_set_process(self):
        process = Process(self._profile, self._profile.depth, self.config)
        process.checks = [('PyLint', 'default', constants.DELAYONERROR),
                          ('PyLint', 'default', None),
                          ('PyLint', None, constants.WARNING),
                          ('PyLint', None, None)]
        process.success = [('File', 'default'), ('File', None)]
        
        self._profile.precommit = process
        checks = self.config['profiles']['default']['precommit']['checks']
        assert checks == ['PyLint.default.' + constants.DELAYONERROR, 
                          'PyLint.default', 
                          'PyLint..' + constants.WARNING, 
                          'PyLint']
        
        success = self.config['profiles']['default']['precommit']['success']
        assert success == ['File.default', 'File']
        
        process = Process(self._profile, self._profile.depth, self.config)
        py.test.raises(KeyError, process._set_checks, 
                       [('PyLint', 'notexists', None)])
        py.test.raises(KeyError, process._set_success_handlers,
                       [('File', 'notexists')])