# pylint: disable-msg=W0232

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
Test methods for the Log class.
"""

from configobj import ConfigObj

from repoguard.checks.log import Log
from repoguard.testutil import TestRepository

config_string = """
viewvc.url=http://localhost
viewvc.root=test
viewvc.view=test
"""

class TestConfig(object):
    
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(config_string.splitlines())
    
    def test_encode(self):
        config = Log.__config__.from_config(self.config)
        url = config.viewvc.encode(1)
        assert url == "http://localhost?revision=1&root=test&view=test"

class TestLog(object):
    
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(config_string.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    def test_run(self):
        log = Log(self.transaction)
        assert log.run(self.config).success == True
