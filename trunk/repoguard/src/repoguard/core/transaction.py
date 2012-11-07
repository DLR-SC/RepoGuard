# pylint: disable-msg=W0102, W0704
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

""" Class to work with transactions. """


import os
import re
import shutil
import tempfile

from repoguard.core import process

class FileNotFoundException(Exception):
    def __init__(self, filename):
        Exception.__init__(self, "No such file in repository or transaction %r." % filename)

class PropertyNotFoundException(Exception):
    def __init__(self, keyword, filename):
        Exception.__init__(self, "Property %r for file %r not set." % (keyword, filename))


class Transaction(object):

    def __init__(self, repos_path, txn_name):
        """ 
        Initialize the transaction object. 
        """
        
        if txn_name is None: # HEAD revision
            self.type = "revision"
        else:
            txn_name = str(txn_name)
            try:
                int(txn_name)
                self.type = "revision"
            except ValueError:
                self.type = "transaction"
 
        self.repos_path = repos_path
        self.txn_name = txn_name
        self._profile = re.compile(".*")
        self.tmpdir = tempfile.mkdtemp()
        self.cache = {}

    def _execute_svn(self, command, arg="", split=False):
        if self.txn_name is None:
            command = 'svnlook %s "%s" %s' % (command, self.repos_path, arg)
        else:
            command = 'svnlook --%s %s %s "%s" %s' % (self.type, self.txn_name, command, self.repos_path, arg)
        
        if command in self.cache:
            return self.cache[command]
        
        try:
            output = process.execute(command, raw_out=True)
        except process.ProcessException, error:
            if "Transaction '(null)'" in error.output: # Nothing bad happened we just have an empty repository
                output = ""
            else:
                raise
        
        if split:
            output = [x.strip() for x in output.split("\n") if x.strip()]
        
        self.cache[command] = output
        return self.cache[command]

    def cleanup(self):
        """
        Delete the temporary directory.
        Do NOT use in your checks or handlers.
        """
        shutil.rmtree(self.tmpdir)
        
    def _get_profile(self):
        """
        Returns the current profile.
        Do NOT use in your checks or handlers.
        """
        return self._profile

    def _set_profile(self, profile):
        """
        Sets the current profile.
        Do NOT use in your checks or handlers.
        """
        self._profile = re.compile(profile)

    def _get_user_id(self):
        """ Returns a string with the username of the current transaction. """
        user = self._execute_svn("author")
        return user.strip()

    def get_files(self, check_list=[".*"], ignore_list=[]):        
        """
        Returns a map of all modified files. The keys of the map
        are the filenames. The values of the map is the
        associated attribute, which can be one of the default
        svnlook changed attributes: 
        http://svnbook.red-bean.com/en/1.4/svn-book.html#svn.ref.svnlook.c.changed
    
        @param check_list List of regular expressions for files which should be included.
        @param ignore_list List of regular expressions for files which should be ignored.
        """
        
        output = self._execute_svn("changed", split=True)
        files = {}
        for entry in output:
            attributes = entry[0:3].strip()
            filename = entry[4:].strip()

            if self._profile.search(filename) and self.__check(filename, check_list) and not self.__check(filename, ignore_list):
                files[filename] = attributes
        return files

    def __check(self, datei, items):
        for item in items:
            regex = re.compile(item)
            if regex.search(datei):
                return True
        return False

    def get_file(self, filename):
        """ Returns the path to a temporary copy of a file in the repository. """
        if not self.file_exists(filename):
            raise FileNotFoundException(filename)

        tmpfilename = os.path.join(self.tmpdir, filename)
        if os.path.exists(tmpfilename):
            return tmpfilename

        content = self._execute_svn("cat", "\"" + filename + "\"")

        dirname = os.path.dirname(filename)
        tmpdirname = os.path.join(self.tmpdir, dirname)
        if dirname and not os.path.exists(tmpdirname):
            os.makedirs(tmpdirname)

        file_object = open(tmpfilename, "w")
        try:
            file_object.write(content)
        finally:
            file_object.close()
        return tmpfilename

    def file_exists(self, filename, ignore_case=False):
        """ 
        Returns whether a file exists in the current transaction or revision of 
        the repository, optionally case-insensitive. 
        """
        exists = False

        if ignore_case:
            filename = filename.lower()
            files = self._execute_svn("tree", "--full-paths", split=True)
            count = 0
            for fname in files:
                if fname.lower() == filename:
                    count += 1
                    if count >= 2:
                        exists = True
                        break

        else:
            try:
                self._execute_svn("proplist", "\"" + filename + "\"", split=True)
                exists = True
            except process.ProcessException:
                pass

        return exists

    def _get_commit_msg(self):
        """ 
        Returns the commit message. 
        """
        
        output = self._execute_svn("info", split=True)
        temp = output[3:]
        msg = "\n".join(temp)
        return msg.strip()

    def _get_revision(self):
        """ 
        Returns the id of the revision or transaction. 
        """
        
        revision = "HEAD"
        if not self.txn_name is None:
            try:
                revision = int(self.txn_name.split("-")[0]) + 1
            except ValueError:
                revision = self.txn_name
        return str(revision)

    def get_property(self, keyword, filename):
        """ 
        Returns a specified property of a file.
        """
        
        if not self.has_property(keyword, filename):
            raise PropertyNotFoundException(keyword, filename)
    
        return self._execute_svn("propget", " ".join([keyword, "\"" + filename + "\""]))

    def has_property(self, keyword, filename):
        """
        Checks if a given file has the given property.
        """
        
        return keyword in self.list_properties(filename)

    def list_properties(self, filename):
        """
        Returns a list of names of the properties for a file.
        """
        
        if not self.file_exists(filename):
            raise FileNotFoundException(filename)

        return self._execute_svn("proplist", "\"" + filename + "\"", split=True)

    profile = property(_get_profile, _set_profile)
    user_id = property(_get_user_id)
    revision = property(_get_revision)
    commit_msg = property(_get_commit_msg)
