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


""" Provides tests of the protocol module. """


from repoguard.core import constants
from repoguard.core.protocol import Protocol, ProtocolEntry


class TestProtocol(object):
    
    def setup_method(self, _):
        self._protocol = Protocol("test")
        self._entry = ProtocolEntry("dummy", dict(), constants.SUCCESS, "dummy")
        self._protocol.append(self._entry)
    
    def test_properties(self):
        assert self._protocol.success == True
        assert self._protocol.result == constants.SUCCESS
        
        entry = ProtocolEntry("dummy", dict(), constants.ERROR,"dummy")
        self._protocol.append(entry)
        assert self._protocol.success == False
        
        entry = ProtocolEntry("dummy", dict(), constants.SUCCESS,"dummy")
        self._protocol.append(entry)
        assert self._protocol.success == False
        
        assert self._protocol.errors == 1
        assert self._protocol.successors == 2
        assert self._protocol.warnings == 0
        assert self._protocol.exceptions == 0
        assert self._protocol.result == constants.ERROR
        assert str(self._protocol) != None

    def test_filter(self):
        assert len(self._protocol.filter(None, None)) == 1
        assert len(self._protocol.filter(["dummy"], None)) == 1
        assert len(self._protocol.filter(None, ["dummy"])) == 0
        assert len(self._protocol.filter(["dummy"], list())) == 1
        assert len(self._protocol.filter(list(), ["dummy"])) == 0
        assert len(self._protocol.filter(list(), list())) == 0
        
    def test_clear(self):
        assert len(self._protocol) == 1
        
        self._protocol.clear()
        assert len(self._protocol) == 0


class TestProtocolEntry(object):
        
    def setup_method(self, _):
        self._entry = ProtocolEntry("dummy", dict(), constants.ERROR,"dummy")
        
    def test_properties(self):
        assert self._entry.duration == 0
        assert self._entry.check == "dummy"
        assert self._entry.msg == "dummy"
        assert self._entry.config == dict()
        assert self._entry.result == constants.ERROR
        assert self._entry.success == False
        assert str(self._entry) != None
        
    def test_is_included(self):
        assert self._entry.is_included(None, None) == True
        assert self._entry.is_included(["dummy"], None) == True
        assert self._entry.is_included(None, ["dummy"]) == False
        assert self._entry.is_included(["dummy"], list()) == True
        assert self._entry.is_included(list(), ["dummy"]) == False
        assert self._entry.is_included(list(), list()) == False
        
    def test_duration(self):
        self._entry.start_time = 0.5
        self._entry.end_time = 1.5
        assert self._entry.duration == 1000
