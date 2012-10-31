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
Tests the Mantis module.
"""


import mock
import pytest

try:
    from repoguard.modules import mantis
    _SKIP = False
except ImportError:
    _SKIP = True
       

_COMMIT_MESSAGE = """
mantis id 3662
Test1
MANTIS ID 3883
Test2
"""


class TestMantis(object):
    
    pytestmark = pytest.mark.skipif("_SKIP")
    
    def setup_method(self, _):
        mantis.Client = mock.MagicMock()
        self.mantis = mantis.Mantis(mock.Mock())
        self.service = self.mantis.service
        
    def test_pattern(self):
        assert self.mantis.extract_issues(_COMMIT_MESSAGE) == ["3662", "3883"]
        assert self.mantis.extract_issues("NO VALID IDS 234, 23434") == list() 

    def test_issue_exists(self):
        assert self.mantis.issue_exists(1)

    def test_issue_get_status(self):
        assert not self.mantis.issue_get_status("1") == None

    def test_issue_get_handler_handler_defined(self):
        handler_result = mock.Mock()
        handler_result.handler.name = "me"
        self.service.mc_issue_get.return_value = handler_result
        
        assert self.mantis.issue_get_handler("2") == "me"
        
    def test_issue_get_handler_no_handler_defined(self):
        patcher = mock.patch("repoguard.modules.mantis.hasattr", create=True)
        hasattr_mock = patcher.start()
        try:
            hasattr_mock.return_value = False
            assert self.mantis.issue_get_handler("1") == None
        finally:
            hasattr_mock = patcher.stop()
            
    def test_issue_add_note(self):
        self.mantis.issue_add_note("1", "test")
        
    def test_issue_set_custom_field_success(self):
        custom_field = mock.Mock()
        custom_field.field.name = "SVNRevision"
        custom_fields = mock.MagicMock()
        custom_fields.__iter__ = lambda _: iter(["SVNRevision"])
        custom_fields.__getitem__ = lambda _, __: custom_field
        self.service.mc_issue_get.return_value = mock.Mock(custom_fields=custom_fields)
        
        self.mantis.issue_set_custom_field("1", "SVNRevision", "123")
        assert self.service.mc_issue_update.call_count == 1

    def test_issue_set_custom_field_no_field(self):
        pytest.raises(ValueError, 
            self.mantis.issue_set_custom_field, "1", "SVNRevision", "123")
