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
Logging factory facility to load logging config from a config file.
"""


import logging
import sys

from configobj import ConfigObj

from repoguard.core import constants


class LoggerFactory(object):
    """
    Singleton logger factory object for the instantiation of loggers and the
    automatic configuration through the configuration file.
    """
    
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        """
        This method is repsonsible for the singleton handling.
        """
        
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def __init__(self, **kwargs):
        """
        Constructor.
        
        Accepts an dictionary for the configuration with the keys:
        - config: To define the path to the configuration file or an dict.
        - default: To define the default logging level.
        """
        
        path = kwargs.get('config', constants.LOGGER_PATH)
        self.config = ConfigObj(
            path, encoding='UTF-8', interpolation='template'
        )
        self.default = kwargs.get('default', logging.ERROR)
        
        logging.basicConfig(stream=sys.stderr)
        
    @staticmethod
    def _check_level(level):
        """
        Checks and converts the given level to an logging level.
        
        :param level: The level that has to be checked and converted.
        :type level: integer, string
        
        :return: The converted level.
        :rtype: integer
        """
        
        if hasattr(logging, str(level)):
            return getattr(logging, level)
        
        try:
            level = int(level)
        except ValueError:
            raise ValueError("Unknown log level '%s'" % level)
        return level
        
    def create(self, name="default", propagate=1, override=None):
        """
        Creates a logger with the given name and set the log level from the
        configuration file.
        
        :param name: Logger name.
        :type name: string
        
        :param propagate: If this evaluates to false, logging messages are not 
                          passed by this logger or by child loggers to higher 
                          level (ancestor) loggers.
        :type propagate: boolean
        
        :param override: If this parameter is set the level from the
                         configuration file will be overritten.
        :type override: integer
        
        :return: Returns a new logger with the given name.
        :rtype: Logger
        """
        
        logger = logging.getLogger(name)
        logger.propagate = propagate
        
        if not override is None:
            level = override
        else:
            default = self.config.get('default', self.default)
            level = self.config.get(name, default)
        level = self._check_level(level)
        logger.setLevel(level)
        return logger
