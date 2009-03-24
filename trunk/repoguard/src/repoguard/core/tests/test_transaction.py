# pylint: disable-msg=W0232, E1102
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
Test methods for the Transaction class.
"""

import py.test

from repoguard.testutil import TestRepository
from repoguard.core.transaction import FileNotFoundException, PropertyNotFoundException


class TestTransaction:
    
    @classmethod
    def setup_class(cls):
        """ create reference to transaction. """
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        
    def testGetUserID(self):
        assert self.transaction._get_user_id()

    def testGetFiles(self):
        assert self.transaction.get_files() == { 'test.java' : 'A', 'test 1.txt' : 'A' }
        assert self.transaction.get_files([".*\.java"]) == { 'test.java' : 'A' }
        assert self.transaction.get_files([".*"], [".*\.java"]) == { 'test 1.txt' : 'A' }
        assert self.transaction.get_files(["test.java", "test 1.txt"]) == { 'test.java' : 'A', 'test 1.txt' : 'A' }
        assert self.transaction.get_files(["test.java", "test 1.txt"], ["test.java"]) == { 'test 1.txt' : 'A' }
        
    def testGetFile(self):
        filename = self.transaction.get_file("test 1.txt")
        assert open(filename).read() == "content"
        # Test caching
        filename = self.transaction.get_file("test 1.txt")
        assert open(filename).read() == "content"
        py.test.raises(FileNotFoundException, self.transaction.get_file, "blablub")

    def test_file_exists(self):
        assert self.transaction.file_exists("test 1.txt")
        assert not self.transaction.file_exists("bla.txt")

    def test_get_commit_msg(self):
        assert self.transaction._get_commit_msg() == self.repository.commit_message
    
    def test_get_revision(self):
        assert self.transaction._get_revision() == "2"
    
    def test_has_property(self):
        assert self.transaction.has_property("svn:keywords", "test 1.txt")
        py.test.raises(FileNotFoundException, self.transaction.get_property, "keywordx", "bla")
        assert not self.transaction.has_property("keywordx", "test 1.txt")
    
    def test_get_keyword(self):
        assert self.transaction.get_property("svn:keywords", "test 1.txt") == "Date"
        py.test.raises(FileNotFoundException, self.transaction.get_property, "keywordx", "bla")
        py.test.raises(PropertyNotFoundException, self.transaction.get_property, "keywordx", "test 1.txt")

    def test_list_keywords(self):
        assert self.transaction.list_properties("test 1.txt") == ["svn:keywords"]
        assert self.transaction.list_properties("test.java") == []
        py.test.raises(FileNotFoundException, self.transaction.list_properties, "bla")
        