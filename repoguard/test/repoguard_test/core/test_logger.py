# pylint: disable=E1101
# E1101: Pylint cannot find pytest.raises
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
Tests of the LoggerFactory class.
"""


import logging
import pytest

from repoguard.core.logger import LoggerFactory


_LOGGER_CONFIG = """
output = /path/to/log/dir
default = ERROR
max_bytes = 10
backup_count = 2

repoguard.core.checker = FAILURE
repoguard.core.validator = INFO

repoguard.foo.bar = 42

repoguard.interpolation = ${repoguard.foo.bar}
"""


class TestLoggerFactory(object):
    
    def setup_method(self, _):
        # Make sure that it has not been yet instantiated
        LoggerFactory._instance = None
        logging.root = logging.RootLogger(logging.WARNING)
        logging.Logger.root = logging.root
        
        self.factory = LoggerFactory(config=_LOGGER_CONFIG.splitlines())
        assert self.factory.create().root.handlers
        assert id(self.factory) == id(LoggerFactory())

    def test_create_default(self):
        logger = self.factory.create()
        assert logger.root.handlers[0].level == logging.ERROR
        assert len(logger.handlers) == 0
        assert len(logger.root.handlers) >= 1
        
    def test_create_undefined(self):
        logger = self.factory.create("DEFAULT")
        assert logger.root.handlers[0].level == logging.ERROR
        if len(logger.root.handlers) == 2:
            assert logger.root.handlers[1].level == logging.NOTSET
        
    def test_create_defined(self):
        logger = self.factory.create("repoguard.core.validator")
        assert logger.root.handlers[0].level == logging.INFO
        
        logger = self.factory.create("repoguard.foo.bar")
        assert logger.root.handlers[0].level == 42
        
    def test_create_override(self):
        logger = self.factory.create("repoguard.core.validator", override=logging.INFO)
        assert logger.root.handlers[0].level == logging.INFO
        
    def test_create_unknown_error_level(self):
        pytest.raises(ValueError, 
            self.factory.create, "repoguard.core.checker")
        
    def test_create_from_variable_def(self):
        logger = self.factory.create("repoguard.interpolation")
        assert logger.root.handlers[0].level == 42
