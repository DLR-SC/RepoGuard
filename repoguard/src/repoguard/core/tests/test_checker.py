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

import tempfile

from repoguard.core import constants
from repoguard.core.checker import RepoGuard
from repoguard.testutil import TestRepository

main_config = """
template_dirs = resources/templates,
""".splitlines()

config_string = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=PyLint.default, PyLint, Mantis.default
        success=Console.success, Mantis.default
        error=Console.error,
        
        [[[postcommit]]]
        checks=UnitTests.default, Checkout.default
        success=File.default, Console.success
        error=File.default, Console.error
    
[checks]
    [[PyLint]]
        [[[default]]]
        
    [[UnitTests]]
        [[[default]]]
        
    [[Checkout]]
        [[[default]]]
        entries=entry1,
        entries.entry1.source=test.java
        entries.entry1.destination=%DESTINATION%
    [[Mantis]]
        [[[default]]]
        url=http://localhost/mantis/mc/mantisconnect.php?wsdl
        user=administrator
        password=root
        
[handlers]
    [[Console]]
        [[[success]]]
        [[[error]]]
        
    [[File]]
        [[[default]]]
        file=${hooks}/repoguard.log
        
    [[Mantis]]
        [[[default]]]
        url=http://localhost/mantis/mc/mantisconnect.php?wsdl
        user=administrator
        password=root
"""

class TestRepoGuard(object):
    
    @classmethod
    def setup_class(cls):
        cls.repository = TestRepository()
        cls.repository.add_file('test.py', 'print "Hallo Welt"')
        cls.repository.create_default()
        
        cls.precommit_checker = RepoGuard(
            constants.PRECOMMIT, cls.repository.repodir
        )
        cls.precommit_checker.load_transaction("1")
        
        cls.postcommit_checker = RepoGuard(
            constants.POSTCOMMIT, cls.repository.repodir
        )
        cls.postcommit_checker.load_transaction("1")
    
    def test_initialize(self):
        config = config_string.replace("%DESTINATION%", tempfile.mkstemp()[1]).splitlines()
        self.precommit_checker.load_config(main_config, config)
        assert not self.precommit_checker.main is None
        
        self.postcommit_checker.load_config(main_config, config)
        assert not self.postcommit_checker.main is None
        
    def test_run(self):
        result = self.precommit_checker.run()
        assert result == constants.ERROR
        
        result = self.postcommit_checker.run()
        assert result == constants.SUCCESS