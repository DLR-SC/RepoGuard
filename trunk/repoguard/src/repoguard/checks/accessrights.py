# pylint: disable-msg=W0232,R0903,C0103
# W0232,R0903,C0103: To allow configuration definition with class type.
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
Check access rights on files. 
"""


from repoguard.core.module import Check, ConfigSerializer, Array, String


class Config(ConfigSerializer):
    """
    AccessRights configuration class that contains all attributes of the
    configuration.
    """
    
    class types(ConfigSerializer.types):
        """
        AccessRights Parameters.
        """
        
        check_files = Array(String, optional=True, default=[".*"])
        ignore_files = Array(String, optional=True, default=[])
        allow_users = Array(String, optional=True, default=[])
        deny_users = Array(String, optional=True, default=[])

        
class AccessRights(Check):
    """
    The AccessRights check can allow or deny the access on a repository path.
    The path of the repository is associated with the profile in which in 
    the AccessRights check is used.
    """
    
    __config__ = Config

    def _run(self, config):
        """
        Method is called when the check has to run.
        
        :param config: The configuration that has to be used by the check.
        :type config: Config
        
        :return: Returns an error or success messages by calling the success
                 or error method.
        :rtype: Tuple that contains the success or error code and message.
        """
        
        userid = self.transaction.user_id
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        
        # rule definition
        deny = userid in config.deny_users 
        allow = userid in config.allow_users
        
        # if users not empty
        deny = deny or config.allow_users and not allow or allow and deny
        allow = allow or config.deny_users and not deny
        
        if len(files) > 0:
            if files and deny or not allow:
                msg = "You don't have rights to edit these files: \n - "
                msg += "\n - ".join(files.keys())
                return self.error(msg)
        return self.success()
