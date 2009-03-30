# pylint: disable-msg=

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

""" executes an svndbadmin update for viewvc 1.1 """

from __future__ import with_statement
from repoguard.core import process
from repoguard.core.module import Handler, HandlerConfig, String



class Config(HandlerConfig):
    """ Class to handle configuration parameters
    """
    class types(HandlerConfig.types):
        """ Class to handle the svndbadmin_bin config parameter
        """
        svndbadmin_bin = String

class ViewVC(Handler):
    """ 
    
    """
    __config__ = Config
    
    
    def __init__(self):
        pass
                
    def _summarize(self, config, _):
        """ Method uses external binary svndbadmin from viewvc 
            to update the viewvc database with changes 
            
            :param config: The config that has to be used.
            :type config: Config instance.
        """
        
        repo_path = self.transaction.repos_path
        svndbadmin_bin = config.svndbadmin_bin
        command = svndbadmin_bin + " update " + repo_path

        process.execute(command)

