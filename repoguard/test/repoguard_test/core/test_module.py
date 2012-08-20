# pylint: disable=E1101,C0111,C0103,R0201,R0903,W0232,W0201,W0212
# E1101: Pylint cannot import py.test.raises
# C0111,C0103,R0201,R0903,W0232,W0201: General problem with test configuration 
# class definition of handler/checks. But fine for test purposes.
# W0212: Access of protected members for test purposes is fine.
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
import mock
import pytest

from repoguard.checks.pylint_ import PyLint
from repoguard.core import constants
from repoguard.core.config import ProjectConfig
from repoguard.core.module import Module, CheckManager, HandlerManager
from repoguard.core.module import ConfigSerializer, String, Array, Handler


# Configuration class definitions for test purposes
class _TestClass1(ConfigSerializer):
    
    class types:
        optional = String(optional=True)
        var = String

class _TestClass(ConfigSerializer):
    
    class types:
        name = Array(_TestClass1)
        subclass = _TestClass1

def test_conversion_to_config_instance():
    test_dict = {
        "name" : ["test1", "test2", "test3"], 
        "name.test1.var" : "test1",
        "name.test2.var" : "test2",
        "name.test3.var" : "test3",
        "subclass.var" : "test"}
    test_class = _TestClass.from_config(test_dict)
    assert test_class.name[0].var == "test1"
    assert test_class.name[1].var == "test2"
    assert test_class.name[2].var == "test3"
    assert hasattr(test_class, "subclass")
    assert hasattr(test_class.subclass, "var")
    assert test_class.subclass.var == test_dict["subclass.var"]
    assert hasattr(test_class.subclass, "optional")

def test_conversion_to_config_dictionary():
    foo_ = _TestClass1()
    foo_.id = "foo"
    foo_.var = "test"
    
    foo1 = _TestClass1()
    foo1.id = "foo1"
    foo1.var = "test1"
    
    foo2 = _TestClass1()
    foo2.id = "foo2"
    
    foo3 = _TestClass1()
    foo3.id = "foo3"
    foo3.var = "test3"
    
    bar_ = _TestClass()
    bar_.id = "bar"
    bar_.name = [foo1, foo2, foo3]
    bar_.subclass = foo_
    
    config = bar_.to_config()
    assert config["subclass.var"] == "test"
    assert config["name.foo1.var"] == "test1"
    assert "name.foo2.var" not in config
    assert config["name.foo3.var"] == "test3"


class TestModule(object):
    
    @classmethod
    def setup_class(cls):
        cls.module = Module(None)
        
    def test_logger(self):
        assert self.module.logger.name == "repoguard.core.module"    
    
    
class TestHandler(object):

    _HANDLER_CONFIG = """
        protocol.include = Log,
        protocol.exclude = PyLint,"""
        
    def setup_method(self, _):
        self._handler = Handler(None)
        self._config = ConfigObj(self._HANDLER_CONFIG.splitlines())
        self._handler._singularize = mock.Mock()
        self._handler._summarize = mock.Mock()
        
    def test_singularize_check_not_skipped(self):
        entry = mock.Mock(check="Log")
        entry.is_included.return_value = True
        self._handler.singularize(self._config, entry, debug=True)
        assert self._handler._singularize.called
        
    def test_singularize_check_skipped(self):
        entry = mock.Mock(check="PyLint")
        entry.is_included.return_value = False
        self._handler.singularize(self._config, entry, debug=True)
        assert not self._handler._singularize.called
        
    def test_singularize_error(self):
        entry = mock.Mock(check="Log")
        entry.is_included.return_value = True
        self._handler._singularize.side_effect = ValueError
        pytest.raises(ValueError,
            self._handler.singularize, self._config, entry, debug=True)
        
    def test_summarize_success(self):
        protocol = mock.MagicMock()
        self._handler.summarize(self._config, protocol, debug=True)
        assert self._handler._summarize.called
        assert protocol.filter.called
        
    def test_summarize_error(self):
        protocol = mock.MagicMock()
        self._handler._summarize.side_effect = ValueError
        pytest.raises(ValueError, 
            self._handler.summarize, self._config, protocol, debug=True)
        assert protocol.filter.called


class TestCheckManager(object):
        
    @classmethod
    def setup_class(cls):
        cls._cache = CheckManager()
        cls._buildin_modules = {
            "PyLint": None, "Mantis": None, "AccessRights": None, "ASCIIEncoded": None,
            "CaseInsensitiveFilenameClash": None, "Checkout": None, "Checkstyle": None,
            "Keywords": None, "Log": None, "RejectTabs": None, "UnitTests": None, 
            "XMLValidator": None}
        pkg_resources.get_entry_map =  mock.Mock(return_value=cls._buildin_modules)
        pkg_resources.load_entry_point = mock.Mock(return_value=PyLint)

    def test_available_checks(self):
        for check in self._cache.available_modules:
            assert check in self._buildin_modules.keys()
            
    def test_load(self):
        check = self._cache.load("PyLint")
        assert issubclass(check, PyLint)
        
    def test_fetch_success(self):
        check = self._cache.fetch("PyLint", None)
        check_id = id(check)
        check = self._cache.fetch("PyLint", None)
        assert check_id == id(check)
        
    def test_fetch_error(self):
        pkg_resources.load_entry_point.side_effect = ImportError
        pytest.raises(ImportError, self._cache.fetch, "Foo", None)


class TestHandlerManager(object):
        
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
                file=repoguard.log"""
    
    def setup_method(self, _):
        self._process = ProjectConfig(
            self._CONFIG_STRING.splitlines(), "hooks").profiles[0].get_process(constants.PRECOMMIT)
        self._cache = HandlerManager()
        assert isinstance(self._cache, CheckManager)
        self._handler_mock = mock.Mock()
        self._cache.fetch = mock.Mock(return_value=self._handler_mock)
        
    def test_singularize(self):
        entry = mock.Mock(success=True)
        self._cache.singularize(None, self._process, entry)
        assert self._handler_mock.singularize.called
        
    def test_summary(self):
        protocol = mock.Mock()
        self._cache.summarize(None, self._process, protocol)
        assert self._handler_mock.summarize.called
