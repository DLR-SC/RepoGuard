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
Checks if a log message contains one or more valid MANTIS ID,
with a MANTIS ID <#> that is set to status 'in_progress' and
handled by the correct user.
"""

from repoguard.modules import mantis as base
from repoguard.core.module import Check, Boolean

class Config(base.Config):
    class types(base.Config.types):
        check_in_progress = Boolean(optional=True)
        check_handler = Boolean(optional=True)

class Mantis(Check):
    
    __config__ = Config

    def _run(self, config):
        mantis = base.Mantis(config)
        issues = mantis.extract_issues(self.transaction.commit_msg)
        
        msg = "Invalid log message: The message must contain 'MANTIS ID <#>'!"
        if len(issues) == 0:
            return self.error(msg)
    
        for issue in issues:
            if not mantis.issue_exists(issue):
                msg = "MANTIS ID %s not found!" % issue
                return self.error(msg)
    
            if config.check_in_progress:
                status = mantis.issue_get_status(issue)
                if status != "in_progress":
                    msg = "MANTIS ID %s is not 'in_progress'!" % issue
                    return self.error(msg)
    
            if config.check_handler:
                handler = mantis.issue_get_handler(issue)
    
                if self.transaction.user_id != handler:
                    msg = "You are not the handler of MANTIS ID %s!" % issue
                    return self.error(msg)
    
        return self.success()
