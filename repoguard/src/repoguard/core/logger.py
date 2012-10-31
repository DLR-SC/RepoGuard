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
Logging factory facility to load logging _configuration from a _configuration file.
"""


import logging
from logging import handlers
import os
import sys

from configobj import ConfigObj

from repoguard.core import constants


class LoggerFactory(object):
    """
    Singleton logger factory object for the instantiation of loggers and the
    automatic configuration through the configuration file.
    
    Every logger obtains by C{create} has two handlers:
    - a stream handler which outputs everything to C{sys.stderr}
      - Specify 'default' to define the default logging level. Use the logging module constant names to to this.
      - Specify '<LOGGER_NAME> = <LOG_LEVEL>' to set the log level for a specifically named logger.
    - a file handler which outputs everything to a log file
      - Specify 'output' for a custom output directory.
      - Specify 'max_bytes' to define the size of the logging file
      - Specify 'backup_count' to define the maximum number of created logging files
      - Really everything is logged to this file.
    """
    
    _MESSAGE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    _instance = None
    
    def __new__(cls, **kwargs):
        """
        This method is responsible for the singleton handling.
        Accepts an dictionary for configuration:
        - config: To define the path to the configuration file or an dict.
        - default: To define the default logging level.
        """
        
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            
            path = kwargs.get("config", constants.LOGGER_PATH)
            cls._configuration = ConfigObj(
                path, encoding="UTF-8", interpolation="template"
            )
            
            cls.default = kwargs.get("default", logging.ERROR)
                        
            cls._stream_handler = cls._configure_stream_handler()
            cls._file_handler = cls._configure_file_handler()
            cls._configure_root_logger()
        return cls._instance
    
    @classmethod
    def _configure_stream_handler(cls):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(cls._MESSAGE_FORMAT))
        handler.setLevel(cls.default)
        return handler
    
    @classmethod
    def _configure_file_handler(cls):
        name = "%s.log" % constants.NAME
        output_dir_path = cls._configuration.get("output", "")
        if not os.path.exists(output_dir_path):
            output_dir_path = constants.CONFIG_HOME
        
        if os.path.exists(output_dir_path):
            log_file_path = os.path.join(output_dir_path, name)
            max_bytes = long(cls._configuration.get("max_bytes", "5242880"))
            backup_count = int(cls._configuration.get("backup_count", "3"))
            handler = handlers.RotatingFileHandler(
                log_file_path, encoding="UTF-8", maxBytes=max_bytes, backupCount=backup_count)
            handler.setFormatter(logging.Formatter(cls._MESSAGE_FORMAT))
            handler.setLevel(logging.NOTSET)
            return handler

    @classmethod
    def _configure_root_logger(cls):
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        logger.addHandler(cls._stream_handler)
        if not cls._file_handler is None:
            logger.addHandler(cls._file_handler)
        else:
            logger.error("Specified output directory does not exist.")
            
    @staticmethod
    def _check_level(level):
        if hasattr(logging, str(level)):
            level = getattr(logging, level)
        else:
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
                         configuration file will be overridden.
        :type override: integer
        
        :return: Returns a new logger with the given name.
        :rtype: Logger
        """
        
        logger = logging.getLogger(name)
        logger.propagate = propagate
        
        if not override is None:
            level = override
        else:
            default = self._configuration.get("default", self.default)
            level = self._configuration.get(name, default)
        level = self._check_level(level)
        self._stream_handler.setLevel(level)
        return logger
