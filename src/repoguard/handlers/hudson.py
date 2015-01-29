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
Handler to trigger a build process in hudson.
"""


from urllib import urlencode, urlopen

from repoguard.core.module import Handler, HandlerConfig, String


class Config(HandlerConfig):
    class types(HandlerConfig.types):
        url = String
        token = String(optional=True)
        
class Hudson(Handler):
    """
    Hudson handler for build triggering.
    """
    
    __config__ = Config
    
    def _summarize(self, config, _):
        """
        Method is called after all checks where runned.
        
        :param config: The config that has to be used.
        :type config: Config instance.
        """
        
        if config.token:
            params = urlencode({'token' : config.token})
        else:
            params = None
        urlopen(config.url, params).close()
