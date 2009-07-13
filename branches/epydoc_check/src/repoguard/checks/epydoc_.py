# pylint: disable-msg=W0232
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
Checks Python files for complete documentation using epydoc 
"""


import os

from epydoc.docbuilder import build_doc_index
from epydoc import log as epydoc_log
from epydoc.checker import DocChecker
from epydoc import docstringparser
from epydoc.checker import _NO_BASIC, _NO_PARAM, _NO_RETURN, _NO_DOCS


from repoguard.core import process
from repoguard.core.module import Check, ConfigSerializer, String, Array, Boolean



class Config(ConfigSerializer):
    """
    Configuration for Epydoc check.
    """
    
    paths = []
    
    class types(ConfigSerializer.types):
        check_files = Array(String, optional = True, default = [".*\.py"])
        ignore_files = Array(String, optional = True, default = [])
        docformat = String(optional = True, default = "plaintext")
        no_docs = Array(String, optional = True, default = ['object.__new__'])
        strict = Boolean(optional = True, default = False)
        

class Epydoc(Check):
    
    __config__ = Config

    def _run(self, config):
        """
        Method is called when the check has to run.
        
        :param config: The configuration that has to be used by the check.
        :type config: Config
        
        :return: Returns an error or success messages by calling the success
                 or error method.
        :rtype: Tuple that contains the success or error code and message.
        """
        
        
        
        #List of files that has to be checked.
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        #Skip if the transaction contains no python files.
        if not files:
            return self.success()
        
        files = " ".join([
            self.transaction.get_file(filename) 
            for filename, attribute in files.iteritems() 
                 if attribute in ["A", "U", "UU"]
        ])
        
        #initialize docchecker
        _NO_DOCS.extend(['__setattr__', '__new__'])
        
        docstringparser.DEFAULT_DOCFORMAT = config.docformat
        #docindex = build_doc_index(files.split())#
        docindex = build_doc_index(["/home/steven/test.py"], introspect = False)
        logger = SimpleLogger()
        epydoc_log.register_logger(logger)
        checker = DocChecker(docindex)
        check_result = checker.check(DocChecker.PARAM | DocChecker.DESCR | DocChecker.TYPE)
        
        if not check_result:    
            print logger.output
            return self.error(logger.output)
        else:
            return self.success()

class SimpleLogger(epydoc_log.Logger):
    """
    Logger to get Epydoc output in case of failure
    """
    def __init__(self):
        self.output = ''
        
    def log(self, _, message):
        """
        
        :param message: message to log
        :type message: string
        """
        if not message[-1] == '\n':
            message += '\n'
        self.output += message
            
    