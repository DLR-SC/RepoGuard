# pylint: disable-msg=W0603, W0232

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
Test methods for the File class.
"""

import os
import tempfile

from configobj import ConfigObj

from repoguard.core import constants
from repoguard.testutil import TestProtocol, TestProtocolEntry
from repoguard.handlers.file import File, SEPARATOR

config_string = """
file=%s
"""

class TestFile:
    
    @classmethod
    def setup_class(cls):
        cls.test_protocol = TestProtocol()
        cls.test_protocol.add_entry(result=constants.SUCCESS, msg="dummy")
        cls.test_protocol.add_entry(result=constants.ERROR, msg="dummy")
        cls.file_ = File(None)
    
    def test_run(self):        
        filehandle, filename = tempfile.mkstemp()
        
        os.fdopen(filehandle).close()
        
        c = (config_string % filename).splitlines()
        
        config = ConfigObj(c)
        
        self.file_.singularize(config, TestProtocolEntry.error())

        fd = open(filename, "r")
        content = fd.read()
        fd.close()
        assert content == str(TestProtocolEntry.error()) + SEPARATOR
        
    def test_summarize(self):
        filehandle, filename = tempfile.mkstemp()
        os.fdopen(filehandle).close()
        c = (config_string % filename).splitlines()
        config = ConfigObj(c)
        self.file_.summarize(config, self.test_protocol)
        
        fd = open(filename, "r")
        content = fd.read()
        fd.close()
        assert content == str(self.test_protocol) + SEPARATOR
