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
Test methods for the LoggerFactory class.
"""

import logging
import py.test
import tempfile

from repoguard.core.logger import LoggerFactory

logger_config = """
output = %s
default = ERROR

repoguard.core.checker = FAILURE
repoguard.core.validator = INFO

repoguard.foo.bar = 42

repoguard.interpolation = ${default}
""" % tempfile.tempdir

class TestLoggerFactory(object):
    
    @classmethod
    def setup_class(cls):
        cls.factory = LoggerFactory(config=logger_config.splitlines())
        
    def test_create(self):
        logger = self.factory.create()
        assert logger.level == logging.ERROR
        
        logger = self.factory.create("DEFAULT")
        assert logger.level == logging.ERROR
        
        logger = self.factory.create("repoguard.core.validator")
        assert logger.level == logging.INFO
        
        logger = self.factory.create(
            "repoguard.core.validator", override=logging.NOTSET
        )
        assert logger.level == logging.NOTSET
        
        logger = self.factory.create("repoguard.foo.bar")
        assert logger.level == 42
        
        py.test.raises(
            ValueError, self.factory.create, "repoguard.core.checker"
        )
        
        logger = self.factory.create("repoguard.interpolation")
        assert logger.level == logging.ERROR