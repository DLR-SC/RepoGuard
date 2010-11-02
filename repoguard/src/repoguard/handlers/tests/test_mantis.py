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


from configobj import ConfigObj

from repoguard.handlers.mantis import Mantis
from repoguard.testutil import MantisMock, TestRepository, TestProtocol


_CONFIG_STRING = """
protocol.include=Log,
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
"""


class TestMantis(object):
    """ Tests the Mantis handler. """
    
    @classmethod
    def setup_class(cls):
        cls.test_protocol = TestProtocol()
        cls.test_protocol.add_entry(check="Foo")
        cls.test_protocol.add_entry(check="Log")
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        from repoguard.modules import mantis
        mantis.Mantis = MantisMock
        
    def test_check_include(self):
        config = Mantis.__config__.from_config(self.config)
        assert config.protocol.include == ['Log']

    def test_run(self):
        """ Tests the successful execution of the handler. """
        
        mantis = Mantis(self.transaction)
        mantis.summarize(
            self.config, self.test_protocol, debug=True
        )
