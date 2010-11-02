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
Test methods for the Mantis class.
"""


from configobj import ConfigObj

from repoguard.checks.mantis import Mantis
from repoguard.modules import mantis
from repoguard.testutil import MantisMock, TestRepository


_CONFIG_STRING = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
check_in_progress=False
check_handler=False
"""


class TestMantis(object):
    """ Tests the Mantis checker. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        mantis.Mantis = MantisMock

    def test_success(self):
        """ Tests successful run of the Mantis checker. """
        
        mantis_ = Mantis(self.transaction)
        result = mantis_.run(self.config, debug=True)
        assert result.success == True
