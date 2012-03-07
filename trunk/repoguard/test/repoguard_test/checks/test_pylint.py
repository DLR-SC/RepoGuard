# pylint: disable=R0903
# R0903: Just the mock classes have to few methods.
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
Test methods for the Pylint class.
"""


from configobj import ConfigObj
from pylint import lint

from repoguard.checks import pylint_
from repoguard_test.util import TestRepository
        

class _StringIoMock(object):
    """ Mock of the StringIO class. """
   
    success = True # Used to trigger errors
   
    def __init__(self):
        """ Just calls the default StringIO constructor. """
       
        pass
   
    def getvalue(self):
        """ Mocks the StringIO.getvalue method. """
        
        if self.success:
            return None
        else:
            return "error"


class _RunMock:
    """ Mocks the lint.Run class. """
    
    def __init__(self, _, reporter=None):
        """ Effectively the constructor dies nothing. """
        
        pass
        
        
class TestPyLint(object):
    """ Tests pylint checker. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        checker_config = "ignore_files=,\n"
        # Test without pylintrc
        cls._config_without_pylintrc = ConfigObj(checker_config.splitlines())
        # Test with custom pylintrc
        checker_config += "config_file=pylintrc\n"
        cls._config_with_pylintrc = ConfigObj(checker_config.splitlines())
        
        # Mocking pylint and StringIO modules
        cls._string_io_class = pylint_.StringIO.StringIO
        pylint_.StringIO.StringIO = _StringIoMock
        lint.Run = _RunMock
        
    @classmethod
    def teardown_class(cls):
        """ Resets the StringIO class. """
        
        pylint_.StringIO.StringIO = cls._string_io_class
        
    def test_for_success(self):
        """ Checks behavior without pylint errors. """

        _StringIoMock.success = True
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\n\nprint "hallo"')
        transaction = repository.commit()
        pylint = pylint_.PyLint(transaction)
        assert pylint.run(self._config_without_pylintrc).success == True
        assert pylint.run(self._config_with_pylintrc).success == True

    def test_for_failure(self):
        """ Checks behavior with existing pylint errors. """

        _StringIoMock.success = False
        repository = TestRepository()
        repository.add_file("test.py", 'print "hallo"')
        transaction = repository.commit()
        pylint = pylint_.PyLint(transaction)
        assert pylint.run(self._config_without_pylintrc).success == False
        assert pylint.run(self._config_with_pylintrc).success == False
