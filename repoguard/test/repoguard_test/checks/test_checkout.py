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
Tests the Checkout checker.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import checkout


_CONFIG_DEFAULT = """
entries=entry1,
entries.entry1.source=test.java
entries.entry1.destination=/path/test.java
"""


class TestCheckout(object):
    
    @classmethod
    def setup_class(cls):
        cls._transaction = mock.Mock()
        checkout.shutil.move = mock.Mock()
        
        cls._config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        cls._checkout = checkout.Checkout(cls._transaction)
        
    def test_success(self):
        self._transaction.get_file.return_value = "filepath"
        assert self._checkout.run(self._config).success

    def test_missing_file(self):
        self._transaction.file_exists.return_value = False
        assert not self._checkout.run(self._config).success

    def test_move_failure(self):
        self._transaction.get_file.return_value = "filepath"
        checkout.shutil.move.side_effect = IOError
        assert not self._checkout.run(self._config).success
