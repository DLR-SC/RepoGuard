# pylint: disable-msg=W0232, W0603

# Copyright 2008 Adam Byrtek
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
Test methods for the RejectTabs class.
"""

from configobj import ConfigObj

from repoguard.checks.rejecttabs import RejectTabs
from repoguard.testutil import TestRepository

import os
import tempfile

config_string = """
check_files=.*\.py$,
ignore_files=,
"""

class TestRejectTabs:

    @classmethod
    def setup_class(cls):
        handle, _ = tempfile.mkstemp()
        os.fdopen(handle).close()
        cls.config = ConfigObj(config_string.splitlines())

    def test_reject_leading_tabs(self):
        repository = TestRepository()
        repository.add_file("first_tab.py", 'if True:\n\tprint "Hello world"')
        repository.add_file("tab_after_space.py", 'if True:\n \tprint "Hello world"')
        repository.add_file("tab_inside.py", 'if True:    print "Hello\tworld"')
        transaction = repository.commit()
        rejecttabs = RejectTabs(transaction)
        entry = rejecttabs.run(self.config)
        msg_list = entry.msg.split("\n")
        assert entry.success == False
        assert len(msg_list) == 2
        assert "File first_tab.py contains leading tabs" in msg_list
        assert "File tab_after_space.py contains leading tabs" in msg_list

    def test_skip_binary_files(self):
        repository = TestRepository()
        repository.add_file("binary_tab.py", '\t\t\t')
        repository.set_property("binary_tab.py", "svn:mime-type", "application/octet-stream")
        transaction = repository.commit()
        rejecttabs = RejectTabs(transaction)
        assert rejecttabs.run(self.config).success == True

    def test_ignore(self):
        repository = TestRepository()
        repository.add_file("tabbed.txt", 'if True:\n\tprint "Hello world"')
        transaction = repository.commit()
        rejecttabs = RejectTabs(transaction)
        assert rejecttabs.run(self.config).success == True
