# -*- coding: utf-8 -*-
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
Tests the console handler.
"""


from configobj import ConfigObj
import mock
import StringIO

from repoguard.core import constants
from repoguard.core import protocol as protocol_
from repoguard.handlers import console as console_


class TestConsole(object):
    
    def setup_method(self, _): # pylint: disable=W0212
        self._entry = mock.MagicMock(result=constants.SUCCESS)
        self._protocol = mock.MagicMock(result=constants.SUCCESS)
        self._protocol.filter.return_value = self._protocol
        self._success_file = StringIO.StringIO()
        self._error_file = StringIO.StringIO()
        
        self._config = ConfigObj()
        self._console = console_.Console(None)
        self._console._OUT = {
            constants.SUCCESS: self._success_file,
            constants.WARNING: self._error_file,
            constants.ERROR: self._error_file,
            constants.EXCEPTION: self._error_file
        }
        
    def test_singularize_success_channel(self):
        self._console.singularize(self._config, self._entry)
        assert self._success_file.len > 0
        
    def test_singularize_warning_channel(self):
        self._entry.result = constants.WARNING
        self._console.singularize(self._config, self._entry)
        assert self._error_file.len > 0
        
    def test_singularize_error_channel(self):
        self._entry.result = constants.ERROR
        self._console.singularize(self._config, self._entry)
        assert self._error_file.len > 0
        
    def test_singularize_exception_channel(self):
        self._entry.result = constants.EXCEPTION
        self._console.singularize(self._config, self._entry)
        assert self._error_file.len > 0
        
    def test_summarize_success_channel(self):
        self._console.summarize(self._config, self._protocol)
        assert self._success_file.len > 0
    
    def test_summarize_warning_channel(self):
        self._protocol.result = constants.WARNING
        self._console.summarize(self._config, self._protocol)
        assert self._error_file.len > 0
        
    def test_summarize_error_channel(self):
        self._protocol.result = constants.ERROR
        self._console.summarize(self._config, self._protocol)
        assert self._error_file.len > 0
        
    def test_summarize_exception_channel(self):
        self._protocol.result = constants.EXCEPTION
        self._console.summarize(self._config, self._protocol)
        assert self._error_file.len > 0


def test_unicode_handling():
    protocol = protocol_.Protocol("Default")
    message = unicode("Something wänt wröng!", "utf-8")
    entry = protocol_.ProtocolEntry("PyLint", None, msg=message)
    protocol.append(entry)
    
    console = console_.Console(None)
    console.singularize(ConfigObj(), entry)
    console.summarize(ConfigObj(), protocol)
