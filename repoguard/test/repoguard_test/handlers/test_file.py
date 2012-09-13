# -*- coding: utf-8 -*-
# pylint: disable=E1101
# E1101: Pylint cannot find pytest.raises
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
Tests the file handler.
"""


import configobj
import mock
import pytest

from repoguard.core import protocol as protocol_
from repoguard.handlers import file as file_


_CONFIG_DEFAULT = "file=/path/to/output/file"


class TestFile(object):
    
    def setup_method(self, _):
        self._entry = mock.Mock()
        self._protocol = mock.MagicMock()
        
        self._config = configobj.ConfigObj(_CONFIG_DEFAULT.splitlines())
        self._file = file_.File(None)
        
    def test_nonexisting_filepath(self):
        patcher, open_mock = self._get_file_open_mock()
        open_mock.side_effect = IOError("")
        try:
            pytest.raises(IOError, self._file.singularize, self._config, mock.Mock(), debug=True)
        finally:
            patcher.stop()
            
    @staticmethod
    def _get_file_open_mock():
        patcher = mock.patch("repoguard.handlers.file.open", create=True)
        open_mock = patcher.start()
        return patcher, open_mock
            
    def test_singularize_success(self):
        patcher, open_mock = self._get_file_open_mock()
        try:
            self._file.singularize(self._config, self._entry, True)
            assert self._write_called(open_mock)
        finally:
            patcher.stop()
            
    def test_summary_success(self):
        patcher, open_mock = self._get_file_open_mock()
        try:
            self._file.summarize(self._config, self._protocol, True)
            assert self._write_called(open_mock)
        finally:
            patcher.stop()

    @staticmethod
    def _write_called(open_mock):
        return open_mock.return_value.write.called

    def test_unicode_handling(self, tmpdir):
        protocol = protocol_.Protocol("Default")
        message = unicode("Something wänt wröng!", "utf-8")
        entry = protocol_.ProtocolEntry("PyLint", None, msg=message)
        protocol.append(entry)
        config = configobj.ConfigObj(["file=" + str(tmpdir.join("out"))])
        
        self._file.singularize(config, entry, debug=True)
        self._file.summarize(config, protocol, debug=True)
