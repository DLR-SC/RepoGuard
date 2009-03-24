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
Tool for repoguard configuration validation.
"""


from __future__ import with_statement

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
        
    def _chhooks(self):
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
                with open(path, 'wb') as fp:
                    if not options.noact:
                        if os.name != 'nt':
                            fp.write("#!/bin/sh\n")
                        fp.write(infile)
                # Changing rights to executable.
                os.chmod(path, 755)
            else:
                with open(path, 'ra+b') as fp:
                    lines = fp.readlines()
                    if lines.count(infile):
                        print "%s already installed." % hook.capitalize()
                        return
                    
                    if exists:
                        question = msg % filename
                        if options.verbose and raw_input(question).lower().startswith("n"):
                            return
                    if not options.noact:
                        fp.write(infile + "\n")
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
        
        if not any((options.precommit, options.postcommit, options.main)):
            precommit = postcommit = config = True
        
        try:
            hooks = self._chhooks()
        except IOError, exc:
            print exc.message
            return 1
        
        if precommit:
            filename, hook = PRECOMMIT
            install_hook(filename, hook, hooks)
            
        if postcommit:
            filename, hook = POSTCOMMIT
            install_hook(filename, hook, hooks)
            
        if config:
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
            with open(path, 'rw+b') as fp:
                lines = fp.readlines()
                try:
                    index = lines.index(infile)
                    del lines[index]
                    fp.writelines(lines)
                except ValueError:
                    return
                
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
        
        if not any((options.precommit, options.postcommit, options.main)):
            precommit = postcommit = config = True
        
        try:
            hooks = self._chhooks()
        except IOError, exc:
            sys.stderr.write(exc.message)
            return 1
            
        if precommit:
            filename, hook = PRECOMMIT
            uninstall_hook(filename, hook, hooks)
            
        if postcommit:
            filename, hook = POSTCOMMIT
            uninstall_hook(filename, hook, hooks)
            
        if config:
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
        
        """
        
        def hook_exists(repoguard, hook, hooks, filename):
            path = os.path.join(hooks, filename)
            infile = constants.CONFIG_PATTERN % (repoguard, hook)
            with open(path, 'ra+b') as fp:
                lines = fp.readlines()
                return lines.count(infile) > 0
        
        repoguard = sys.argv[0].rsplit('-', 1)[0]
        try:
            hooks = self._chhooks()
        except IOError, exc:
            print exc.message
            return 1
            
        for filename, hook in (PRECOMMIT, POSTCOMMIT):
            if hook_exists(repoguard, hook, hooks, filename):
                print "%s hook installed" % hook.capitalize()
    
        path = os.path.join(hooks, constants.CONFIG_FILENAME)
        if os.path.exists(path):
            print "Configuration installed"  
        return 0
            
        