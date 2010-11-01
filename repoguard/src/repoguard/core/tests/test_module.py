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


"""
Test module for the module package.
"""


import pkg_resources
        
from configobj import ConfigObj
import py.test

from repoguard.checks.pylint_ import PyLint
from repoguard.core import constants
from repoguard.core.config import ProjectConfig
from repoguard.core.module import Module, CheckManager, HandlerManager
from repoguard.core.module import ConfigSerializer, String, Array, Handler
from repoguard.testutil import TestProtocol, TestProtocolEntry


_CONFIG_STRING = """
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


_HANDLER_CONFIG = """
protocol.include = Log,
protocol.exclude = PyLint,
""".splitlines()


class _HandlerMock(Handler):
    """ Mocks the handler module. """
    
    raiseImportErrorOnNew = False
    
    def __new__(cls, transaction):
        """ 
        Mocks the transaction initialization 
        and raises if C{cls.raiseImportErrorOnNew} is set to C{True}.
        """
        
        if cls.raiseImportErrorOnNew:
            raise ImportError()
        else:
            return Handler.__new__(cls, transaction) 

    def _singularize(self, _, entry):
        """ Mocks the method C{_singularize}. """
        
        assert entry.check == "Log"
        
    def _summarize(self, _, protocol):
        """ Mocks the method C{_summarize}. """
        
        assert protocol[0].check == "Log"


def _load_entry_point_mock(_, __, name):
    """ 
    Creates a mock for L{pkg_resources.load_entry_point} which
    returns corresponding class objects for the given handler name.
    """

    handler = _HandlerMock
    handler.raiseImportErrorOnNew = False
    if name == "Foo":
        handler.raiseImportErrorOnNew = True
    elif name == "PyLint":
        handler = PyLint
    return handler


# Test configuration class definitions
class _TestClass1(ConfigSerializer):
    """ Serialization helper class. """
    
    class types:
        """ Defines the concrete types. """
        
        optional = String(optional=True)
        var = String


class _TestClass(ConfigSerializer):
    """ Serialization helper classes. """
    
    class types:
        """ Defines the concrete types. """
        
        name = Array(_TestClass1)
        subclass = _TestClass1


class TestConfigSerializer(object):
    """ Tests the serialization of the configuration. """

    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.test_dict = {"name" : ["test1", "test2", "test3"], 
                         "name.test1.var" : "test1",
                         "name.test2.var" : "test2",
                         "name.test3.var" : "test3",
                         "subclass.var" : "test"}
        cls.test_class = _TestClass
    
    def test_from_config(self):
        """ Tests conversion of a configuration dictionary into a configuration object. """
         
        self.test_class = _TestClass.from_config(self.test_dict)
        assert self.test_class.name[0].var == "test1"
        assert self.test_class.name[1].var == "test2"
        assert self.test_class.name[2].var == "test3"
        assert hasattr(self.test_class, "subclass")
        assert hasattr(self.test_class.subclass, "var")
        assert self.test_class.subclass.var == self.test_dict["subclass.var"]
        assert hasattr(self.test_class.subclass, "optional")
    
    def test_to_config(self):
        """ Tests conversion of a configuration instance to a dictionary. """
        
        foo = _TestClass1()
        foo.id = "foo"
        foo.var = "test"
        
        foo1 = _TestClass1()
        foo1.id = "foo1"
        foo1.var = "test1"
        
        foo2 = _TestClass1()
        foo2.id = "foo2"
        
        foo3 = _TestClass1()
        foo3.id = "foo3"
        foo3.var = "test3"
        
        bar = _TestClass()
        bar.id = "bar"
        bar.name = [foo1, foo2, foo3]
        bar.subclass = foo
        
        config = bar.to_config()
        assert config["subclass.var"] == "test"
        assert config["name.foo1.var"] == "test1"
        assert "name.foo2.var" not in config
        assert config["name.foo3.var"] == "test3"


class TestModule(object):
    """ Performs some basic module tests. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.module = Module(None)
        
    def test_logger(self):
        """ Checks whether the correct logger name is used. """
        
        assert self.module.logger.name == "repoguard.core.module"    
        

