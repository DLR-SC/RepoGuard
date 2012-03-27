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
Test the Log check.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import log


_CONFIG_DEFAULT = """
viewvc.url=http://localhost
viewvc.root=test
viewvc.view=test
"""


class TestLog(object):
    
    @classmethod
    def setup_class(cls):
        cls._config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        
    def test_success(self):
        transaction = mock.Mock(user_id="user", revision="1", commit_msg="")
        transaction.get_files.return_value = {"filepath":"A"}
        assert log.Log(transaction).run(self._config).success
        
    def test_encode(self):
        # pylint: disable=E1101
        # E1101:  'ConfigSerializer' HAS a 'viewvc' member.
        config = log.Log.__config__.from_config(self._config)
        url = config.viewvc.encode(1)
        assert url == "http://localhost?revision=1&root=test&view=test"
