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
Tests the CaseInsensitiveFilenameClash check.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import caseinsensitivefilenameclash


class TestCaseInsensitiveFilenameClash(object):

    @classmethod
    def setup_class(cls):
        cls._transaction = mock.Mock()
        
        cls.config = ConfigObj(list())
        cls._check = caseinsensitivefilenameclash.CaseInsensitiveFilenameClash(cls._transaction)
        
    def test_detect_filename_clash(self):
        self._transaction.get_files.return_value = {"test.java": "A"}
        self._transaction.file_exists.return_value = True
        assert not self._check.run(self.config).success

    def test_detect_no_filename_clash(self):
        self._transaction.get_files.return_value = {"test.java": "A"}
        self._transaction.file_exists.return_value = False
        assert self._check.run(self.config).success
