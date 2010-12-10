# pylint: disable=R0201
# R0201: Cannot make test methods static as nose would not find them anymore. 
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
from repoguard_test import util


class TestProtocol(object):
    """ Implements tests of the protocol handler. """
    
    def test_properties(self):
        """ Tests the property access. """
        
        protocol = Protocol("dummy")
        
        entry = ProtocolEntry("dummy", {}, constants.SUCCESS,"dummy")
        protocol.append(entry)
        assert protocol.success == True
        
        entry = ProtocolEntry("dummy", {}, constants.ERROR,"dummy")
        protocol.append(entry)
        assert protocol.success == False
        
        entry = ProtocolEntry("dummy", {}, constants.SUCCESS,"dummy")
        protocol.append(entry)
        assert protocol.success == False
        
        assert protocol.errors == 1
        assert protocol.successors == 2
        assert protocol.warnings == 0
        assert protocol.exceptions == 0
        
    def test_filter(self):
        """ Tests the filter method. """
               
        protocol = Protocol("test")
        entry = ProtocolEntry("dummy", {}, constants.SUCCESS,"dummy")
        protocol.append(entry)
        
        assert len(protocol.filter(None, None)) == 1
        assert len(protocol.filter(["dummy"], None)) == 1
        assert len(protocol.filter(None, ["dummy"])) == 0
        assert len(protocol.filter(["dummy"], [])) == 1
        assert len(protocol.filter([], ["dummy"])) == 0
        assert len(protocol.filter([], [])) == 0
        
    def test_clear(self):
        """ Tests the clear method. """
        
        protocol = Protocol("test")
        entry = ProtocolEntry("dummy", {}, constants.SUCCESS,"dummy")
        protocol.append(entry)
        
        assert len(protocol) == 1
        
        protocol.clear()
        assert len(protocol) == 0


class TestProtocolEntry(object):
    """ Implements tests for the protocol entries. """
        
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.entry = ProtocolEntry("dummy", dict(), constants.ERROR,"dummy")
        
    def test_attributes(self):
        """ Checks the properties. """
        
        assert self.entry.duration == 0
        assert self.entry.check == "dummy"
        assert self.entry.msg == "dummy"
        assert self.entry.config == {}
        assert self.entry.result == constants.ERROR
        assert self.entry.success == False
        
        print self.entry
        
    def test_is_included(self):
        """ Tests the included flag. """
        
        entry = util.TestProtocolEntry.create(check="dummy")
        assert entry.is_included(None, None) == True
        assert entry.is_included(["dummy"], None) == True
        assert entry.is_included(None, ["dummy"]) == False
        assert entry.is_included(["dummy"], []) == True
        assert entry.is_included([], ["dummy"]) == False
        assert entry.is_included([], []) == False
        
        entry = util.TestProtocolEntry.create(check="foo")
        assert entry.is_included(None, None) == True
        assert entry.is_included(["dummy"], None) == False
        assert entry.is_included(None, ["dummy"]) == True
        assert entry.is_included(["dummy"], []) == False
        assert entry.is_included([], ["dummy"]) == False
        assert entry.is_included([], []) == False
        
    def test_duration(self):
        """ Tests the duration property. """
        
        entry = util.TestProtocolEntry.create(check="dummy")
        entry.start_time = 0.5
        entry.end_time = 1.5
        assert entry.duration == 1000
