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
Test methods for the UnitTests class.
"""

from configobj import ConfigObj

from repoguard.checks.unittests import UnitTests
from repoguard.testutil import TestRepository


config_string = """
"""

class TestUnitTests:
    
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj(config_string.splitlines())

    def test_for_success(self):
        repository = TestRepository()
        repository.create_diretory("src")
        repository.create_diretory("src/main")
        repository.create_diretory("src/test")
        repository.add_file("src/main/Klasse.java", "public class Klasse {\n}\n")
        repository.add_file("src/test/KlasseTest.java", "public class TestKlasse {\n}\n")
        repository.add_file("TestInterface.java", "public interface TestInterface {\n}\n")
        transaction = repository.commit()
        unittests = UnitTests(transaction)
        assert unittests.run(self.config).success == True

    def test_for_failure(self):
        repository = TestRepository()
        repository.create_diretory("main")
        repository.add_file("main/Klasse.java", "public class Klasse {\n}\n")
        transaction = repository.commit()
        unittests = UnitTests(transaction)
        assert unittests.run(self.config).success == False
