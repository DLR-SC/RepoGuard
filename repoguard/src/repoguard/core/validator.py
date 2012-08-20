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
Module that contains the main validator class.
"""

import re

from validate import Validator, ValidateError

from repoguard.core import constants
from repoguard.core.module import CheckManager, HandlerManager
from repoguard.core.logger import LoggerFactory


class ConfigValidator(Validator):
    """
    The _config validator class validates a given ConfigObj object.
    """
    
    def __init__(self, propagate=1, override=None, excepts=False):
        """
        Constructor.
        
        :param propagate: If this evaluates to false, logging messages are not 
                          passed by this logger or by child loggers to higher 
                          level (ancestor) loggers.
        :type propagate: boolean
        
        :param override: Overrides the default log level for the intern logger.
        :type override: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        
        Validator.__init__(self)
        
        self.check_regex = re.compile(constants.CHECK_REGEX)
        self.handler_regex = re.compile(constants.HANDLER_REGEX)
        
        self.default_profile = False
        self.main = None
        self.errors = 0
        self.excepts = excepts
        
        self.valid_checks = []
        self.valid_handlers = []
        
        self.logger = LoggerFactory().create(
            self.__module__, propagate, override
        )
        
        self.check_manager = CheckManager()
        self.handler_manager = HandlerManager()
    
    def validate(self, main):
        """
        Validates the given ConfigObj object.
        
        :param main: The configuration that has to be validated.
        :type main: ConfigObj
        
        :raise ValidateError: When a the given ConfigObj object is not in a 
                              valid form a ValidateError is raised.
                              
        **Usage**
        
        >>> main = ConfigObj()
        >>> validator = ConfigValidator()
        >>> try:
        >>>    validator.validate(main)
        >>> except ValidateError, exc:
        >>>    print exc
        """
        
        self.default_profile = False
        self.errors = 0
        self.main = main  

        self.logger.info("Starting validation...")
        try:            
            if 'extends' in self.main:
                self.check('string', self.main['extends'])
            
            self.logger.info("Validating profiles...")
            if 'profiles' in self.main:
                for profile, config in self.main['profiles'].iteritems():
                    self._validate_profile(profile, config)
            if not self.default_profile:
                self.exception("No default profile found.")
            
            self.logger.info("Validating check configurations...")
            if 'checks' in self.main:
                self._validate_checks(self.main['checks'])
            else:
                self.logger.info("No check configurations defined.")
                
            self.logger.info("Validating handler configurations...")
            if 'handlers' in self.main:
                self._validate_handlers(self.main['handlers'])
            else:
                self.logger.info("No handler configurations defined.")
        finally:
            self.logger.info("Validation finished with %s.", self.errors)
        return self.errors
    
    def _validate_checks(self, config):
        """
        Validates all checks.
        """

        for check, conf in config.iteritems():
            if not check in self.check_manager.available_modules:
                msg = "The check '%s' is not available. Check the spelling."
                self.exception(msg % check)
                continue
            for check_config in conf.values():
                self._validate_check_config(check, check_config)
            
    def _validate_handlers(self, config):
        """
        Validates all handlers.
        """
        
        for handler, conf in config.iteritems():
            if not handler in self.handler_manager.available_modules:
                msg = "The handler '%s' is not available. Check the spelling."
                self.exception(msg % handler)
                continue
            for handler_config in conf.values():
                self._validate_handler_config(handler, handler_config)
        
    def _validate_profile(self, profile, config):
        """
        Validates a given profile.
        
        @param profile: The profile that has to be validated.
        @type profile: list<string>
        
        @param _config: The main _config.
        @type _config: ConfigObj
        """
        
        if 'regex' not in config:
            if self.default_profile:
                msg = "Default profile already exists. " \
                    + "Only one default profile is allowed."
                self.exception(msg)
            else:
                self.default_profile = True
                self.logger.info("Default profile found.")
        else:
            self.check('string', config['regex'])
        
        for commit in constants.HOOKS:
            if commit in config:                  
                self._validate_profile_commit(profile, commit, config[commit])
        
    def _validate_profile_commit(self, profile, commit, config):
        """
        Validates a given precommit or postcommit section.
        
        @param profile: The profile that has to be checked.
        @type profile: string
        
        @param commit: The pre or postcommit section of the profile.
        @type commit: constants.PRECOMMIT, constants.POSTCOMMIT
        
        @param _config: The main ConfigObj object.
        @type _config: ConfigObj
        """
        
        for key in ('checks', 'success', 'error'):
            if key not in config:
                msg = "No %s found for profile '%s' in %s process"
                self.exception(msg % (key, profile, commit))
        
        if 'default' in config and not config['default'] in constants.INTERPS:
            msg = "Unknown default value '%s' in profile '%s'"
            self.exception(msg % (config['default'], profile))
                                  
        self._validate_process_check(config['checks'])
        self._validate_process_handler(config['success'])
        self._validate_process_handler(config['error'])
        
    def _validate_process_check(self, process):
        """
        Validates the checks of the given process.
        
        @param process: The process that contains the checks.
        @type process: dict
        """
        
        process = self.check('string_list', process)
        for check in process:
            result = self.check_regex.search(check)
            name, config, interp = result.group("name", "config", "interp")
            if not name:
                self.logger.error("Empty checks are not allowed.")
            
            if config:
                try:
                    self.main['checks'][name][config]
                except KeyError:
                    msg = "Configuration '%s' for check '%s' is not defined"
                    self.exception(msg % (config, name))
            else:
                self._validate_emtpy_check_config(name)
            
            if interp and not interp in constants.INTERPS:
                msg = "Error interpretation '%s' is not valid."
                self.exception(msg % interp)
            
    def _validate_process_handler(self, process):
        """
        Validates the handlers of the given process.
        
        @param process: The process that contains the handlers.
        @type process: dict
        """
        
        process = self.check('string_list', process)
        for handler in process:
            result = self.handler_regex.search(handler)
            name, config = result.group("name", "config")
            
            if not name:
                self.logger.error("Empty handlers are not allowed.")
            
            if config:
                try:
                    self.main['handlers'][name][config]
                except KeyError:
                    msg = "Configuration '%s' for check '%s' is not defined" 
                    self.exception(msg % (config, name))
            else:
                self._validate_empty_handler_config(name)
        
    def _validate_check_config(self, check, config):
        """
        Validates the _config that is specified by the given check.
        
        @param check: The check of which the _config has to be validated.
        @type check: string
        
        @param config: The _config of the check.
        @type config: Section
        """
        
        try:
            check_class = self.check_manager.load(check)
            check_class.__config__.from_config(config)
        except ImportError, exc:
            msg = "Unable to load check '%s'."
            self.exception(msg % check)
        except (ValueError, KeyError), exc:
            msg = "Validation error in check '%s': '%s'"
            self.exception(msg % (check, str(exc)))
            
    def _validate_emtpy_check_config(self, check):
        """
        Validates the given check with an empty main dictionary.
        
        @param check: The name of the check that has to been checked.
        @type check: C{string}
        
        @raise ValidateError: Is raised when the given check can not be 
                              validated with an empty main.
        """
        
        self._validate_check_config(check, {})
    
    def _validate_handler_config(self, handler, config):
        """
        Validates the _config for given handler.
        
        @param handler: The handler of which the _config has to be validated.
        @param handler: string
        
        @param _config: The _config of the handler.
        @type _config: Section
        """

        try:
            handler_class = self.handler_manager.load(handler)
            handler_class.__config__.from_config(config)
        except ImportError:
            msg = "Unable to load handler '%s'."
            self.exception(msg % handler)
        except (ValueError, KeyError), exc:
            msg = "Validation error in handler '%s': '%s'"
            self.exception(msg % (handler, str(exc)))
            
    def _validate_empty_handler_config(self, handler):
        """
        Validates the given handler with an empty main dictionary.
        
        @param check: The name of the handler that has to been checked.
        @type check: C{string}
        
        @raise ValidateError: Is raised when the given handler can not be 
                              validated with an empty main.
        """
        
        self._validate_handler_config(handler, {})
        
    def exception(self, msg):
        """
        Custom exception method that is used for logging, stats and exceptions.
        
        :param msg: The message for the occurred exception.
        :type msg: string
        """
        
        self.logger.exception(msg)
        if self.excepts:
            raise ValidateError(msg)
        self.errors += 1