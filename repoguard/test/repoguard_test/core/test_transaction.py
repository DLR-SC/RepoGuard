# pylint: disable=E1101,E0611,F0401,W0212
# E1101,E0611,F0401: Pylint cannot import py.test
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


import py.test

from repoguard.core.transaction import FileNotFoundException, \
                                       PropertyNotFoundException
from repoguard_test.util import TestRepository


class TestTransaction(object):
    """ Implements the transaction tests. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the reference to the transaction. """
        
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        
    def test_get_user_id(self):
        """ Checks the user id. """
        
        assert self.transaction._get_user_id()

    def test_get_files(self):
        """ Checks the determined file sets. """
        
        assert self.transaction.get_files() == {'test.java': 'A', 
                                                'test 1.txt': 'A'}
        assert self.transaction.get_files([".*\.java"]) == { 'test.java' : 'A' }
        assert self.transaction.get_files([".*"], [".*\.java"]) \
                                          == {'test 1.txt': 'A'}
        assert self.transaction.get_files(["test.java", "test 1.txt"]) \
                                           == {'test.java' : 'A',
                                               'test 1.txt' : 'A'}
        assert self.transaction.get_files(["test.java", "test 1.txt"], 
                                          ["test.java"]) \
                                           == {'test 1.txt' : 'A'}
        
    def test_get_file(self):
        """" Checks a determined file. """
        
        filename = self.transaction.get_file("test 1.txt")
        assert open(filename).read() == "content"
        # Test caching
        filename = self.transaction.get_file("test 1.txt")
        assert open(filename).read() == "content"
        py.test.raises(FileNotFoundException, self.transaction.get_file, 
                       "blablub")

    def test_file_exists(self):
        """ Checks file existence. """
        
        assert self.transaction.file_exists("test 1.txt")
        assert not self.transaction.file_exists("bla.txt")

    def test_get_commit_msg(self):
        """ Checks commit message. """
        
        assert self.transaction._get_commit_msg() \
               == self.repository.commit_message
    
    def test_get_revision(self):
        """ Checks revision. """
        
        assert self.transaction._get_revision() == "2"
    
    def test_has_property(self):
        """ Checks property existence. """
        
        assert self.transaction.has_property("svn:keywords", "test 1.txt")
        py.test.raises(FileNotFoundException, self.transaction.get_property, 
                       "keywordx", "bla")
        assert not self.transaction.has_property("keywordx", "test 1.txt")
    
    def test_get_keyword(self):
        """ Checks keywords. """
        
        assert self.transaction.get_property("svn:keywords", "test 1.txt") \
               == "Date"
        py.test.raises(FileNotFoundException, self.transaction.get_property, 
                       "keywordx", "bla")
        py.test.raises(PropertyNotFoundException, 
                       self.transaction.get_property, "keywordx", "test 1.txt")

    def test_list_keywords(self):
        """ Checks keyword listing. """
        
        assert self.transaction.list_properties("test 1.txt") \
               == ["svn:keywords"]
        assert self.transaction.list_properties("test.java") == []
        py.test.raises(FileNotFoundException, self.transaction.list_properties,
                       "bla")
