# pylint: disable-msg=W0704
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

""" Create a log message. """

from urllib import urlencode
from datetime import datetime

from repoguard.core.module import Check, ConfigSerializer, String

class ViewVC(ConfigSerializer):
    url = None
    root = None
    view = "rev"
    
    class types(ConfigSerializer.types):
        url = String
        root = String
        view = String(optional=True, default="rev")
        
    def encode(self, revision):
        params = {'view' : self.view, 'root' : self.root, 'revision' : revision}
        return "%s?%s" % (self.url, urlencode(params))

class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        viewvc = ViewVC(optional=True)
        
class Log(Check):
    
    __config__ = Config
    
    def _run(self, config):
    
        files = self.transaction.get_files()
    
        msg = "Date: %s\n" % datetime.now().strftime("%H:%M - %d.%m.%Y")
        msg += "Author: " + self.transaction.user_id + "\n"
        msg += "Revision: " + self.transaction.revision + "\n\n"
    
        if config.viewvc:
            msg += config.viewvc.encode(self.transaction.revision) + "\n\n"
    
        msg += "Modified Files:\n"
        for filename, attribute in files.iteritems():
            msg += "%s\t%s\n" % (attribute, filename)
    
        msg += "\n"
    
        msg += "Log Message:\n"
        msg += self.transaction.commit_msg
        msg += "\n"
    
        return self.success(msg)
    