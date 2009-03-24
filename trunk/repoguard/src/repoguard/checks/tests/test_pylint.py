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
Test methods for the Pylint class.
"""

from configobj import ConfigObj

from repoguard.checks.pylint_ import PyLint
from repoguard.testutil import TestRepository

import os
import tempfile

config_string = """
ignore_files=,
"""

class TestPyLint:

    @classmethod
    def setup_class(cls):
        handle, filename = tempfile.mkstemp()
        fd = os.fdopen(handle)
        fd.close()
        global config_string
        # Test without pylintrc
        cls.config = ConfigObj(config_string.splitlines())
        # Test with pylintrc
        config_string += "config_file=%s\n" % filename
        cls.config2 = ConfigObj(config_string.splitlines())

    def test_for_success(self):
        repository = TestRepository()
        repository.add_file("test.py", '""" docstring. """\nprint "hallo"')
        transaction = repository.commit()
        pylint = PyLint(transaction)
        assert pylint.run(self.config).success == True
        assert pylint.run(self.config2).success == True

    def test_for_failure(self):
        repository = TestRepository()
        repository.add_file("test.py", 'print "hallo"')
        transaction = repository.commit()
        pylint = PyLint(transaction)
        assert pylint.run(self.config).success == False
        assert pylint.run(self.config2).success == False
