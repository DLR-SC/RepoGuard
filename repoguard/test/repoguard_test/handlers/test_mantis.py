# pylint: disable=E1101
# E1101: ConfigSerializer has the protocol member -> False-Negative.
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

from repoguard.handlers import mantis
from repoguard_test.util import MantisMock, TestRepository, TestProtocol


_CONFIG_STRING = """
protocol.include=Log,
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
custom_field = peter
vcs_sync_url=http://localhost/mantis/plugin.php?page=Source/import&id=all
"""


class TestMantis(object):
    """ Tests the Mantis handler. """
    
    @classmethod
    def setup_class(cls):
        """ Creates test setup. """
        
        cls.test_protocol = TestProtocol()
        cls.test_protocol.add_entry(check="Foo")
        cls.test_protocol.add_entry(check="Log")
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        # Activates mocks
        mantis.urllib2.urlopen = lambda _: StringIO("No Revisions Parsed.")
        mantis.base.Mantis = MantisMock
        
    def test_check_include(self):
        """ Tests the inclusion. """
        
        config = mantis.Mantis.__config__.from_config(self.config)
        assert config.protocol.include == ["Log"]

    def test_run(self):
        """ Tests the successful execution of the handler. """
        
        mantis_ = mantis.Mantis(self.transaction)
        mantis_.summarize(
            self.config, self.test_protocol, debug=True
        )
