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
Test methods of the file handler.
"""


import os
import tempfile

from configobj import ConfigObj

from repoguard.core import constants
from repoguard.handlers.file import File, SEPARATOR
from repoguard_test.util import TestProtocol, TestProtocolEntry


_CONFIG_STRING = """
file=%s
"""


class TestFile(object):
    """ Implements the file handler tests. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.test_protocol = TestProtocol()
        cls.test_protocol.add_entry(result=constants.SUCCESS, msg="dummy")
        cls.test_protocol.add_entry(result=constants.ERROR, msg="dummy")
        cls.file_ = File(None)
    
    def test_run(self):
        """ Tests the successful execution of a certain handler step. """
         
        filehandle, filename = tempfile.mkstemp()
        
        os.fdopen(filehandle).close()
        
        config = ConfigObj((_CONFIG_STRING % filename).splitlines())
        
        self.file_.singularize(config, TestProtocolEntry.error())

        file_object = open(filename, "r")
        content = file_object.read()
        file_object.close()
        os.remove(filename)
        assert content == str(TestProtocolEntry.error()) + SEPARATOR
        
    def test_summarize(self):
        """ Tests the successful execution of the handler. """
        
        filehandle, filename = tempfile.mkstemp()
        os.fdopen(filehandle).close()
        config = ConfigObj((_CONFIG_STRING % filename).splitlines())
        self.file_.summarize(config, self.test_protocol)
        
        file_object = open(filename, "r")
        content = file_object.read()
        file_object.close()
        os.remove(filename)
        assert content == str(self.test_protocol) + SEPARATOR
