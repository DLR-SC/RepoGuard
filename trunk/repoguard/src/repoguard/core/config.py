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
Module that contains all classes that are necessary for the configuration.

:Classes:
    Process
    
    Profile
    
    Project
    
    ProjectConfig
    
    RepoGuardConfig
    
    TemplateConfig
"""


import os
import re

from configobj import ConfigObj, Section

from repoguard.core import constants


class RepoGuardConfig(ConfigObj):
    """
    Configuration class for the main RepoGuard configuration options.
    """
    
    def __init__(self, config=None):
        """
        Constructor.
        
        :param config: The path or a splittedline configuration string.
                       See the U(ConfigObj documentation<http://www.voi
                       dspace.org.uk/python/configobj.html#reading-a-co
                       nfig-file>) for more details.
        :type config: string
        """
        
        ConfigObj.__init__(
            self, config, raise_errors=True, file_error=True, 
            write_empty_values=True, encoding='UTF-8', interpolation='template'
        )
        self._template_dirs = None
        self._projects = None
        
    def _get_template_dirs(self):
        """
        Returns the template directory from the main configuration file.
        
        :return: A list of directory paths that contains template files.
        :rtype: list
        """
        
        if not self._template_dirs:
            dirs = self.get('template_dirs', [])
            self._template_dirs = [os.path.normcase(path) for path in dirs]
        return self._template_dirs + [constants.BUILDIN_TPL_PATH]
    
    def _get_templates(self):
        """
        Returns all templates found under the template directory.
        
        :return: A dictionary of available templates with the associated path.
        :rtype: dict
        """
        
        templates = {}
        for template_dir in self.template_dirs:
            for template_file in os.listdir(template_dir):
                if template_file.endswith(constants.TEMPLATE_POSTFIX):
                    template = template_file[:-len(constants.TEMPLATE_POSTFIX)]
                    if template not in templates:
                        templates[template] = template_dir
        return templates
    
    def _get_validate(self):
        return cmp(self.get('validate', 'True'), 'False')
    
    def _get_projects(self):
        """
        Returns a list of projects that are configured in the repoguard 
        config.
        
        :return: Returns a list of projects.
        :rtype: list
        """
        
        if not self._projects:
            self._projects = {}
            for project in self.get('projects', {}).values():
                self._projects[project.name] = Project(project)
        return self._projects

    template_dirs = property(_get_template_dirs)
    templates = property(_get_templates)
    projects = property(_get_projects)
    validate = property(_get_validate)
    
class Project(Section):
    
    def __init__(self, project):
        """
        Constructor.
        """
        Section.__init__(self, project.parent, project.depth, 
                         project.main, project, project.name)
        
    def _get_path(self):
        """
        Returns the project path.
        
        :return: The path of the project.
        :rtype: string
        """
        
        return self['path']
    
    def _get_url(self):
        """
        Returns the project url under which the project is external reachable.
        
        :return: The external url.
        :rtype: string
        """
        
        return self['url']
    
    def _get_editors(self):
        """
        Returns a list of editors that has write rights for this project.
        
        :return: A list of editors.
        :rtype: list
        """
        
        return self['editors']
    
    path = property(_get_path)
    editors = property(_get_editors)
    url = property(_get_url)
    
class TemplateConfig(ConfigObj):
    """
    The TemplateConfig represents a configuration without any modifications.
    This class is mainly used for representing templates.
    """
    
    def __init__(self, config=None):
        """
        Constructor.
        
        :param config: The path or a splittedline configuration string.
                       See the U(ConfigObj documentation<http://www.voi
                       dspace.org.uk/python/configobj.html#reading-a-co
                       nfig-file>) for more details.
        :type config: string
        """
        ConfigObj.__init__(self, config, encoding='UTF-8')
        
    def _get_properties(self):
        """
        Returns the properties that are defined in the DEFAULT section.
        
        :return: Returns a dictionary with key/value pairs.
        :rtype: dict
        """
        
        return self.get('DEFAULT', {})
    
    def _set_properties(self, properties):
        """
        Setter for the properties. That are all values in the 'DEFAULT'-Section.
        
        :param properties: The properties that has to been set.
        :type properties: dict
        """
        
        self['DEFAULT'] = properties
    
    def _get_extends(self):
        """
        Returns the extended configuration. 
        If now extend is found None will be returned.
        
        :return: The extended configuration name.
        :rtype: string
        """
        
        return self.get('extends', None)
        
    def _get_profiles(self):
        """
        Returns all profiles that are contained in this configuration.
        
        :return: A list that contains all profiles.
        :rtype: list<Profile>
        """
        
        return [Profile(self, self.depth, self, profile, name) \
                for name, profile in self.get('profiles', {}).iteritems()]       
    
    def _get_vcs(self):
        """
        Returns the version control system that is used for this project.
        
        :return: The version control system that is used.
        :rtype: string
        """
        
        return self.get('vcs', 'svn')
    
    def has_profile(self, name):
        """
        Method to check if the given _profile exists.
        
        :param name: The name of the _profile.
        :type name: string
        
        :return: True if the _profile exists else False.
        :rtype: boolean
        """
        
        return 'profiles' not in self and name not in self['profiles']
    
    def profile(self, name):
        """
        Returns the _profile under the given name.
        
        :param name: The name of the project.
        :type name: string
        
        :return: The _profile for the given name.
        :rtype: Profile
        """
        
        if 'profiles' in self:
            indict = self['profiles'][name]
            profile = Profile(self['profiles'], self['profiles'].depth, 
                              self, indict, name)
            # Inject the _profile object in the configobj dict.
            self['profiles'][name] = profile
            return profile
        raise KeyError("Unable to find _profile '%s'" % name)
    
    def add_profile(self, name, regex):
        """
        Helper method to add _profile to configuration.
        It is recommended to use the method insteat of initlaizing a Profile 
        class.
        
        :param name: The name of the _profile.
        :type name: string
        
        :param regex: The regular expression for this _profile.
        :type regex: string
        
        :return: The Profile instance that was automatically added to the config.
        :rtype: Profile
        """
        
        if 'profiles' not in self:
            self['profiles'] = {}
        
        profiles = self['profiles']
        profile = Profile(profiles, profiles.depth, self, name=name)
        profile.regex = regex
        profiles[name] = profile
        return profile
    
    def del_profile(self, name):
        """
        Deletes the _profile with the given name.
        
        :param name: The _profile name.
        :type name: string
        """
        
        del self['profiles'][name]
        
        if not self['profiles']:
            del self['profiles']
    
    def _module_configs(self, type_, module):
        """
        Helper method that returns the configurations of a given module.
        
        :param type_: The type of the method whether it is a check or a handler.
        :type type_: string
        
        :param module: The name of the module that has to be returned.
        :type module: string
        
        :return: A list of configurations.
        :rtype: list
        """
        
        if type_ in self:
            return self[type_].get(module, {}).keys()
        return []
    
    def check_configs(self, check):
        """
        Calls internally the _module_configs method for the given check.
        
        :param check: The name of the check.
        :type check: string
        
        :return: A list of check configurations.
        :rtype: list
        """
        
        return self._module_configs(constants.CHECKS, check)
    
    def handler_configs(self, handler):
        """
        Calls internally the _module_configs method for the given handler.
        
        :param handler: The name of the handler.
        :type handler: string
        
        :return: A list of handler configurations.
        :rtype: list
        """
        return self._module_configs(constants.HANDLERS, handler)
    
    def check_config(self, check, name):
        """
        Returns the configuration for the given check with the given name.
        
        :param check: The name of the check.
        :type check: string
        
        :param name: The name of the configuration.
        :type name: string
        
        :return: Returns the configuration as dict.
        :rtype: dict
        """
        
        return self['checks'][check][name]
    
    def handler_config(self, handler, name):
        """
        Returns the configuration for the given handler with the given name.
        
        :param handler: The name of the handler.
        :type handler: string
        
        :param name: The name of the configuration.
        :type name: string
        
        :return: Returns the configuration as dict.
        :rtype: dict
        """
        return self['handlers'][handler][name]
    
    def _set_module_config(self, type_, module, name, config):
        """
        Helper method that sets the configuration for a module of the given 
        type under the given name with the given config.
        
        :param type_: The module type whether it is a check or a handler.
        :type type_: string
        
        :param module: The check or handler name.
        :type module: string
        
        :param name: The name of the configuration.
        :type name: string
        
        :param config: The configuration for the check/handler.
        :type config: dict
        """
        
        if type_ not in self:
            self[type_] = {}
        if module not in self[type_]:
            self[type_][module] = {}
        if name not in self[type_][module]:
            self[type_][module][name] = {}
        module_config = self[type_][module][name]
            
        module_config.clear()
        module_config.update(config)
    
    def set_check_config(self, check, name, config):
        """
        Calls internally the _set_module_config method for checks.
        
        :param check: The name of the check.
        :type check: string
        
        :param name: The name of the conifguration.
        :type name: string
        
        :param config: The configuration for the given check.
        :type config: dict
        """
        
        self._set_module_config(constants.CHECKS, check, name, config)
    
    def set_handler_config(self, handler, name, config):
        """
        Calls internally the _set_module_config method for handlers.
        
        :param handler: The name of the handler.
        :type handler: string
        
        :param name: The name of the conifguration.
        :type name: string
        
        :param config: The configuration for the given handler.
        :type config: dict
        """
        
        self._set_module_config(constants.HANDLERS, handler, name, config)

    def _del_module_config(self, type_, module, name):
        """
        Helper method for deleting a configuration from a check/handler.
        
        :param type_: The module type whether it is a check or handler.
        :type type_: string
        
        :param module: The check/handler name.
        :type module: string
        
        :param name: The configuration name.
        :type name: string
        """
        
        del self[type_][module][name]
        if not self[type_][module]:
            del self[type_][module]
        if not self[type_]:
            del self[type_]
        
    def del_check_config(self, check, name):
        """
        Calls internally the _del_module_config method for deleting 
        configurations from checks.
        
        :param check: The check name.
        :type check: string
        
        :param name: The configuration name.
        :type name: string
        """
        
        self._del_module_config(constants.CHECKS, check, name)
    
    def del_handler_config(self, handler, name):
        """
        Calls internally the _del_module_config method for deleting 
        configurations from handlers.
        
        :param handler: The handler name.
        :type handler: string
        
        :param name: The configuration name.
        :type name: string
        """
        self._del_module_config(constants.HANDLERS, handler, name)
    
    vcs = property(_get_vcs)
    extends = property(_get_extends)
    properties = property(_get_properties, _set_properties)
    profiles = property(_get_profiles)

class ProjectConfig(TemplateConfig):
    """
    The ProjectConfig is a class that extends the TemplateConfig by
    the ability of inheritance of template configurations.
    """
    
    def __init__(self, config, hooks_location="hooks", template_dirs=None):
        """
        Constructor.
        
        :param config: The path or a splittedline configuration string.
                       See the U(ConfigObj documentation<http://www.voi
                       dspace.org.uk/python/configobj.html#reading-a-co
                       nfig-file>) for more details.
        :type config: string
        
        :param hooks_location: The location of the hooks directory.
        :type hooks_location: string
        
        :param template_dirs: A list of directories where the repoguard
                              has to look for templates.
        :type template_dirs: list
        """
        
        TemplateConfig.__init__(self)
        
        # Dictionary that contains all templates by that the project file
        # was inheriated.
        self.extended = {}
        # Add the location of the hooks directory to the blank configuration.
        self.merge({u'DEFAULT' : {u'hooks' : hooks_location}})
        
        self._initialize(config, template_dirs)
        
        # Enables the template interpolation.
        self.interpolation = 'template'
        
        if isinstance(config, str) and os.path.exists(config):
            self.filename = config
    
    def _initialize(self, project, template_dirs=None):
        """
        Initalize the project config and merge them automatically with all 
        super templates.
        
        :param project: The project specific configuration.
        :type project: string
        
        :param template_dirs: A list of paths where a template can be found.
        :type template_dirs: list
        """
        
        def extend(config, template_dirs):
            """
            Function to walk recursive up till the last extended class.
            
            :param config: The configuration that has to be extended.
            :type config: ConfigObj
            
            :param template_dirs: A list of directories where templates
                                  can be found.
            :type template_dirs: list
            """
            
            extends = config.get('extends', None)
            if extends:
                template_file = extends + constants.TEMPLATE_POSTFIX
                for template_dir in template_dirs:
                    template_path = os.path.join(template_dir, 
                                                 template_file)
                    if os.path.exists(template_path):
                        template = TemplateConfig(template_path)
                        template = extend(template, template_dirs)
                        template.merge(config)
                        self.extended[extends] = template_path
                        
                        return template
                    
                msg = "Unable to find template '%s' in %s"
                raise ValueError(msg % (extends, " ,".join(template_dirs)))
            return config
        
        config = TemplateConfig(project)
        if template_dirs:
            config = extend(config, template_dirs)
        elif 'extends' in config:
            raise ValueError("Unable to extends. No template directory found.")
        self.merge(config.dict())
        
class Profile(Section):
    """
    Wrapper class for a _profile section.
    """
    
    def __init__(self, parent, depth, main, indict=None, name=None):
        """
        Constructor.
        
        :param _profile: Profile section that has to be wrapped by this class.
        :type _profile: Section
        """
        
        Section.__init__(self, parent, depth + 1, main, indict, name)
        
    def _get_regex(self):
        """
        Getter for the profiles regular expression.
        
        :return: The regular expresion.
        :rtype: string
        """
        
        return self.get('regex')
    
    def _set_regex(self, regex):
        """
        Setter for the regular expression.
        
        :param regex: The regular expression.
        :type regex: string
        """
        
        if regex:
            self['regex'] = regex
        else:
            del self.regex
        
    def _del_regex(self):
        """
        Deleter for the regular expression.
        """
        
        del self['regex']
                
    def get_process(self, hook):
        """
        Returns the _process for the given hook.
        
        :param hook: Pre- or postcommit _process.
        :type hook: constants.PRECOMMIT, constants.POSTCOMMIT
        
        :return: Returns the process that is associated with the given hook.
        :rtype: Process
        """
        
        if not hook in constants.HOOKS:
            raise ValueError("Unknown hook with the name '%s'", hook)
        
        if hook in self:
            process = Process(self, self.depth, self.main, self[hook], hook)
            # Inject the process object in the configobj dict.
            self[hook] = process
            return process
        return None
    
    def set_process(self, hook, process):
        """
        Setter for the process under the given hook.
        
        :param hook: The hook under which the process has to be set.
        :type hook: constants.PRECOMMIT, constants.POSTCOMMIT
        
        :param process: The process that has to be set.
        :type process: Process
        """
        
        if not hook in constants.HOOKS:
            raise ValueError("Unknown hook with the name '%s'", hook)
        
        if not isinstance(process, Process):
            raise ValueError("Unknown type for process '%s'" % type(process))
        
        self[hook] = process
        
    def del_process(self, hook):
        """
        Deleter for the process under the given hook.
        
        :param hook: The hook under which the process has to be deleted.
        :type hook: constants.PRECOMMIT, constants.POSTCOMMIT
        """
        
        if not hook in constants.HOOKS:
            raise ValueError("Unknown hook with the name '%s'", hook)
        del self[hook]
        
    def _get_precommit(self):
        """
        Calls internally the get_process method with the preset hook parameter 
        for the precommit process.
        
        :return: Returns the process that is associated with the precommit.
        :rtype: Process
        """
        
        return self.get_process(constants.PRECOMMIT)
        
    def _get_postcommit(self):
        """
        Calls internally the get_process method with the preset hook parameter 
        for the postcommit process.
        
        :return: Returns the process that is associated with the postcommit.
        :rtype: Process
        """
        
        return self.get_process(constants.POSTCOMMIT)
    
    def _set_precommit(self, process):
        """
        Calls internally the set_process method with the preset hook parameter
        for the precommit process.
        
        :param process: The process that has to be set.
        :type process: Process
        """
        
        self.set_process(constants.PRECOMMIT, process)
        
    def _set_postcommit(self, process):
        """
        Calls internally the set_process method with the preset hook parameter
        for the postcommit process.
        
        :param process: The process that has to be set.
        :type process: Process
        """
        
        self.set_process(constants.POSTCOMMIT, process)
        
    def _del_precommit(self):
        """
        Calls internally the del_process method with the preset hook parameter
        for the precommit process.
        """
        
        self.del_process(constants.PRECOMMIT)
    
    def _del_postcommit(self):
        """
        Calls internally the del_process method with the preset hook parameter
        for the precommit process.
        """
        
        self.del_process(constants.POSTCOMMIT)
        
    regex = property(_get_regex, _set_regex, _del_regex)
    precommit = property(_get_precommit, _set_precommit, _del_precommit)
    postcommit = property(_get_postcommit, _set_postcommit, _del_postcommit)
    
class Process(Section):
    """
    Wrapper class for a _process section.
    """
    
    check_regex = re.compile(constants.CHECK_REGEX)
    handler_regex = re.compile(constants.HANDLER_REGEX)
    
    def __init__(self, parent, depth, main, indict=None, name=None):
        """
        Constructor.
        
        :param get_process: Process section.
        :type get_process: Section
        """
        
        Section.__init__(self, parent, depth + 1, main, indict, name)
        
    def _get_default(self):
        """
        Getter for the default error interpretation for checks.
        
        :return: The interpretation constants.
        :rtype: WARNING, ABORTONERROR, DELAYONERROR
        """
        
        return self.get('default', constants.ABORTONERROR)
    
    def _set_default(self, default):
        """
        Setter for the default error interpretation for checks.
        
        :param default: The default interpretation.
        :type default: WARNING, ABORTONERROR, DELAYONERROR
        """
        
        if not default in constants.HOOKS:
            raise ValueError("Unknown hook '%s'" % default)
        self['default'] = default
        
    def _get_checks(self):
        """
        Getter for all checks that are contained in this process.
        Every element in this list is a tuple that are containing:
        1. Check name as string.
        2. Check configuration as Section.
        3. Error interpretation as constants.WARNING, 
        constants.DELAYONERROR, constants.ABORTONERROR.
        If no interpretation is defined in the configuration the default 
        is constants.ABORTONERROR.
        
        :return: A list that contains all checks as tuple.
        :rtype: list<tuple>
        """
        
        checks = []
        for check in self.get('checks', []):
            result = self.check_regex.search(check)
            name, config, interp = result.group("name", "config", "interp")
            if config:
                config = self.main['checks'][name][config]
            else:
                config = None
            interp = interp or self.get('default', constants.ABORTONERROR)
            checks.append((name, config, interp))
        return checks
    
    def _set_checks(self, checks):
        """
        Setter for all checks that has to be contained in this process.
        
        :param checks: A list of three element tuples that are containing:
        1. Check name as string.
        2. Check configuration as string or Section or None if the given
        check needs no configuration.
        3. The error interpretation as constants.WARNING, 
        constants.DELAYONERROR, constants.ABORTONERROR or None if the 
        default interpretation has to be choosed.
        :type checks: list
        """
        
        joined = []
        for name, config, interp in checks:
            check = [name]
            config = config or ''
            interp = interp or ''
            
            if interp and not interp in constants.INTERPS:
                raise ValueError("Unknown interpretation '%s'" % check[2])
            
            if isinstance(config, Section):
                config = config.name
                
            if isinstance(config, str):
                if config and config not in self.main['checks'][name]:
                    msg = "Unknown check config '%s' for '%s'" % (config, name)
                    raise KeyError(msg)
                check = check + [config, interp]
            else:
                raise ValueError("Unknown config type")
            
            # Removes all unnecessary elements.
            for i in range(2, 0, -1):
                if check[i]:
                    break
                del check[i]
                
            joined.append('.'.join(check))
        self['checks'] = joined
    
    def _get_handlers(self, type_):
        """
        Returns all handlers that are contained in this _process section.
        Every element in this list is a tuple that contains:
        1. Handler name
        2. Handler configuration
        
        :param type_: Defines if a success or error handler has to be returned.
        :type type_: constants.SUCCESS, constants.ERROR
        
        :return: A list that contains all handlers as tuple.
        :rtype: list<tuple>
        """
        
        handlers = []
        for handler in self.get(type_, []):
            result = self.handler_regex.search(handler)
            name, config = result.group("name", "config")
            if config:
                config = self.main['handlers'][name][config]
            else:
                config = None
            handlers.append((name, config))
        return handlers
    
    def _set_handlers(self, type_, handlers):
        joined = []
        for name, config in handlers:
            handler = [name]
            config = config or ''
            if isinstance(config, Section):
                config = config.name
                
            if isinstance(config, str):
                if config:
                    if config not in self.main['handlers'][name]:
                        msg = "Unknown handler config '%s'" % config
                        raise KeyError(msg)
                    handler = handler + [config]
            joined.append('.'.join(handler))
        self[type_] = joined
    
    def _set_success_handlers(self, handlers):
        self._set_handlers('success', handlers)
        
    def _set_error_handlers(self, handlers):
        self._set_handlers('error', handlers)
    
    def _get_success_handlers(self):
        """
        Helper method that returns all success handlers.
        
        :return: A list that contains all success handlers.
        :rtype: list<tuple>
        """
        
        return self._get_handlers('success')
        
    def _get_error_handlers(self):
        """
        Helper method that returns all error handlers.
        
        :return: A list that contains all error handlers.
        :rtype: list<tuple>
        """
        
        return self._get_handlers('error')
    
    default = property(_get_default, _set_default)
    checks = property(_get_checks, _set_checks)
    success = property(_get_success_handlers, _set_success_handlers)
    error = property(_get_error_handlers, _set_error_handlers)
