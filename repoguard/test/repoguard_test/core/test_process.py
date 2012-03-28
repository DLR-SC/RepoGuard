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
    with mock.patch("repoguard.core.process.subprocess.Popen") as popen_class:
        popen_class.return_value.returncode = 0
        process.execute("svnlook help")
    
def test_execute_error():
    with mock.patch("repoguard.core.process.subprocess.Popen") as popen_class:
        popen_class.return_value.returncode = -1
        with pytest.raises(process.ProcessException) as error: # pytest.raises exists pylint: disable=E1101
            process.execute("somecommand")
            assert error.exit_code != 0
            assert error.command == "somecommand"
            assert error.output != ""
