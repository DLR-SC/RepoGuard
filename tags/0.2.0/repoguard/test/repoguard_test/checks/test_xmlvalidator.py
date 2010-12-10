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
Test methods for the XMLValidator class.
"""


from configobj import ConfigObj

from repoguard.checks.xmlvalidator import XMLValidator
from repoguard_test.util import TestRepository


class TestXMLValidator(object):
    """ Tests the XML validator. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.config = ConfigObj(list())

    def test_for_success(self):
        """ Tests successful validation. """
        
        repository = TestRepository()
        content = '<?xml version="1.0" encoding="UTF-8"?><body></body>'
        repository.add_file("Test.xml", content)
        transaction = repository.commit()
        xmlvalidator = XMLValidator(transaction)
        assert xmlvalidator.run(self.config).success == True

    def test_for_failure(self):
        """ Tests unsuccessful validation. """
        
        repository = TestRepository()
        content = '<?xml version="1.0" encoding="UTF-8"?><body>/body>'
        repository.add_file("Test.xml", content)
        transaction = repository.commit()
        xmlvalidator = XMLValidator(transaction)
        assert xmlvalidator.run(self.config).success == False
