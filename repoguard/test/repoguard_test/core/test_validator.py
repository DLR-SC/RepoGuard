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


""" Provides tests for the configuration validation. """


import pkg_resources

from repoguard.core.config import ProjectConfig
from repoguard.core.module import Handler
from repoguard.core.validator import ConfigValidator


_SUCCESS_CONFIG = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=PyLint..warning, CaseInsensitiveFilenameClash
        success=Console,
        error=Console,
        
        [[[postcommit]]]
        checks=UnitTests, Checkout.default
        success=File.default, Console
        error=File.default, Console
        
    [[branches]]
    regex=^.*/branches/.*$
        [[[precommit]]]
        default=warning
        checks=Keywords.default.delayonerror, RejectTabs
        success=Mail.branches,
        error=Console, Mail.branches
    
[checks]        
    [[Checkout]]
        [[[default]]]
        entries=entry1,
        entries.entry1.source=test.java
        entries.entry1.destination=.
    [[Keywords]]
        [[[default]]]
        keywords=Date,
        
[handlers]
    [[Mail]]
        [[[branches]]]
        addresses=all@repoguard.org,
        
    [[File]]
        [[[default]]]
        file=default.log
""".splitlines()


_ERROR_CONFIG = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=PyLint.default,
        success=Console.success,
        error=Console.error,
        
        [[[postcommit]]]
        checks=UnitTests, Checkout.default
        success=File.default, Console.success
        error=File.default, Console.error

[checks]        
    [[Checkout]]

[handlers]
    [[Console]]
        [[[success]]]
        [[[error]]]
        
    [[File]]
        [[[default]]]
        file=${hooks}/repoguard.log
""".splitlines()


class TestConfigValidator(object):
    
    @classmethod
    def setup_class(cls):
        cls.validator = ConfigValidator()
        
        # Setting pkg_resources mocks
        all_handler_checks = {"PyLint": 0, "AccessRights": 0, "ASCIIEncoded": 0,
                              "CaseInsensitiveFilenameClash": 0, "Checkout": 0, 
                              "Checkstyle": 0, "Keywords": 0, "Log": 0, 
                              "RejectTabs": 0, "UnitTests": 0, 
                              "XMLValidator": 0, "File": 0, "Console": 0, 
                              "Mail": 0, "Mantis": 0, "BuildBot": 0, 
                              "Hudson": 0}
        pkg_resources.load_entry_point = lambda _, __, ___: Handler
        pkg_resources.get_entry_map = lambda _, __: all_handler_checks

    def test_validate_for_success(self):
        
        config = ProjectConfig(_SUCCESS_CONFIG, "hooks")
        assert self.validator.validate(config) == 0
        
    def test_validate_for_error(self):
        config = ProjectConfig(_ERROR_CONFIG, "hooks")
        result = self.validator.validate(config)
        assert result == 2
