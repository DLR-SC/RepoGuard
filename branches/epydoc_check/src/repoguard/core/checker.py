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
Module that contains the main RepoGuard class.
"""

import os
import re

from repoguard.core import constants
from repoguard.core.logger import LoggerFactory
from repoguard.core.config import ProjectConfig
from repoguard.core.transaction import Transaction
from repoguard.core.protocol import Protocol
from repoguard.core.validator import ConfigValidator
from repoguard.core.module import CheckManager, HandlerManager

class RepoGuard(object):
    """
    Main RepoGuard class.
    """
    
    def __init__(self, hook, repository_path):
        """
        Constructor.
        
        :param hook: The hook that has to be executed. Valid values are 
                     constants.PRECOMMIT or constants.POSTCOMMIT.
        :type hook: constants.PRECOMMIT, constants.POSTCOMMIT.
        
        :param transaction_name: The name of the current transaction.
        :type transaction_name: string
        
        :param repository_path: The path to the current repository.
        :type repository_path: string
        """
        
        self.hook = hook
        self.repository_path = repository_path

        self.checks = CheckManager()
        self.handlers = HandlerManager()
        self.result = constants.SUCCESS
        self.main = None
        self.transaction = None
        
        self.logger = LoggerFactory().create(self.__module__)
        
    def load_transaction(self, name):
        """
        Load the transaction with the given name.
        
        :param name: The name of the current transaction.
        :type name: string
        """
        
        self.transaction = Transaction(self.repository_path, name)
        
    def load_config(self, tpl_dirs, config):
        """
        Load the project configuration.
        
        :param tpl_dirs: Path lists where all templates are located.
        :type tpl_dirs: string
                            
        :param config: The path or a splittedline project configuration string.
        :type config: string
        """
        
        self.logger.debug("Loading project configuration...")
        hooks_path = os.path.join(self.repository_path, "hooks")
        self.main = ProjectConfig(config, hooks_path, tpl_dirs)
        self.logger.debug("Project configuration loaded.")
        
    def validate(self):
        """
        Runs the internal validation process of the current loaded 
        configuration.
        
        :return: Returns the status code of the validator. succes = 0, error > 0
        :rtype: integer
        """
        
        validator = ConfigValidator(excepts=True)
        return validator.validate(self.main)
    
    def _default_regex(self):
        """
        Generates the default regex expression that manches all files, that are
        not covered by any profile.
        
        :return: Regex expression that matches all uncovert files.
        :rtype: string
        """
        
        files = set(self.transaction.get_files().keys())
        for profile in self.main.profiles:
            self.transaction.profile = profile.regex or "^$"
            files -= frozenset(self.transaction.get_files().keys())
            
        # generation of the regex for all files that are left.
        return '^(%s)$' % '|'.join([re.escape(item) for item in files])
    
    def run(self):
        """
        Execution of the checking _process and handler handling.
        It is recommended to call the load_config method before 
        calling this method.
        
        :return: Returns the _process result as a constant string.
        :rtype: constants.SUCCESS, constants.ERROR
        """
        
        self.logger.debug("Running run...")
        default = self._default_regex()
        self.logger.debug("Default regex: %s", default)
        
        # Process executing
        for profile in self.main.profiles:
            self.logger.debug("Running profile '%s'...", profile.name)
            self.transaction.profile = profile.regex or default
        
            # if there are no files in this profile continue
            if not self.transaction.get_files():
                self.logger.debug("Profile '%s' skipped.", profile.name)
                continue
            
            process = profile.get_process(self.hook)
            if not process:
                self.logger.debug(
                    "%s process skipped." % self.hook.capitalize()
                )
                continue
            
            protocol = Protocol(profile.name)
            # run the configured checks
            for name, config, interp in process.checks:
                self.logger.debug("Loading check %s...", name)
                check = self.checks.fetch(name, self.transaction)
                self.logger.debug("Starting check %s...", name)
                entry = check.run(config, interp)
                self.logger.debug(
                    "Check %s finished with %s.", name, entry.result
                )
                protocol.append(entry)
                
                # run the configured handlers when a message was returned 
                if entry.msg:
                    self.logger.debug(
                        "Running handler after check %s...", entry.check
                    )
                    self.handlers.singularize(self.transaction, process, entry)
                    self.logger.debug(
                        "Handler after check %s finished.", entry.check
                    )
                
                # cancel the _process chain when an abortonerror was detected.
                if interp == constants.ABORTONERROR and not protocol.success:
                    msg = "Profile %s aborted after check %s."
                    self.logger.debug(msg, profile.name, entry.check)
                    break
            
            # cumulativ execution of all handlers.
            self.logger.debug("Running handler summarize...")
            self.handlers.summarize(self.transaction, process, protocol)
            self.logger.debug("Handler summarize finished.")
            
            if not protocol.success:
                self.result = constants.ERROR
            self.logger.debug("Profile %s finished.", profile.name)
        
        self.logger.debug("Cleaning up transaction.")
        self.transaction.cleanup()
        self.logger.debug("Run finished with %s.", self.result)
        return self.result