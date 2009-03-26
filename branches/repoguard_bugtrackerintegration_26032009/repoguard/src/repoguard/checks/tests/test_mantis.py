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
Test methods for the Mantis class.
"""

import py.test

from urllib2 import URLError

from configobj import ConfigObj

from repoguard.checks.mantis import Mantis
from repoguard.testutil import TestRepository


config_string = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
check_in_progress=False
check_handler=False
"""

class TestMantis:
    
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(config_string.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    def test_run(self):
        mantis = Mantis(self.transaction)
        try:
            result = mantis.run(self.config, debug=True)
        except URLError:
            py.test.skip()
        assert result.success == True
