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
Test methods of the console handler.
"""


from __future__ import with_statement

import os
import sys
import tempfile

from configobj import ConfigObj

from repoguard.core import constants
from repoguard.handlers.console import Console
from repoguard_test.util import TestProtocol, TestProtocolEntry


class TestConsole(object):
    """ Implements the console handler tests. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.test_protocol = TestProtocol()
        cls.test_protocol.add_entry(result=constants.SUCCESS, msg="dummy")
        cls.test_protocol.add_entry(result=constants.ERROR, msg="dummy")
        
        cls.console = Console(None)
        cls.config = ConfigObj()
    
    def test_run(self):
        """ Tests the successful execution of a certain handler step. """
        
        error_filehandle, error_filename = tempfile.mkstemp()
        success_filehandle, success_filename = tempfile.mkstemp()
        
        error_file = os.fdopen(error_filehandle, "w")
        success_file = os.fdopen(success_filehandle, "w")
        
        self.console.out = {
            constants.SUCCESS : success_file,
            constants.WARNING : error_file,
            constants.ERROR : error_file,
            constants.EXCEPTION : error_file
        }
        
        self.console.singularize(self.config, TestProtocolEntry.error())
        self.console.singularize(self.config, TestProtocolEntry.success())

        error_file.close()
        success_file.close()

        with open(error_filename, "r") as file_object:
            assert file_object.read() == self.console.pattern \
                                         % TestProtocolEntry.error()

        with open(success_filename, "r") as file_object:
            assert file_object.read() == self.console.pattern \
                                         % TestProtocolEntry.success()
        
    def test_summarize(self):
        """ Tests the successful execution of the handler. """
        
        error_filehandle, error_filename = tempfile.mkstemp()
        error_file = os.fdopen(error_filehandle, "w")
        self.console.out = {
            constants.SUCCESS : sys.stdout,
            constants.WARNING : error_file,
            constants.ERROR : error_file,
            constants.EXCEPTION : error_file
        }
        self.console.summarize(self.config, self.test_protocol)
        error_file.close()
        
        with open(error_filename, "r") as file_object:
            assert file_object.read() == self.console.pattern \
                                         % self.test_protocol