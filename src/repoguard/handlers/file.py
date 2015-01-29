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


""" Log the message into a file. """


from repoguard.core.module import Handler, HandlerConfig, String


class Config(HandlerConfig):
    """ Configuration parameters. """
    # Normal errors for RepoGuard configuration: pylint: disable=C0103,R0903,W0232

    class types(HandlerConfig.types):
        """ file: file path of the log file. """
        file = String


class File(Handler):
    """ Writes messages to a configuration file. """
    
    __config__ = Config
    _SEPARATOR = "\n====================\n"
    _ENCODING = "UTF-8"
       
    def _singularize(self, config, entry):
        self._write(config, entry)
        
    def _summarize(self, config, protocol):
        self._write(config, protocol)
        
    def _write(self, config, msg):
        file_object = open(config.file, "a")
        try:
            file_object.write(unicode(msg).encode(self._ENCODING))
            file_object.write(self._SEPARATOR)
        finally:
            file_object.close()
