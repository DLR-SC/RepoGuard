# pylint: disable=E1101
# E1101: Pylint cannot find pytest.raises
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
Tests the process execution.
"""


import mock
import pytest

from repoguard.core import process


def test_execute_success():
    patcher = mock.patch("repoguard.core.process.subprocess.Popen")
    popen_class = patcher.start()
    try:
        popen_class.return_value.returncode = 0
        popen_class.return_value.communicate.return_value = ("output")
        output = process.execute("svnlook help")
        assert isinstance(output, unicode) 
    finally:
        patcher.stop()
        
def test_execute_raw_out():
    patcher = mock.patch("repoguard.core.process.subprocess.Popen")
    popen_class = patcher.start()
    try:
        popen_class.return_value.returncode = 0
        popen_class.return_value.communicate.return_value = ("output")
        output = process.execute("svnlook help", raw_out=True)
        assert isinstance(output, str) 
    finally:
        patcher.stop()
        
def test_execute_error():
    patcher = mock.patch("repoguard.core.process.subprocess.Popen")
    popen_class = patcher.start()
    try:
        popen_class.return_value.returncode = -1
        pytest.raises(process.ProcessException, process.execute, "somecommand")
    finally:
        patcher.stop()
