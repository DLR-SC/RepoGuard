# pylint: disable-msg=W0602, W0613

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

""" Log the message into a file. """

from __future__ import with_statement

import os.path

from repoguard.core.module import Handler, HandlerConfig, String

SEPARATOR = "\n====================\n"

class Config(HandlerConfig):
    class types(HandlerConfig.types):
        file = String

class File(Handler):
    
    __config__ = Config
        
    def _write(self, config, msg):
        if not os.path.exists(os.path.dirname(config.file)):
            msg = "Could not write logfile because directory does not exist: %r"
            raise IOError(msg % os.path.dirname(config.file))
    
        with open(config.file, "a") as fp:
            fp.write(str(msg))
            fp.write(SEPARATOR)
        
    def _singularize(self, config, entry):
        self._write(config, entry)
        
    def _summarize(self, config, protocol):
        self._write(config, protocol)
