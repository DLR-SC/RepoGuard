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
    
    @classmethod
    def setup_class(cls):
        transaction = mock.Mock()
        transaction.get_files.return_value = {"filepath":"A"}
        transaction.get_file.return_value = "filepath"
        checkstyle.process.execute = mock.Mock()
        
        cls._config = ConfigObj(_CONFIG_DEFAULT.splitlines())
        cls._checkstyle = checkstyle.Checkstyle(transaction)

    def test_success(self):
        assert self._checkstyle.run(self._config, debug=True).success

    def test_failure(self):
        checkstyle.process.execute.side_effect = process.ProcessException("", -1, "")
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
