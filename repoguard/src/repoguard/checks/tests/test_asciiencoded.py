# -*- coding: utf-8 -*-
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
Test methods for the AccessRights class.
"""

from configobj import ConfigObj

from repoguard.checks.asciiencoded import ASCIIEncoded
from repoguard.testutil import TestRepository


class TestASCIIEncoded(object):
    
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(encoding='UTF-8')
        
    def test_ascii_check_success(self):
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\nprint "hällo@#"')
        transaction = repository.commit()  
        
        asciiencoded = ASCIIEncoded(transaction)
        result = asciiencoded.ascii_check(
            transaction.get_file("test.py"), "ä", "e"
        )
        assert not result
        
    def test_ascii_check_error(self):
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\nprint "hellö@#"')
        transaction = repository.commit()
        
        asciiencoded = ASCIIEncoded(transaction)
        result = asciiencoded.ascii_check(
            transaction.get_file("test.py"), "ö", "e"
        )
        assert result
        
    def test_run_success(self):
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\nprint "hallo@#"')
        transaction = repository.commit()  
        
        asciiencoded = ASCIIEncoded(transaction)
        assert asciiencoded.run(self.config, debug=True).success == True
        
    def test_run_error(self):
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\nprint "hällö@#"')
        transaction = repository.commit()  
        
        asciiencoded = ASCIIEncoded(transaction)
        assert asciiencoded.run(self.config, debug=True).success == False