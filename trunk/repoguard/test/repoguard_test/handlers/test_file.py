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


from __future__ import with_statement

from configobj import ConfigObj
import mock
import pytest

from repoguard.handlers import file as file_


_CONFIG_DEFAULT = "file=/path/to/output/file"


class TestFile(object):
    
    def setup_method(self, _):
        self._entry = mock.Mock()
        self._protocol = mock.MagicMock()
        
        self._config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        self._file = file_.File(None)
        
    def test_nonexisting_filepath(self):
        with mock.patch("repoguard.handlers.file.os.path.exists", create=True) as exists:
            exists.return_value = False
            with pytest.raises(IOError):
                self._file.singularize(self._config, mock.Mock(), debug=True)
        
    def test_singularize_success(self):
        with mock.patch("repoguard.handlers.file.os.path.exists", create=True) as exists:
            exists.return_value = True
            with mock.patch("repoguard.handlers.file.open", create=True) as open_mock:
                self._file.singularize(self._config, self._entry, True)
                assert self._write_called(open_mock)
            
    def test_summary_success(self):
        with mock.patch("repoguard.handlers.file.os.path.exists", create=True) as exists:
            exists.return_value = True
            with mock.patch("repoguard.handlers.file.open", create=True) as open_mock:
                self._file.summarize(self._config, self._protocol, True)
                assert self._write_called(open_mock)
                
    @staticmethod
    def _write_called(open_mock):
        return open_mock.return_value.__enter__.return_value.write.called
