# pylint: disable-msg=W0613, W0612, W0232

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
Append the message to one or more Mantis issues as note and update the 
SVNRevision field.
"""

from repoguard.modules import mantis as base
from repoguard.core.module import Handler, HandlerConfig, String

class Config(HandlerConfig, base.Config):
    class types(HandlerConfig.types, base.Config.types):
        custom_field = String(optional=True)


class Mantis(Handler):
    """
    Mantis handler add all generated log messages to th given mantis issue.
    """
    
    __config__ = Config
    mantis = None
    
    def add_note(self, issue, msg):
        """
        Adds a note to the given issue with the given msg.
        
        :param issue: Issue id.
        :type issue: integer
        """
        
        self.logger.debug("Adding note to issue %s:\n%s", issue, msg)
        self.mantis.issue_add_note(issue, msg)
        
    def set_revision(self, issue, custom_field, revision):
        """
        Set the revision on the given field.
        
        :param custom_field: The field where the revision has to be set.
        :type custom_field: string
        
        :param revision: The current revision.
        :type revision: integer
        """
        
        self.logger.debug("Setting custom field '%s'.", custom_field)
        self.mantis.issue_set_custom_field(issue, custom_field, revision)
        
    def _summarize(self, config, protocol):
        """
        Method writes a note and set custom field for the issues containt in
        the transaction.
        
        :param config: Configuration that has to be used.
        :type config: Config
        
        :param protocol: The protocol that has to be add as note.
        :type protocol: Protocol
        """
        
        self.mantis = base.Mantis(config)
        
        issues = self.mantis.extract_issues(self.transaction.commit_msg)
        self.logger.debug("Mantis ids %s found", ", ".join(issues))
        
        msg = "\n\n".join([entry.msg for entry in protocol])
        
        for issue in issues:
            self.logger.debug("Checking if issue %s exists", issue)
            if self.mantis.issue_exists(issue):
                self.add_note(issue, msg)
                if config.custom_field is not None:
                    revision = self.transaction.revision
                    self.set_revision(issue, config.custom_field, revision)
                self.logger.debug("Issue %s finished.", issue)
        self.logger.debug("Mantis handler finished.")