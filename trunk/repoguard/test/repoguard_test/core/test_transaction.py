# pylint: disable=E1101,W0212
# E1101: Pylint cannot import py.test
# W0212: Access to protected methods is ok in tests cases.
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
Test methods for the Transaction class.
"""


import mock
import py.test

from repoguard.core import process
from repoguard.core import transaction


from __future__ import with_statement


class TestTransaction(object):
    
    def setup_method(self, _):
        self._transaction = transaction.Transaction("repoPath", "10")
        self._transaction._execute_svn = mock.Mock()
        
    def test_get_files(self):
        self._transaction._execute_svn.return_value = ["A   test 1.txt", "A   test.java"]
        assert self._transaction.get_files() == {"test.java": "A", "test 1.txt": "A"}
        assert self._transaction.get_files(
            [".*\.java"]) == {"test.java" : "A"}
        assert self._transaction.get_files(
            [".*"], [".*\.java"]) == {"test 1.txt": "A"}
        assert self._transaction.get_files(
            ["test.java", "test 1.txt"]) == {"test.java" : "A", "test 1.txt" : "A"}
        assert self._transaction.get_files(
            ["test.java", "test 1.txt"], ["test.java"])  == {"test 1.txt" : "A"}
        
    def test_get_file_not_found(self):
        self._transaction.file_exists = mock.Mock(return_value=False)
        with py.test.raises(transaction.FileNotFoundException):
            self._transaction.get_file("/path/notexisting.java")
            
    def test_get_file_in_cache(self):
        self._transaction.file_exists = mock.Mock(return_value=True)
        cached_filepath = "/path/existing.java"
        with mock.patch("repoguard.core.transaction.os.path.exists", create=True):
            assert cached_filepath in self._transaction.get_file(cached_filepath)

    def test_get_file_not_cached(self):
        self._transaction.file_exists = mock.Mock(return_value=True)
        transaction.os.makedirs = mock.Mock()
        filepath = "/path/existing.java"
        with mock.patch("repoguard.core.transaction.os.path.exists", create=True):
            with mock.patch("repoguard.core.transaction.open", create=True):
                assert filepath in self._transaction.get_file(filepath)

    def test_file_exists(self):
        assert self._transaction.file_exists("test 1.txt")
    
    def test_file_exists_not(self):
        self._transaction._execute_svn.side_effect = process.ProcessException("", 0, "")
        assert not self._transaction.file_exists("bla.txt")

    def test_file_exists_ignorecase(self):
        self._transaction._execute_svn.return_value = ["test 1.txt", "test 1.txt"]
        assert self._transaction.file_exists("test 1.txt", True)
    
    def test_file_exists_not_ignorecase(self):
        self._transaction._execute_svn.return_value = list()
        assert not self._transaction.file_exists("bla.txt", True)

    def test_has_property(self):
        self._transaction.file_exists = mock.Mock(return_value=True)
        self._transaction._execute_svn.return_value = ["svn:keywords"]
        assert self._transaction.has_property("svn:keywords", "test 1.txt")
        
    def test_has_property_not(self):
        self._transaction.file_exists = mock.Mock(return_value=True)
        self._transaction._execute_svn.return_value = ["svn:keywords"]
        assert not self._transaction.has_property("keywordx", "test 1.txt")
    
    def test_get_property(self):
        self._transaction.has_property = mock.Mock(return_value=True)
        self._transaction._execute_svn.return_value = "Date"
        assert self._transaction.get_property("svn:keywords", "test 1.txt") == "Date"
       
    def test_get_property_not(self):
        self._transaction.has_property = mock.Mock(return_value=False)
        with py.test.raises(transaction.PropertyNotFoundException): 
            self._transaction.get_property("keywordx", "test 1.txt")

    def test_list_properties(self):
        self._transaction.file_exists = mock.Mock(return_value=True)
        self._transaction._execute_svn.return_value = ["svn:keywords"]
        assert self._transaction.list_properties("test 1.txt") == ["svn:keywords"]
    
    def test_list_properties_file_not_found(self):
        self._transaction.file_exists = mock.Mock(return_value=False)
        with py.test.raises(transaction.FileNotFoundException):
            self._transaction.list_properties("nonexisting.java")
