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


""" Simply print the message to the console. Either to stdout or to stderr. """


import sys

from repoguard.core import constants
from repoguard.core.module import Handler


class Console(Handler):
    """
    Prints the incoming messages on stdout or stderr.
    """

    _OUT = {
        constants.SUCCESS : sys.stdout,
        constants.WARNING : sys.stderr,
        constants.ERROR : sys.stderr,
        constants.EXCEPTION : sys.stderr
    }
    _PATTERN = "\n%s\n" + "-" * 80 + "\n"
    _ENCODING = sys.stdout.encoding or sys.getdefaultencoding() or "ascii"

    def _singularize(self, config, entry):
        self._OUT[entry.result].write(
            self._PATTERN % unicode(entry).encode(self._ENCODING, "replace"))

    def _summarize(self, config, protocol):
        self._OUT[protocol.result].write(
            self._PATTERN % unicode(protocol).encode(self._ENCODING, "replace"))