class TestHandler(object):
    """ Performs basic handler tests. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.handler = _HandlerMock(None)
        cls.config = ConfigObj(_HANDLER_CONFIG)
        cls.dconfig = cls.handler.__config__.from_config(cls.config)
        
    def test_skip_entry(self):
        """ Checks whether a certain handler execution has been skipped. """
        
        entry = TestProtocolEntry.create(check="Log")
        assert self.handler._skip_entry(self.dconfig, entry) == False
        
        entry = TestProtocolEntry.create(check="PyLint")
        assert self.handler._skip_entry(self.dconfig, entry) == True
        
        entry = TestProtocolEntry.create(check="Foo")
        assert self.handler._skip_entry(self.dconfig, entry) == True
        
    def test_prepare_protocol(self):
        """ Checks correct preparation of the protocol of a RepoGuard run. """
        
        protocol = TestProtocol()
        protocol.add_entry("Log")
        
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
        protocol.add_entry("PyLint")
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
        protocol.add_entry("Foo")
        assert len(self.handler._prepare_protocol(self.dconfig, protocol)) == 1
        
    def test_singularize(self):
        """ Checks the call of implemented singularize methods. """
        
        entry = TestProtocolEntry.create(check="Log")
        self.handler.singularize(self.config, entry, debug=True)
        
        entry = TestProtocolEntry.create(check="Foo")
        self.handler.singularize(self.config, entry, debug=True)
        
    def test_summarize(self):
        """ Checks the default behavior of the summarize method. """
        
        protocol = TestProtocol()
        protocol.add_entry(check="Foo")
        protocol.add_entry(check="Log")
        
        self.handler.summarize(self.config, protocol, debug=True)


class TestCheckCache(object):
    """ Tests the checker management. """
        
    @classmethod
    def setup_class(cls):
        """ Performs test setup. """
        
        cls.cache = CheckManager()
        cls.buildin_modules = {"PyLint": None, "Mantis": None, "AccessRights": None, "ASCIIEncoded": None,
                               "CaseInsensitiveFilenameClash": None, "Checkout": None, "Checkstyle": None,
                               "Keywords": None, "Log": None, "RejectTabs": None, "UnitTests": None, 
                               "XMLValidator": None}
        pkg_resources.get_entry_map = lambda _, __: cls.buildin_modules
        pkg_resources.load_entry_point = _load_entry_point_mock

    def test_available_modules(self):
        """ Checks available checker. """
        
        for module in self.cache.available_modules:
            assert module in self.buildin_modules.keys()
            
    def test_load(self):
        """ Checks loading of a specific check. """
        
        check = self.cache.load("PyLint")
        assert issubclass(check, PyLint)
        
    def test_fetch(self):
        """ Tests the fetching of a specific check from cache. """
        
        check = self.cache.fetch("PyLint", None)
        
        check_id = id(check)
        
        check = self.cache.fetch("PyLint", None)
        assert check_id == id(check)
        
        py.test.raises(ImportError, self.cache.fetch, "Foo", None)


class TestHandlerCache(object):
    """ Tests the handler management / cache. """
        
    @classmethod
    def setup_class(cls):
        """ Performs test setup. """
        
        cls._process = ProjectConfig(_CONFIG_STRING, "hooks").profiles[0].get_process(constants.PRECOMMIT)
        cls.cache = HandlerManager()
        cls.buildin_modules = {"File": None, "Console": None, "Mail": None, 
                               "Mantis": None, "BuildBot": None, "Hudson": None}
        pkg_resources.get_entry_map = lambda _, __: cls.buildin_modules 
        pkg_resources.load_entry_point = _load_entry_point_mock

    def test_available_modules(self):
        """ Tests available handler. """
        
        for module in self.cache.available_modules:
            assert module in self.buildin_modules.keys()
        
    def test_fetch(self):
        """ Tests fetching of handler objects from cache. """
        
        handler = self.cache.fetch("Console", None)
        handler_id = id(handler)
        
        handler = self.cache.fetch("Console", None)
        assert handler_id == id(handler)
        
        py.test.raises(ImportError, self.cache.fetch, "Foo", None)
        
    def test_singularize(self):
        """ Tests the singularization of handler instances. """
        
        protocol = TestProtocol()
        protocol.add_entry(result=constants.SUCCESS)
        self.cache.singularize(None, self._process, protocol)
        
        protocol = TestProtocol()
        protocol.add_entry(result=constants.ERROR)
        self.cache.singularize(None, self._process, protocol)
    
    def test_summary(self):
        """ Tests the summary method of a handler. """
        
        protocol = TestProtocol()
        protocol.add_entry(result=constants.SUCCESS)
        protocol.add_entry(result=constants.ERROR)
        self.cache.summarize(None, self._process, protocol)
