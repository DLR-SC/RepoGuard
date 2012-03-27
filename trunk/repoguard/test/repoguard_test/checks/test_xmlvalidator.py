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
Tests the XMLValidator check.
"""


from configobj import ConfigObj
import mock
import StringIO

from repoguard.checks import xmlvalidator


class TestXMLValidator(object):
    
    @classmethod
    def setup_class(cls):
        cls._transaction = mock.Mock()
        cls._transaction.get_files = mock.Mock(return_value={"filepath":"A"})
        
        cls._config = ConfigObj()
        cls._xmlvalidator = xmlvalidator.XMLValidator(cls._transaction)

    def test_validation_success(self):
        content = '<?xml version="1.0" encoding="UTF-8"?><body></body>'
        self._transaction.get_file = mock.Mock(return_value=StringIO.StringIO(content))
        assert self._xmlvalidator.run(self._config).success

    def test_validation_failure(self):
        content = '<?xml version="1.0" encoding="UTF-8"?>NOT_VALID'
        self._transaction.get_file = mock.Mock(return_value=StringIO.StringIO(content))
        assert not self._xmlvalidator.run(self._config).success
