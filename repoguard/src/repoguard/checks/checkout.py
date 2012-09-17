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

""" Checkout files from the repository to file system locations. """

import shutil

from repoguard.core.module import Check, ConfigSerializer, String, Array

class Entry(ConfigSerializer):
    class types(ConfigSerializer.types):
        source = String
        destination = String
        
class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        entries = Array(Entry)

class Checkout(Check):

    __config__ = Config

    def _run(self, config):
        for entry in config.entries:
            if self.transaction.file_exists(entry.source):
                filepath = self.transaction.get_file(entry.source)
            else:
                return self.error("File %r to checkout does not exist in the repository." % entry.source)
            try:
                shutil.move(filepath, entry.destination)
            except IOError, error:
                return self.error("Failed to checkout file %r to %r: %s" % (entry.source, entry.destination, error))
        return self.success()
