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
Checks if a log message contains one or more valid MANTIS ID,
with a MANTIS ID <#> that is set to status 'in_progress' and
handled by the correct user.
"""

from repoguard.modules import bugtracker as base
from repoguard.core.module import Check, Boolean, ModuleManager

class Config(base.Config):
    """
    Basic check bug tracking configuration.
    """
    
    class types(base.Config.types):
        """
        Types that are contained in the initialized configuration.
        """
        
        check_in_progress = Boolean(optional=True, default=False)
        check_handler = Boolean(optional=True, default=False)
        allow_multiple = Boolean(optional=True, default=True)

class BugTracker(Check):
    """
    General bug tracker check.
    """
    
    __config__ = Config
    
    def __init__(self, transaction):
        """
        Constructor.
        
        :param transaction: The current transaction of the commit.
        :type transaction: Transaction object.
        """
        
        Check.__init__(self, transaction)
        
        self.bugtracker = None
        self.manager = ModuleManager()

    def _run(self, config):
        """
        Runs the check with the given config.
        
        :param config: The config that has to be used by the check.
        :type config: Config object.
        """
        
        self.bugtracker = self.manager.load(self.load_info.name)(config)
        issues = config.parse_commit_msg(self.transaction.commit_msg)
        
        msg = "Invalid log message: The message must contain the pattern '%s'!"
        if len(issues) == 0:
            return self.error(msg % config.pattern)
        
        if not config.allow_multiple and len(issues) > 1:
            return self.error("Commit to multiple issues is not allowed.")
    
        for issue in issues:
            if not self.bugtracker.issue_exists(issue):
                return self.error("Bug ID %s not found!" % issue)
    
            if config.check_in_progress:
                status = self.bugtracker.get_status(issue)
                if status != "in_progress":
                    return self.error("Bug ID %s is not 'in_progress'!" % issue)
    
            if config.check_handler:
                handler = self.bugtracker.get_handler(issue)
                if self.transaction.user_id != handler:
                    msg = "You are not the handler of bug ID %s!" % issue
                    return self.error(msg)
    
        return self.success()