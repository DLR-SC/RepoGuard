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
Test methods for the Checkout class.
"""


import os
import tempfile

from configobj import ConfigObj

from repoguard.checks.checkout import Checkout
from repoguard_test.util import TestRepository


_CONFIG_STRING = """
entries=entry1,
entries.entry1.source=test.java
entries.entry1.destination=%DESTINATION%
"""


class TestCheckout(object):
    """ Tests the checkout check. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        file_descriptor, cls._dest_filepath = tempfile.mkstemp()
        config = _CONFIG_STRING.replace("%DESTINATION%", cls._dest_filepath)\
                 .splitlines()
        os.close(file_descriptor)
        cls.config = ConfigObj(config)
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()

    @classmethod
    def teardown_class(cls):
        """ Removes the checked out file. """
        
        os.remove(cls._dest_filepath)
    
    def test_run(self):
        """ Tests the successful run. """
        
        checkout = Checkout(self.transaction)
        assert checkout.run(self.config).success == True
