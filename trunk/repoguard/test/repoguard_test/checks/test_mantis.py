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
Tests of the Mantis check.
"""


from configobj import ConfigObj
import mock
import pytest

try:
    from repoguard.checks import mantis
    _SKIP = False
except ImportError:
    _SKIP = True

_CONFIG_DEFAULT = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=me
password=secret
check_in_progress=True
check_handler=True
"""


class TestMantisCheck(object):
    
    pytestmark = pytest.mark.skipif("_SKIP")
    
    @classmethod
    def setup_class(cls):
        cls._mantis_module = mock.Mock()
        cls.__mantis_class = mantis.base.Mantis
        mantis.base.Mantis = mock.Mock(return_value=cls._mantis_module)
        
        cls.config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        cls._mantis = mantis.Mantis(mock.Mock(user_id="me"))

    @classmethod
    def teardown_class(cls):
        mantis.base.Mantis = cls.__mantis_class
        
    def test_no_issue_ids(self):
        self._mantis_module.extract_issues.return_value = list()
        assert not self._mantis.run(self.config).success

    def test_issue_not_exists(self):
        self._mantis_module.extract_issues.return_value = ["1278"]
        self._mantis_module.issue_exists.return_value = False
        assert not self._mantis.run(self.config).success

    def test_issue_not_in_progress(self):
        self._mantis_module.extract_issues.return_value = ["1278"]
        self._mantis_module.issue_exists.return_value = True
        self._mantis_module.issue_get_status.return_value = "assigned"
        assert not self._mantis.run(self.config).success
    
    def test_issue_not_wrong_handler(self):
        self._mantis_module.extract_issues.return_value = ["1278"]
        self._mantis_module.issue_exists.return_value = True
        self._mantis_module.issue_get_status.return_value = "in_progress"
        self._mantis_module.issue_get_handler.return_value = "anotheruser"
        assert not self._mantis.run(self.config).success
        
    def test_success(self):
        self._mantis_module.extract_issues.return_value = ["1278"]
        self._mantis_module.issue_exists.return_value = True
        self._mantis_module.issue_get_status.return_value = "in_progress"
        self._mantis_module.issue_get_handler.return_value = "me"
        assert self._mantis.run(self.config).success
