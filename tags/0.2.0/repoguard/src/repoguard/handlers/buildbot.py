# pylint: disable-msg=E1101,W0232
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
Handler that triggers the build bot for triggering the build process.
Mainly used as success handler.
"""

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor

from repoguard.core.module import Handler, HandlerConfig, String, Integer

class Config(HandlerConfig):
    class types(HandlerConfig.types):
        url = String(optional=True, default="localhost")
        port = Integer(optional=True, default=8007)
        user = String
        password = String

class BuildBot(Handler):
    
    __config__ = Config

    stop = lambda client: reactor.stop()

    def send_change(self, remote):
        who = self.transaction.user_id
        files = self.transaction.get_files().keys()
        comments = self.transaction.commit_msg.splitlines()
        change = {'who': who, 'files': files, 'comments': comments}
        remote.callRemote('addChange', change).addCallback(self.stop)
        self.logger.debug("%s: %s", who, " ".join(files))
        
    def _summarize(self, config, _):
        client = pb.PBClientFactory()
        cred = credentials.UsernamePassword(config.user, config.password)
        result = client.login(cred)
        reactor.connectTCP(config.url, config.port, client)
        result.addCallback(self.send_change).addErrback(self.stop)
        reactor.run()