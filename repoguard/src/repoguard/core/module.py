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
Module contains all classes that are responsible for 
check and handler handling.

:Classes:
    Array
    
    Check
    
    CheckManager
    
    ConfigSerializer
    
    Handler
    
    HandlerManager
    
    Integer
    
    Module
    
    Boolean
    
    String
    
    Integer
"""


import inspect
import re

import pkg_resources
from validate import Validator

from repoguard.core import constants
from repoguard.core.protocol import ProtocolEntry
from repoguard.core.logger import LoggerFactory


def _objectname(obj):
    """
    Returns the name of a given obj or class.
    
    :param obj: The class or object from which the name has to be returned.
    :type obj: object
    
    :return: The name of the class/object.
    :rtype: string
    """
    
    if hasattr(obj, '__name__'):
        return obj.__name__
    else:
        return obj.__class__.__name__


class Boolean(object):
    """
    Class that represents an boolean value.
    """
    
    optional = False
    default = False
    
    def __init__(self, optional=False, default=False):
        """
        Constructor.
        
        :param optional: Set this param to True if the config param is optional.
        :type optional: boolean
        
        :param default: The default value if this param is optional.
        :type default: boolean
        """
        
        self.optional = optional
        self.default = default
        
    @classmethod
    def validate(cls, value):
        return Validator().check('boolean', value)


class String(object):
    """
    Class that represents an string value.
    """
    
    minsize = 0
    maxsize = -1
    regex = ".*"
    optional = False
    default = None
    
    def __init__(
        self, minsize=0, maxsize=-1, regex=".*", optional=False, default=None):
        """
        Constructor.
        
        :param minsize: The minimum string length.
        :type minsize: int
        
        :param maxsize: The maximum string length.
        :type maxsize: int
        
        :param regex: The regulare expression that the stirng has to be kept.
        :type regex: string
        
        :param optional: Set this param to True if the config param is optional.
        :type optional: boolean
        
        :param default: The default value if this param is optional.
        :type default: string
        """
        
        self.minsize = minsize
        self.maxsize = maxsize
        self.regex = regex
        self.optional = optional
        self.default = default
        
    @classmethod
    def validate(cls, value):
        if not isinstance(value, (unicode, str)):
            msg = "Given value '%s' is not a unicode or str instance." % value
            raise ValueError(msg)
        
        if len(value) < cls.minsize:
            msg = "Value '%s' is too short. (Minimum size: %d)"
            raise ValueError(msg % (value, cls.minsize))
        
        if cls.maxsize > -1 and len(value) > cls.maxsize:
            msg = "Value '%s' is too long. (Maximum size: %d)"
            raise ValueError(msg % (value, cls.maxsize))
        
        if not re.match(cls.regex, value):
            msg = "Value '%s' does not match the regex '%s'." 
            raise ValueError(msg % (value, cls.regex))
    
        return value

            
class Integer(object):
    """
    Class that represents an int value.
    """
    
    optional = False
    default = None
    
    def __init__(self, optional=False, default=None):
        """
        Constructor.
        
        :param optional: Set this attribute to True if the config param is 
                         optional.
        :type optional: boolean
        
        :param default: Set a default value when the config param is not set.
        :type default: object
        """
        self.optional = optional
        self.default = default
        
    @classmethod
    def validate(cls, value):
        """
        Validate the given value.
        
        :param value: The value that has to be validated.
        :type value: object
        
        :return: The translated and checked type for this value.
        :rtype: int
        
        :raises ValueError: Is raised when the given value is invalid.
        """
        
        return Validator().check('integer', value)
    
            
class Array(object):
    """
    Class that represents an array/list structure.
    """
    
    minsize = 0
    maxsize= -1
    optional = False
    default = None
    
    def __init__(
        self, serializer, minsize=0, maxsize=-1, optional=False, default=None):
        """
        Constructor.
        
        :param serializer: The class of types that are contained in this array.
        :type serializer: String, Integer
        
        :param minsize: The minimum size of items contained in this array.
        :type minsize: int
        
        :param maxsize: The maximum size of item contained in this array.
        :type maxsize: int
        
        :param optional: Set this attribute to True if the config param is 
                         optional.
        :type optional: boolean
        
        :param default: Set a default value when the config param is not set.
        :type default: object
        """
        
        self.serializer = serializer
        self.minsize = minsize
        self.maxsize = maxsize
        self.optional = optional
        self.default = default
    
    @classmethod
    def validate(cls, value):
        """
        Validate the given value.
        
        :param value: The value that has to be validated.
        :type value: object
        
        :raises ValueError: Is raised when the given value is invalid.
        """
        
        if not isinstance(value, list):
            raise ValueError("Given value is not a list")
        
        if len(value) < cls.minsize:
            raise ValueError("Value '%s' is too short" % value)
        
        if cls.maxsize > -1 and len(value) > cls.maxsize:
            raise ValueError("Value '%s' is too long" % value)
        
        return value


class ConfigSerializer(object):
    """
    Serializer class that converts given config in an object representation
    and from an object representation to a config.
    """
    
    class types:
        # Special variable that is needed for the translation from the object to
        # the dictionary representation.
        id = String
        
    __section__ = None
    optional = False
    default = None
    
    def __init__(self, optional=False, default=None):
        """
        Constructor.
        
        :param optional: If this option is set this class is optional in the 
                         configuration.
        :type optional: boolean
        
        :param default: Sets the value that has to be set when the value is 
                        optional.
        :type default: object
        """
        
        cls = self.__class__
        for key, _ in inspect.getmembers(cls.types):
            setattr(self, key, None)
        self.optional = optional
        self.default = default
        
    @classmethod
    def validate(cls, value):
        """
        Method can be overridden for special validate purposes.
        
        :param cls: The class that has to be checked.
        :type cls: ConfigSerializer
        
        :param value: A configserializer instance that has to be checked.
        :type value: ConfigSerializer
        """
        
        return value
        
    @staticmethod
    def predicate(value):
        """
        Protocol method for all invalid attributes.
        """
        
        return not value is None and not isinstance(value, str)
    
    @classmethod
    def from_config(cls, config):
        """
        Converts a given config in a object representation.
        
        :param cls: The class that has to be converted.
        :type cls: ConfigSerializer
        
        :param config: The config that has to be build as a class.
        :type config: dict
        """
        
        def has_composite_key(config, key):
            """
            Checks if the given key is a composite key in config.
            
            @param config: The config where the given key has to be searched.
            @type config: C{dict}
            
            @param key: The composite key.
            @type key: C{string}
            """
            
            if config:
                for k in config.keys():
                    if not cmp(k, key) or k.startswith(key + '.'):
                        return True
            return False            
        
        def walk(obj, config, path):
            """
            Method that walks through the class definitions and build
            the classes.
            
            @param obj: The class that has to build.
            @type obj: C{ConfigSerializer}
            
            @param config: The config that has to be build to an class.
            @type config: C{dict}
            
            @param path: The current path where the method is running.
            @type path: C{list}
            
            @return: Returns the object representation for the given config.
            @rtype: C{ConfigSerializer}
            """

            members = inspect.getmembers(obj.types, ConfigSerializer.predicate)
            for name, clazz in members:
                if not cmp(name, 'id'):
                    continue 
                          
                key = '.'.join(path + [name])
                if not has_composite_key(config, key):
                    if not clazz.optional:
                        msg = "Unable to set attribute '%s' in class '%s'. " \
                            + "This paramter is not optional."
                        raise KeyError(msg % (name, _objectname(obj)))

                    clazz = value = clazz.default
                else:
                    value = clazz.validate(config.get(key))
                    
                if isinstance(clazz, Array):
                    if issubclass(clazz.serializer, ConfigSerializer):
                        value = [
                            walk(
                                clazz.serializer(), config, path + [name, item]
                            ) for item in value
                        ]
                elif inspect.isclass(clazz) and issubclass(clazz, 
                                                           ConfigSerializer):
                    value = walk(clazz(), config, path + [name])
                elif isinstance(clazz, ConfigSerializer):
                    value = walk(clazz, config, path + [name])
                setattr(obj, name, value)
            return obj
        
        cls.__section__ = config
        return walk(cls(), config, [])
    
    def to_config(self):
        """
        Converts the object representation back to an config dict.
        For right convertion to an 
        
        :return: The configuration as a dict.
        :rtype: dict
        """
        
        def walk(config, obj, path):
            """
            Method that walks through the object and sets the given values in 
            the given config.
            
            @param config: The current config that has to be filled with data.
            @type config: C{dict}
            
            @param obj: The object that has to serialized.
            @type obj: C{ConfigSerializer}
            
            @param path: The current position the object hierarchy.
            @type path: C{list}
            
            @return: The current config filled with data.
            @rtype: C{dict}
            """
            
            members = inspect.getmembers(obj.types, ConfigSerializer.predicate)
            for name, clazz in members:
                
                if not cmp(name, 'id'):
                    continue 
                
                key = '.'.join(path + [name])
                value = getattr(obj, name)
                if not value:
                    if not hasattr(clazz, 'optional'):
                        msg = "Unable to get attribute '%s' from class '%s'."
                        raise KeyError(msg % (name, _objectname(obj)))
                    continue
                
                if isinstance(clazz, Array):
                    clazz = clazz.serializer
                    if issubclass(clazz, ConfigSerializer):
                        config[key] = []
                        for item in value:
                            walk(config, item, path + [name, item.id])
                            config[key].append(item.id)
                        continue
                elif issubclass(clazz, ConfigSerializer):
                    walk(config, value, path + [name])
                    continue
                
                config[key] = value
            return config
        return walk({}, self, [])
    
class Module(object):
    """
    Base class for the check and handler classes. Handles the automatic
    transaction initialisation.
    """
    
    __config__ = ConfigSerializer
    
    transaction = None
    logger = None
    
    def __new__(cls, transaction):
        """
        Overriden __new__ method that handles the automatic transaction
        iniialisation.
        
        :param cls: The class that has to be created.
        :type cls: Module
        
        :param transaction: The current transaction for this module.
        :type transaction: C{Transaction}
        
        :return: Returns the created module object.
        :rtype: Module
        """
        
        obj = super(Module, cls).__new__(cls)
        
        # Initialize transaction.
        obj.transaction = transaction
        
        # Generate an own logger for every module.
        obj.logger = LoggerFactory().create(cls.__module__)

        return obj
    
    @staticmethod
    def config(config_class):
        """
        Config class decorator to allow a more easier config assignment.
        
        :param config_class: The class that represents the configuration.
        :type config_class: ConfigSerializer
        
        :return: Function with a preset config class parameter.
        :rtype: func
        """
        
        def assign(module_class):
            """
            Inner method to set the __config__ parameter of the module_class.
            
            :param config_class: The configuration that has to been set.
            :type config_class: ConfigSerializer
            
            :param module_class: The module that has to be assigned with the 
                                 config.
            :type module_class: Module
            
            :return: Returns th module_class with the assigned config_class.
            :rtype: Module
            """
            
            module_class.__config__ = config_class
            return module_class
        return assign 


class Check(Module):
    """
    Base object for all checks.
    """
        
    @staticmethod
    def success(msg=""):
        """
        Class that specifies a success return value.
        
        :param msg: The success message.
        :type msg: string
        
        :return: The success return representation.
        :rtype: constants.SUCCESS, string
        """
        
        return constants.SUCCESS, msg
    
    @staticmethod
    def error(msg):
        """
        Class that specifies a error return value.
        
        :param msg: The error message.
        :type msg: string
    
        :return: The success return representation.
        :rtype: constants.ERROR, string
        """
        return constants.ERROR, msg
        
    def _run(self, config):
        """
        This method defines literally the check. This method has to be 
        implemented by every check.
        
        :param check: The configuration that has to be executed by the check.
        :type check: Section
        
        :return: The method has to return a value that is generated by the 
                 success and error methods.
        :rtype: Result of the success() or error() method.
        """
        
        raise NotImplementedError("The _run method has to be implemented.")
    
    def run(self, config, interp=constants.ABORTONERROR, debug=False):
        """
        The singularize method calls the implemented check. It initializes all 
        nessessary values and returns the check result as a C{ProtocolEntry}.
        
        :param config: The check configuration that has to be used.
        :type config: C{Section}
        
        :param interp: Defines how the check result has to be interpreted.
        :type interp: - C{constants.WARNING}
                      - C{constants.DELAYONERROR}
                      - C{constants.ABORTONERROR}
                      
        :param debug: Returns an exception instead of translation in a log msg.
        :type debug: C{boolean}
                      
        :return: Returns the result of the check as a C{ProtocolEntry}.
        :rtype: C{ProtocolEntry}
        """
        
        name = self.__class__.__name__
        config = self.__config__.from_config(config)
        entry = ProtocolEntry(name, config)
        try:
            entry.start()
            entry.result, entry.msg = self._run(config)
            entry.end()
        except Exception, exc:
            if debug:
                raise exc
            
            entry.result = constants.EXCEPTION
            entry.msg = "Exception in check '%s': %s" % (name, str(exc))
            self.logger.exception(entry.msg) 
        
        if entry.result == constants.ERROR and interp == constants.WARNING:
            entry.result = constants.WARNING
        return entry
    
class Protocol(ConfigSerializer):
    """
    Protocol checks that has to be included or excluded.
    """
    
    class types:
        include = Array(String, optional=True)
        exclude = Array(String, optional=True)
        template = String(optional=True)

class HandlerConfig(ConfigSerializer):
    """
    Default handler configuration.
    """
    
    protocol = None
    
    class types(ConfigSerializer.types):
        protocol = Protocol(optional=True, default=Protocol)

class Handler(Module):
    """
    Base class for all handlers.
    """
    
    __config__ = HandlerConfig
    
    def _skip_entry(self, config, entry):
        """
        Check if the config and the given entry indicates a non execution.
        
        :param config: Deserialized configuration.
        :type config: HandlerConfig
        
        :param entry: The entry that maybe has to be skipped.
        :type entry: ProtocolEntry
        
        :return: Returns true if the entry has to be skipped else false.
        :rtype: boolean
        """
        
        if not config.protocol is None:
            include, exclude = config.protocol.include, config.protocol.exclude
            result = entry.is_included(include, exclude)
            if result:
                msg = "Handler '%s' skipped."
                self.logger.debug(msg, self.__class__.__name__)
            return not result
        return False
        
    def singularize(self, config, entry, debug=False):
        """
        The singularize method calls the implemented _singularize method and 
        handles all raised exceptions. This method is called after every check.
        
        :param config: The configuration that has to be used by the handler.
        :type config: C{Section}
        
        :param entry: The C{ProtocolEntry} that has to be handled.
        :type entry: C{ProtocolEntry}
        
        :param debug: Returns an exception instead of translation in a log msg.
        :type debug: C{boolean}
        """
        
        config = self.__config__.from_config(config)
            
        try:
            if not self._skip_entry(config, entry):
                self._singularize(config, entry)
        except Exception, exc:
            if debug:
                raise exc
            
            msg = "Exception in %s handler in method _singularize: %s"
            self.logger.exception(msg, self.__class__.__name__, str(exc))
    
    def _singularize(self, config, entry):
        """
        This method can be implemented if a handler has to be called 
        after every check execution.
        
        :param config: The configuration that has to be used by the handler.
        :type config: C{Section}
        
        :param entry: The C{ProtocolEntry} that has to be handled.
        :type entry: C{ProtocolEntry}
        """
        
        pass
    
    def _prepare_protocol(self, config, protocol):
        """
        Prepares the given protocol with the configuration.
        
        :param config: Deserialized configuration.
        :type config: HandlerConfig
        
        :param protocol: Protocol that has to be prepared.
        :type protocol: Protocol
        
        :return: Filtered protocol.
        :rtype: Protocol
        """
        
        if not config.protocol is None:
            include, exclude = config.protocol.include, config.protocol.exclude
            self.logger.debug("Include: %s", str(include))
            self.logger.debug("Exclude: %s", str(exclude))
            protocol = protocol.filter(include, exclude)
        self.logger.debug("Checks: " + str([entry.check for entry in protocol]))
        return protocol
    
    def summarize(self, config, protocol, debug=False):
        """
        The summarize method calls the _summarize method and handlers all raised
        exception. This method is only called at the end of a profile 
        execution.
        
        :param config: The configuration that has to be used by the handler.
        :type config: C{Section}
        
        :param protocol: The C{Protocol} that has to be handled.
        :type protocol: C{ProtocolEntry}
        
        :param debug: Returns an exception instead of translation in a log msg.
        :type debug: C{boolean}
        """
        
        config = self.__config__.from_config(config)
        protocol = self._prepare_protocol(config, protocol)
        try:
            self._summarize(config, protocol)
        except Exception, exc:
            if debug:
                raise exc
            
            msg = "Exception in %s handler in method _summarize: %s"
            self.logger.exception(msg, self.__class__.__name__, str(exc))
    
    def _summarize(self, config, protocol):
        """
        This method can be implemented if a handler has to be called 
        only at the end of a profile execution.
        
        :param config: The configuration that has to be used by the handler.
        :type config: C{Section}
        
        :param protocol: The C{Protocol} that has to be handled.
        :type protocol: C{ProtocolEntry}
        """
        
        pass

    
class CheckManager(object):
    """
    Manager class that initialize and keeps all intialized checks.
    """
    
    def __init__(self, module_type=constants.CHECKS):
        """
        Constructor.
        """
        
        self._module_type = module_type
        self._group = 'repoguard.' + module_type
        self.cache = {}
        
    def _get_available_modules(self):
        """
        Returns all available modules.
        
        :return: A list of all available handlers.
        :rtype: C{list<string>}
        """
        
        result = list()
        for entrypoint in pkg_resources.iter_entry_points(self._group):
            result.append(entrypoint.name)
        return result
    
    def load(self, name):
        """
        Loads a class with the given name.
        
        :param name: The name of the module that has to be instantiated.
        :type name: C{string}
        
        :return: The class of the given name.
        :rtype: C{Check}, C{Handler}
        """
        
        for entrypoint in pkg_resources.iter_entry_points(self._group):
            if entrypoint.name == name:
                return entrypoint.load()
        raise ImportError("Entry point %s not found" % name)
    
    def fetch(self, module, transaction=None):
        """
        Returns a cached module or creates a new one.
        
        :param module: The name of the module that has to be returned.
        :type module: C{string}
        
        :param transaction: The transaction that has to be assign 
                            to the module.
        :type transaction: C{Transaction}
        
        :return: The module by the given name.
        :rtype: C{Check}, C{Handler}
        """
        
        instance = self.cache.get(module, self.load(module)(transaction))
        self.cache[module] = instance
        return instance
    
    available_modules = property(_get_available_modules)
    
class HandlerManager(CheckManager):
    """
    Manager class that initialize and keeps all handlers.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        CheckManager.__init__(self, constants.HANDLERS)
        
    def _execute(self, func, transaction, process, msg_container):
        """
        Execution of a given func with the given parameters.
        
        :param func: Function that has to be executed on all cached handlers.
        :type func: C{string}
        
        :param transaction: The current transaction.
        :type transaction: C{Transaction}
        
        :param process: The process context for the handlers.
        :type process: C{Process}
        
        :param msg_container: The message container class that contains all 
                              check messages.
        :type msg_container: C{Protocol}, C{ProtocolEntry}
        """
        
        if msg_container.success:
            handlers = process.success
        else:
            handlers = process.error
        
        for name, config in handlers:
            handler = self.fetch(name, transaction)
            getattr(handler, func)(config, msg_container)
            
    def singularize(self, transaction, process, entry):
        """
        Call all singularize methods for all handlers in the given process.
        
        :param transaction: The current transaction.
        :type transaction: C{Transaction}
        
        :param process: The process context for the handlers.
        :type process: C{Process}
        
        :param entry: The C{ProtocolEntry} object that contains the 
                      check message.
        :type entry: C{ProtocolEntry}
        """
        
        self._execute('singularize', transaction, process, entry)
                
    def summarize(self, transaction, process, protocol):
        """
        Call all summarize methods for all handlers in the given process.
        
        :param transaction: The current transaction.
        :type transaction: C{Transaction}
        
        :param process: The process context for the handlers.
        :type process: C{Process}
        
        :param protocol: The C{Protocol} object that contains all 
                         check messages.
        :type protocol: C{Protocol}
        """
        
        self._execute('summarize', transaction, process, protocol)
    