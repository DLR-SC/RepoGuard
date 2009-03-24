# pylint: disable-msg=E1102
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
Test module for the module package.
"""

import py.test

from configobj import ConfigObj

from repoguard.core import constants
from repoguard.core.config import ProjectConfig
from repoguard.core.module import Module, CheckManager, HandlerManager
from repoguard.core.module import ConfigSerializer, String, Array, Handler
from repoguard.testutil import TestProtocol, TestProtocolEntry
from repoguard.checks.pylint_ import PyLint

config_string = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=PyLint,
        success=Console,
        error=File.default,
        
[handlers]        
    [[File]]
        [[[default]]]
        file=repoguard.log
""".splitlines()

handler_config = """
protocol.include = Log,
protocol.exclude = PyLint,
""".splitlines()

class MockHandler(Handler):
    def _singularize(self, config, entry):
        assert entry.check == "Log"
        
    def _summarize(self, config, protocol):
        assert protocol[0].check == "Log"

class TestClass1(ConfigSerializer):
    class types:
        optional = String(optional=True)
        var = String

class TestClass(ConfigSerializer):
    class types:
        name = Array(TestClass1)
        subclass = TestClass1

class TestConfigSerializer(object):

    @classmethod
    def setup_class(cls):
        cls.test_dict = {'name' : ['test1', 'test2', 'test3'], 
                         'name.test1.var' : 'test1',
                         'name.test2.var' : 'test2',
                         'name.test3.var' : 'test3',
                         'subclass.var' : 'test'}
        cls.test_class = TestClass
    
    def test_from_config(self):        
        self.test_class = TestClass.from_config(self.test_dict)
        assert self.test_class.name[0].var == "test1"
        assert self.test_class.name[1].var == "test2"
        assert self.test_class.name[2].var == "test3"
        assert hasattr(self.test_class, 'subclass')
        assert hasattr(self.test_class.subclass, 'var')
        assert self.test_class.subclass.var == self.test_dict['subclass.var']
        assert hasattr(self.test_class.subclass, 'optional')
    
    def test_to_config(self):
        foo = TestClass1()
        foo.id = "foo"
        foo.var = "test"
        
        foo1 = TestClass1()
        foo1.id = "foo1"
        foo1.var = "test1"
        
        foo2 = TestClass1()
        foo2.id = "foo2"
        #foo2.var = "test2"
        
        foo3 = TestClass1()
        foo3.id = "foo3"
        foo3.var = "test3"
        
        bar = TestClass()
        bar.id = "bar"
        bar.name = [foo1, foo2, foo3]
        bar.subclass = foo
        
        config = bar.to_config()
        assert config['subclass.var'] == "test"
        assert config['name.foo1.var'] == "test1"
        assert 'name.foo2.var' not in config
        assert config['name.foo3.var'] == "test3"

class TestModule(object):
    
    @classmethod
    def setup_class(cls):
        cls.module = Module(None)
        
    def test_logger(self):
        assert self.module.logger.name == "repoguard.core.module"    
        
class TestHandler(object):
    
    @classmethod
    def setup_class(cls):
        cls.handler = MockHandler(None)
        cls.config = ConfigObj(handler_config)
        cls.dconfig = cls.handler.__config__.from_config(cls.config)
        
    def test_skip_entry(self):
        entry = TestProtocolEntry.create(check="Log")
        assert self.handler._skip_entry(self.dconfig, entry) == False
        
        entry = TestProtocolEntry.create(check="PyLint")
        assert self.handler._skip_entry(self.dconfig, entry) == True
        
        entry = TestProtocolEntry.create(check="Foo")
        assert self.handler._skip_entry(self.dconfig, entry) == True
        
    def test_prepare_protocol(self):
        protocol = TestProtocol()
        protocol.add_entry("Log")
        
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
        protocol.add_entry("PyLint")
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
        protocol.add_entry("Foo")
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
    def test_singularize(self):
        entry = TestProtocolEntry.create(check="Log")
        self.handler.singularize(self.config, entry, debug=True)
        
        entry = TestProtocolEntry.create(check="Foo")
        self.handler.singularize(self.config, entry, debug=True)
        
    def test_summarize(self):
        protocol = TestProtocol()
        protocol.add_entry(check="Foo")
        protocol.add_entry(check="Log")
        
        self.handler.summarize(self.config, protocol, debug=True)
        
class TestCheckCache(object):
    
    @classmethod
    def setup_class(cls):
        cls.cache = CheckManager()
        
    def test_available_modules(self):
        buildin = ['PyLint', 'Mantis', 'AccessRights', 'ASCIIEncoded',
                   'CaseInsensitiveFilenameClash', 'Checkout', 'Checkstyle',
                   'Keywords', 'Log', 'RejectTabs', 'UnitTests', 'XMLValidator']
        for module in self.cache.available_modules:
            assert module in buildin
            
    def test_load(self):
        check = self.cache.load('PyLint')
        assert issubclass(check, PyLint)
        
    def test_fetch(self):
        check = self.cache.fetch('PyLint', None)
        
        check_id = id(check)
        
        check = self.cache.fetch('PyLint', None)
        assert check_id == id(check)
        
        py.test.raises(ImportError, self.cache.fetch, 'Foo', None)
        
class TestHandlerCache(object):
    
    @classmethod
    def setup_class(cls):
        cls._process = ProjectConfig(config_string, "hooks").profiles[0].get_process(constants.PRECOMMIT)
        cls.cache = HandlerManager()
        
    def test_available_modules(self):
        buildin = ['File', 'Console', 'Mail', 'Mantis', 'BuildBot', 'Hudson']
        for module in self.cache.available_modules:
            assert module in buildin
        
    def test_fetch(self):
        handler = self.cache.fetch('Console', None)
        handler_id = id(handler)
        
        handler = self.cache.fetch('Console', None)
        assert handler_id == id(handler)
        
        py.test.raises(ImportError, self.cache.fetch, 'Foo', None)
        
    def test_run(self):
        protocol = TestProtocol()
        protocol.add_entry(result=constants.SUCCESS)
        self.cache.singularize(None, self._process, protocol)
        
        protocol = TestProtocol()
        protocol.add_entry(result=constants.ERROR)
        self.cache.singularize(None, self._process, protocol)
    
    def test_summary(self):
        protocol = TestProtocol()
        protocol.add_entry(result=constants.SUCCESS)
        protocol.add_entry(result=constants.ERROR)
        self.cache.summarize(None, self._process, protocol)
    
        