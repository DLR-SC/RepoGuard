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

""" Checks XML files for correctness. """

from xml.dom import minidom
from xml.parsers import expat

from repoguard.core.module import Check, ConfigSerializer, Array, String

class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*\.xml"])
        ignore_files = Array(String, optional=True, default=[])

class XMLValidator(Check):

    __config__ = Config

    def _run(self, config):
        files = self.transaction.get_files(config.check_files, 
                                           config.ignore_files)
        msg= ""
        for filename, attribute in files.iteritems():
            if attribute in ["A", "U"]:
                try:
                    minidom.parse(self.transaction.get_file(filename))
                except expat.ExpatError, e:
                    msg += "XML validation error in file %r: %s" % (filename, e)
        if msg:
            return self.error(msg)
        else:
            return self.success()
