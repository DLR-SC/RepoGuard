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
Test methods for the Checkout class.
"""

import tempfile

from configobj import ConfigObj

from repoguard.checks.checkout import Checkout
from repoguard.testutil import TestRepository


config_string = """
entries=entry1,
entries.entry1.source=test.java
entries.entry1.destination=%DESTINATION%
"""

class TestCheckout:
    
    @classmethod
    def setup_class(cls):
        config = config_string.replace("%DESTINATION%", tempfile.mkstemp()[1]).splitlines()
        cls.config = ConfigObj(config)
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    def test_run(self):
        checkout = Checkout(self.transaction)
        assert checkout.run(self.config).success == True
