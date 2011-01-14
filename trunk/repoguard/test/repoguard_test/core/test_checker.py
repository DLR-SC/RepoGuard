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


""" Tests the RepoGuard main class. """


import os
import pkg_resources
import tempfile

from repoguard.core import constants
from repoguard.core.checker import RepoGuard
from repoguard.core.module import Check, Handler
from repoguard_test.util import TestRepository


_MAIN_CONFIG = """
template_dirs = resources/templates,
""".splitlines()


_CONFIG_STRING = """
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


def _load_entry_point_mock(_, group, name):
    """ 
    Mocks the C{load_entry_point} function. 
    For handlers the handler base class is returned. For
    the PyLint checker a checker instance which always ends up with
    an error is returned. For all other checker a checker instance is 
    returned which always succeeds.
    """
    
    class ErrorCheck(Check):
        """ Represents a failed check. """
        
        def _run(self, _):
            return self.error("")
        
    class SuccessCheck(Check):
        """ Represents a successful check. """
        
        def _run(self, _):
            return self.success()

    if "handler" in group:
        return Handler
    else:
        if name == "PyLint":
            return ErrorCheck
        else:
            return SuccessCheck


class TestRepoGuard(object):
    """ Tests configuration pre and post commit checker runs. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.repository = TestRepository()
        cls.repository.add_file("test.py", "print 'Hallo Welt'")
        cls.repository.create_default()
        
        cls.precommit_checker = RepoGuard(
            constants.PRECOMMIT, cls.repository.repodir
        )
        cls.precommit_checker.load_transaction("1")
        
        cls.postcommit_checker = RepoGuard(
            constants.POSTCOMMIT, cls.repository.repodir
        )
        cls.postcommit_checker.load_transaction("1")
        pkg_resources.load_entry_point = _load_entry_point_mock
    
    def test_initialize(self):
        """ Tests the run initialization. """
        
        file_descriptor, filepath = tempfile.mkstemp()
        config = _CONFIG_STRING.replace("%DESTINATION%", filepath)\
                 .splitlines()
        os.close(file_descriptor)
        os.remove(filepath)
        self.precommit_checker.load_config(_MAIN_CONFIG, config)
        assert not self.precommit_checker.main is None
        
        self.postcommit_checker.load_config(_MAIN_CONFIG, config)
        assert not self.postcommit_checker.main is None
        
    def test_run(self):
        """ Tests the pre and post commit checker runs. """
        
        result = self.precommit_checker.run()
        assert result == constants.ERROR
        
        result = self.postcommit_checker.run()
        assert result == constants.SUCCESS
