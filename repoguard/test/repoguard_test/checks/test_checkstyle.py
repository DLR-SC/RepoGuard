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
Test the for the Checkstyle check.
"""


from __future__ import with_statement

import os
import sys

from configobj import ConfigObj
import mock

from repoguard.core import process
from repoguard.checks import checkstyle


_CONFIG_DEFAULT = """
java=C:/Programme/Java/jdk1.6.0_11/bin/java.exe
paths=C:/,
config_file=checkstylefile
"""


class TestCheckstyle(object):
    
    def setup_method(self, _):
        self._transaction = mock.Mock()
        self._transaction.get_files.return_value = {"filepath":"A"}
        self._transaction.get_file.return_value = "filepath"
        
        self._config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        self._checkstyle = checkstyle.Checkstyle(self._transaction)

    def test_empty_file_set(self):
        self._transaction.get_files.return_value = dict()
        with mock.patch("repoguard.checks.checkstyle.process.execute") as execute_mock:
            assert self._checkstyle.run(self._config, debug=True).success
            assert not execute_mock.called
            
    def test_empty_deleted(self):
        self._transaction.get_files.return_value = {"filepath":"D"}
        with mock.patch("repoguard.checks.checkstyle.process.execute") as execute_mock:
            assert self._checkstyle.run(self._config, debug=True).success
            assert not execute_mock.called
            
    def test_success(self):
        with mock.patch("repoguard.checks.checkstyle.process.execute"):
            assert self._checkstyle.run(self._config, debug=True).success

    def test_failure(self):
        with mock.patch("repoguard.checks.checkstyle.process.execute") as process_mock:
            process_mock.side_effect = process.ProcessException("", -1, "")
            assert not self._checkstyle.run(self._config, debug=True).success

        
def test_classpath():
    isdir = os.path.isdir
    listdir = os.listdir
    os.path.isdir = lambda path: path == "/libs"
    os.listdir = lambda _: ["foo.jar", "bar.txt"]
    config = checkstyle.Config()
    config.paths = ["/libs", "/path/dummy.jar"]
    try:
        if sys.platform == "win32":
            assert config.classpath == "\\libs\\foo.jar:\\path\\dummy.jar"
        else:
            assert config.classpath == "/libs/foo.jar:/path/dummy.jar"
    finally:
        os.path.isdir = isdir
        os.listdir = listdir
