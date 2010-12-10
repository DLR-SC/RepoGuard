# pylint: disable=E1101
# E1101:  'ConfigSerializer' HAS a 'viewvc' member.
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
Test methods for the Log class.
"""


from configobj import ConfigObj

from repoguard.checks.log import Log
from repoguard_test.util import TestRepository

_CONFIG_STRING = """
viewvc.url=http://localhost
viewvc.root=test
viewvc.view=test
"""

class TestConfig(object):
    """ Tests configuration of the log check. """
    
    @classmethod
    def setup_class(cls):
        """ Creates test setup. """
        
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
    
    def test_encode(self):
        """ Tests configuration loading from string. """
        
        config = Log.__config__.from_config(self.config)
        url = config.viewvc.encode(1)
        assert url == "http://localhost?revision=1&root=test&view=test"


class TestLog(object):
    """ Tests of the log check. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    def test_run(self):
        """ Tests the successful execution of the check. """
        log = Log(self.transaction)
        assert log.run(self.config).success == True
