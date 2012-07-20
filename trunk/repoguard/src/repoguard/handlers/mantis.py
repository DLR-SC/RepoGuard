# pylint: disable=C0103,R0903,W0232
# C0103,R0903,W0232: General problem with configuration definition of 
#                    handler/checks.
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
Append the message to one or more Mantis issues as note and update the 
SVNRevision field.
"""


import urllib2

from repoguard.modules import mantis as base
from repoguard.core.module import Handler, HandlerConfig, String


class Config(HandlerConfig, base.Config):
    """ Handler-specific configuration which extends the one 
    of the Mantis base module. """
    
    class types(HandlerConfig.types, base.Config.types):
        """ 
        custom_field: Used to set the revision (optionally).
        vcs_sync_url: URL which is called to synchronize Mantis issues 
                      with the VCS revision history (optionally).
        The URL to call should be as follows:
        http(s)://<HOSTNAME>/<PATH_TO_MANTIS_ROOT>/plugin.php?
        page=Source/import&id=<PROJECT_ID>
        e.g.: https://myserver.dom/mantis/plugin.php?page=Source/import&id=12
        """
        
        custom_field = String(optional=True)
        vcs_sync_url = String(optional=True)


class Mantis(Handler):
    """
    Mantis handler add all generated log messages to the given Mantis issue.
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
        
    def sychronize_with_vcs(self, vcs_sync_url):
        """ Synchronizes the Mantis issues and the VCS history. """
        
        file_object = urllib2.urlopen(vcs_sync_url)
        content = file_object.read()
        self.logger.debug(content)
        file_object.close()
        
    def _summarize(self, config, protocol):
        """
        Method writes a note and set custom field 
        for the issues contained in the transaction.
        
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
                if config.vcs_sync_url is None:
                    self.add_note(issue, msg)
                if config.custom_field is not None:
                    revision = self.transaction.revision
                    self.set_revision(issue, config.custom_field, revision)
                self.logger.debug("Issue %s finished.", issue)
        
        if not config.vcs_sync_url is None:
            self.sychronize_with_vcs(config.vcs_sync_url)
        self.logger.debug("Mantis handler finished.")
