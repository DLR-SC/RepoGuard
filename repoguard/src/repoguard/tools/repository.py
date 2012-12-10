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
Installs/uninstalls RepoGuard in/from a repository.
"""


import os
import sys

from configobj import ConfigObj

from repoguard.core import constants
from repoguard.tools.base import Tool


PRECOMMIT = constants.PRECOMMIT_FILENAME, "precommit"
POSTCOMMIT = constants.POSTCOMMIT_FILENAME, "postcommit"

class Repository(Tool):
    """
    Tool class that is responsible for the installation, deinstallation and the
    current status of the repoguard in the current repository.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        
        Tool.__init__(self)
        
        self.version = "0.1"
        
    @staticmethod
    def _chhooks():
        """
        Changes the cwd to the hooks directory and returns the hooks path.
        
        :return: The path to the hooks location.
        :rtype: string
        
        :raise: IOError if no hooks directory was found.
        """
        hooks = os.getcwd()
        if not hooks.endswith('hooks'):
            hooks = os.path.join(hooks, 'hooks')
            if not os.path.exists(hooks):
                raise IOError("No hooks directory found.")
            os.chdir(hooks)
        return hooks
        
    @Tool.command_method(
        command="repo-install",
        description="Installs the repoguard in the current repository",
        usage=""
    )
    def install(self, parser):
        """
        Installs the repoguard in the current repository.
        
        :param parser: The parser that is responsible for the commandline.
        :type parser: optparse object.
        """
        
        def install_hook(filename, hook, hooks):
            """
            Installs a hook in the given hooks directory.
            
            :param filename: The hook filename.
            :type filename: string
            
            :param hook: The hook that has to be installed.
            :type hook: string
            
            :param hooks: The hooks directory.
            :type hooks: string
            """
            
            path = os.path.join(hooks, filename)
            exists = os.path.exists(path)
            infile = constants.CONFIG_PATTERN % (repoguard, hook)
            msg = "%s already exists. You want to append the repoguard? (yes/no) "
            if not exists:
                file_object = open(path, 'wb')
                try:
                    if not options.noact:
                        if os.name != 'nt':
                            file_object.write("#!/bin/sh\n")
                        file_object.write(infile)
                finally:
                    file_object.close()
                # Changing rights to executable.
                os.chmod(path, 0744)
            else:
                file_object = open(path, 'r+ab')
                try:
                    lines = file_object.readlines()
                    if lines.count(infile):
                        print "%s already installed." % hook.capitalize()
                        return
                    
                    if exists:
                        question = msg % filename
                        if options.verbose and raw_input(question).lower().startswith("n"):
                            return
                    if not options.noact:
                        file_object.write(infile + "\n")
                finally:
                    file_object.close()
            if options.verbose:
                print "%s successfully added." % hook.capitalize()        
                        
        def install_config(hooks, template):
            """
            Installes a main under the given hoks directory.
            
            :param hooks: The hook directory.
            :type hooks: string
            
            :param template: The template from with the main has to extend.
            :type template: string
            """
            path = os.path.join(hooks, constants.CONFIG_FILENAME)
            msg = "%s already exists. Do you want to override? (yes/no) "
            if not os.path.exists(path) \
            or not options.verbose \
            or raw_input(msg % constants.CONFIG_FILENAME).lower().startswith("y"):
                if options.verbose:
                    msg = "Writing file %s.\n"
                    print msg % constants.CONFIG_FILENAME
                
                indict = {
                    'vcs' : 'svn'
                }
                if template:
                    indict['extends'] = template
                else:
                    indict.update({
                        'profiles' : {
                            'default' : {
                                'precommit' : {
                                    'checks' : [],
                                    'success' : [],
                                    'error' : []
                                },
                                'postcommit' : {
                                    'checks' : [],
                                    'success' : [],
                                    'error' : []
                                }
                            }
                        }
                    })
                config = ConfigObj()
                config.initial_comment.append(
                    "%s config file for '%s'" % (
                        constants.NAME, hooks.split(os.sep)[-2]
                    )
                )
                config.update(indict)
                config.filename = path
                if not options.noact:
                    config.write()
        
        parser.add_option(
          "-n", "--no-act", dest="noact", action="store_true",
          help="executes the repo_installer without changing anything",
          default=False
        )
        parser.add_option(
          "-q", "--quiet", action="store_false", dest="verbose",
          help="be vewwy quiet (I'm hunting wabbits).", 
          default=True
        )
        parser.add_option(
            "-r", "--precommit", action="store_true", dest="precommit",
            help="install precommit", default=False
        )
        parser.add_option(
            "-o", "--postcommit", action="store_true", dest="postcommit",
            help="install postcommit", default=False
        )
        parser.add_option(
            "-c", "--main", action="store_true", dest="main",
            help="install configuration", default=False
        )
        parser.add_option(
            "-t", "--template", action="store", dest="template",
            help="extended configuration", metavar="TEMPLATE", default=""
        )
        options = parser.parse_args()[0]
        # convert the python script path to executable path.
        repoguard = sys.argv[0].rsplit('-', 1)[0]
        
        if not (options.precommit or options.postcommit or options.main):
            options.precommit = options.postcommit = options.main = True
        
        try:
            hooks = self._chhooks()
        except IOError, exc:
            print exc
            return 1
        
        if options.precommit:
            filename, hook = PRECOMMIT
            install_hook(filename, hook, hooks)
            
        if options.postcommit:
            filename, hook = POSTCOMMIT
            install_hook(filename, hook, hooks)
            
        if options.main:
            install_config(hooks, options.template)
            
        if options.verbose:
            print "RepoGuard is successfully installed."
        return 0
    
    @Tool.command_method(
        command="repo-uninstall",
        description="Deinstalls the repoguard form the current repository",
        usage=""
    )
    def uninstall(self, parser):
        """
        Method that is responsible for the uninstallation of the repoguard from
        the current repository.
        
        :param parser: The parser for the current commandline.
        :type parser: optparse object.
        """
        
        def uninstall_hook(filename, hook, hooks):
            path = os.path.join(hooks, filename)
            if not os.path.exists(path):
                return
            
            infile = constants.CONFIG_PATTERN % (repoguard, hook)
            file_object = open(path, 'rw+b')
            try:
                lines = file_object.readlines()
                try:
                    index = lines.index(infile)
                    del lines[index]
                    file_object.writelines(lines)
                except ValueError:
                    return
            finally:
                file_object.close()
                
            if not lines:
                os.remove(path)
            if options.verbose:
                print "%s sucessfully removed." % hook
        
        parser.add_option(
            "-q", "--quiet", action="store_false", dest="verbose",
            help="be vewwy quiet (I'm hunting wabbits).", default=True
        )
        parser.add_option(
            "-r", "--precommit", action="store_true", dest="precommit",
            help="uninstall precommit", default=False
        )
        parser.add_option(
            "-o", "--postcommit", action="store_true", dest="postcommit",
            help="uninstall postcommit", default=False
        )
        parser.add_option(
            "-c", "--main", action="store_true", dest="main",
            help="uninstall configuration", default=False
        )
        options = parser.parse_args()[0]
        repoguard = sys.argv[0].rsplit('-', 1)[0]
        
        if not (options.precommit or options.postcommit or options.main):
            options.precommit = options.postcommit = options.main = True
        
        try:
            hooks = self._chhooks()
        except IOError, exc:
            sys.stderr.write(str(exc))
            return 1
            
        if options.precommit:
            filename, hook = PRECOMMIT
            uninstall_hook(filename, hook, hooks)
            
        if options.postcommit:
            filename, hook = POSTCOMMIT
            uninstall_hook(filename, hook, hooks)
            
        if options.main:
            path = os.path.join(hooks, constants.CONFIG_FILENAME)
            if os.path.exists(path):
                os.remove(path)
                if options.verbose:
                    msg = "%s successfully removed."
                    print msg % constants.CONFIG_FILENAME
        return 0
    
    @Tool.command_method(
        command="repo-status",
        description="Shows the repoguard status of the current repository",
        usage=""
    )
    def status(self, _):
        """
        Checks which RepoGuard components are installed for the repository.
        """
        
        def hook_exists(repoguard, hook, hooks, filename):
            path = os.path.join(hooks, filename)
            infile = constants.CONFIG_PATTERN % (repoguard, hook)
            try:
                file_object = open(path, 'ra+b')
                try:
                    lines = file_object.readlines()
                    return lines.count(infile) > 0
                finally:
                    file_object.close()
            except IOError:
                return False
        
        repoguard = sys.argv[0].rsplit('-', 1)[0]
        try:
            hooks = self._chhooks()
        except IOError, exc:
            print exc
            return 1
            
        for filename, hook in (PRECOMMIT, POSTCOMMIT):
            if hook_exists(repoguard, hook, hooks, filename):
                print "%s hook installed" % hook.capitalize()
            else:
                print "%s hook NOT installed" % hook.capitalize()
    
        path = os.path.join(hooks, constants.CONFIG_FILENAME)
        if os.path.exists(path):
            print "Configuration installed"
        else:
            print "Configuration NOT installed"
        return 0
