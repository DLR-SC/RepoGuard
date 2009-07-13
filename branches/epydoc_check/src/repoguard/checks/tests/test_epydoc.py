# pylint: disable-msg=W0232, W0603

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
Test methods for the Epydoc class.
"""

from configobj import ConfigObj
from repoguard.checks.epydoc_ import Epydoc
from repoguard.testutil import TestRepository


class TestEpydoc:
    @classmethod
    def setup_class(cls):
        cls.config = ConfigObj()


    def test_for_success(self):
        repository = TestRepository()
        repository.add_file('test.py', 
                            '"""\nThis is a test file\n"""\n\nclass Test(object):\n'\
                            '  """Test class"""\n'\
                            '  def start():\n'\
                            '    """\n'\
                            '    Starts test\n'\
                            '    """\n'\
                            '    print "start"')
        transaction = repository.commit()
        epydoc = Epydoc(transaction)
        assert epydoc.run(self.config).success == True

    def test_for_failure(self):
        repository = TestRepository()
        repository.add_file("test.py", 'print "hallo"')
        transaction = repository.commit()
        epydoc = Epydoc(transaction)
        assert epydoc.run(self.config).success == False
