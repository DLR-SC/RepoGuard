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
Tests the Mantis handler
"""


from StringIO import StringIO

from configobj import ConfigObj
import mock

from repoguard.handlers import mantis


_CONFIG_DEFAULT = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=user
password=secret
custom_field = custom
"""

_CONFIG_WITH_VCS_SYNC = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=user
password=secret
custom_field = custom
vcs_sync_url=http://localhost/mantis/plugin.php?page=Source/import&id=all
"""


class TestMantis(object):
    
    def setup_method(self, _):
        self._urlopen = mock.Mock(return_value=StringIO("No Revisions Parsed."))
        mantis.urllib2.urlopen = self._urlopen
        self._mantis = mock.Mock()
        self.__mantis_class = mantis.base.Mantis 
        mantis.base.Mantis = mock.Mock(return_value=self._mantis)
        self._protocol = mock.MagicMock()
        
        self._config_default = ConfigObj(_CONFIG_DEFAULT.splitlines())
        self._config_with_vcs_sync = ConfigObj(_CONFIG_WITH_VCS_SYNC.splitlines())
        self._mantis_handler = mantis.Mantis(mock.Mock(return_value="commit_msg"))
        
    def teardown_method(self, _):
        mantis.base.Mantis = self.__mantis_class
        
    def test_no_issues_extracted(self):
        self._mantis.extract_issues.return_value = list()
        self._mantis_handler.summarize(self._config_default, self._protocol, debug=True)
        assert not self._note_added
        assert not self._field_set
        assert not self._vcs_sync
    
    def test_no_issues_exist(self):
        self._mantis.extract_issues.return_value = ["1234"]
        self._mantis.issue_exists.return_value = False
        self._mantis_handler.summarize(self._config_default, self._protocol, debug=True)
        assert not self._note_added
        assert not self._field_set
        assert not self._vcs_sync
    
    def test_issues_found(self):
        self._mantis.extract_issues.return_value = ["1234"]
        self._mantis.issue_exists.return_value = True
        self._mantis_handler.summarize(self._config_default, self._protocol, debug=True)
        assert self._note_added
        assert self._field_set
        assert not self._vcs_sync

    def test_issues_found_with_vcs_sync(self):
        self._mantis.extract_issues.return_value = ["1234"]
        self._mantis.issue_exists.return_value = True
        self._mantis_handler.summarize(self._config_with_vcs_sync, self._protocol, debug=True)
        assert not self._note_added
        assert self._field_set
        assert self._vcs_sync

    @property
    def _note_added(self):
        return self._mantis.issue_add_note.called
    
    @property
    def _field_set(self):
        return self._mantis.issue_set_custom_field.called
    
    @property
    def _vcs_sync(self):
        return self._urlopen.called
