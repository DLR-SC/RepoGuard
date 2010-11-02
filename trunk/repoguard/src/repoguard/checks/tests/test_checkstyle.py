# pylint: disable=R0903, R0201
# R0903: The _ProcessFunctionMock does not to to have more methods.
# R0201: test_classpath is only recognized as test method when 
#        it is a "normal" method.
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
Test methods for the Checkstyle class.
"""


import os

from configobj import ConfigObj

from repoguard.core import process
from repoguard.checks import checkstyle
from repoguard.checks.checkstyle import Checkstyle, Config
from repoguard.testutil import TestRepository


_CONFIG_STRING = """
java=C:/Programme/Java/jdk1.6.0_11/bin/java.exe
paths=C:/,
config_file=checkstylefile
"""



class _ProcessFunctionMock(object):
    """ Mocks repoguard.core.process.execute function. """
    
    success = True
    def __call__(self, command):
        """
        For the checkstyle command behavior is defined by C{success}.
        For svnlook (and all others) a valid change set is returned.
        """
        
        result = ""
        if "java" in command: # Mocks checkstyle command
            if not self.success:
                raise process.ProcessException(command, -1, "error")
        else: # Mocks svnlook command
            result = " U Test.java"
        return result
    

class TestCheckstyle(object):
    """ Tests the check style checker. """
    
    
    @classmethod
    def setup_class(cls):
        """ Creates test setup. """
        
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.default_execute = None
        
    def setup(self):
        """ Mocks process.execute."""
        
        self.default_execute = process.execute
        process.execute = _ProcessFunctionMock()
        
    def teardown(self):
        """ Resets the process.execute mock. """
        
        process.execute = self.default_execute
        
    def test_for_success(self):
        """ Tests successful behavior. """
        
        _ProcessFunctionMock.success = True
        repository = TestRepository()
        repository.add_file("Test.java", "public class test { }\n")
        transaction = repository.commit()
        checkstyle_check = Checkstyle(transaction)
        assert checkstyle_check.run(self.config, debug=True).success == True

    def test_for_failure(self):
        """ Tests failure behavior. """
        
        _ProcessFunctionMock.success = False
        repository = TestRepository()
        repository.add_file("Test.java", "public class test { }")
        transaction = repository.commit()
        checkstyle_check = Checkstyle(transaction)
        assert checkstyle_check.run(self.config, debug=True).success == False
        
    def test_classpath(self):
        """ Tests Java class path creation. """
        
        # Mocking some os functions
        isdir = os.path.isdir
        listdir = os.listdir
        os.path.isdir = lambda path: path == "/libs"
        os.listdir = lambda _: ["foo.jar", "bar.txt"]
        # Check it
        try:
            config = Config()
            config.paths = ["/libs", "/path/dummy.jar"]
            result = ":".join((
                os.path.normpath("/libs/foo.jar"), 
                os.path.normpath("/path/dummy.jar")
            ))
            assert config.classpath == result
        finally:
            # Reset some os functions
            os.path.isdir = isdir
            os.listdir = listdir
