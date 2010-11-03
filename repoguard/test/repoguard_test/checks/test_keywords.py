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
Test methods for the Keywords class.
"""


from configobj import ConfigObj

from repoguard.checks.keywords import Keywords
from repoguard_test.util import TestRepository


_CONFIG_STRING = """
keywords=Date,Revision
"""

class TestKeywords(object):
    """ Tests the keyowrd check. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.config = ConfigObj(_CONFIG_STRING.splitlines())
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    def test_run(self):
        """ Tests the successful run. """
        
        keywords = Keywords(self.transaction)
        entry = keywords.run(self.config)
        assert entry.msg.count("Revision") == 2
        assert entry.msg.count("Date") == 1
        assert entry.success == False
