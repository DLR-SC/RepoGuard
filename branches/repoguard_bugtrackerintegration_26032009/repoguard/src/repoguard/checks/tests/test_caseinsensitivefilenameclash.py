# pylint: disable-msg=W0232, E1101

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
Test methods for the CaseInsensitiveFilenameClash class.
"""

import sys

from configobj import ConfigObj

from repoguard.checks.caseinsensitivefilenameclash import CaseInsensitiveFilenameClash
from repoguard.testutil import TestRepository

config_string = """
"""

class TestCaseInsensitiveFilenameClash:
    
    disabled = sys.platform == "win32"

    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(config_string.splitlines())

    def test_for_success(self):
        repository = TestRepository()
        repository.create_diretory("src")
        repository.add_file("TestInterface.java", "public interface TestInterface {\n}\n")
        transaction = repository.commit()
        caseinsensitivefilenameclash = CaseInsensitiveFilenameClash(transaction)
        assert caseinsensitivefilenameclash.run(self.config, debug=True).success == True

    def test_for_failure(self):
        repository = TestRepository()
        repository.create_diretory("main")
        repository.create_diretory("Main")
        transaction = repository.commit()
        caseinsensitivefilenameclash = CaseInsensitiveFilenameClash(transaction)
        assert caseinsensitivefilenameclash.run(self.config, debug=True).success == False
