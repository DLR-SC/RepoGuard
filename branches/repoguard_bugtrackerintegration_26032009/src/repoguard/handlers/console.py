# pylint: disable-msg=W0613, W0602

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

""" Simply print the message to the console. Either to stdout or to stderr. """

import sys

from repoguard.core import constants
from repoguard.core.module import Handler

class Console(Handler):
    """
    Prints the incoming messages on stdout or stderr.
    """
    
    #Output target definition.
    out = {
        constants.SUCCESS : sys.stdout,
        constants.WARNING : sys.stderr,
        constants.ERROR : sys.stderr,
        constants.EXCEPTION : sys.stderr
    }
    pattern = "\n%s\n" + "-" * 80 + "\n"
    
    def _singularize(self, config, entry):
        self.out[entry.result].write(self.pattern % entry)
        
    def _summarize(self, config, protocol):
        self.out[protocol.result].write(self.pattern % protocol)
