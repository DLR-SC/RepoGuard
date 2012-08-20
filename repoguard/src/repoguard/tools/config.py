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
Tool for repoguard configuration display and validation.
"""
 

import logging
import os

from repoguard.core import constants
from repoguard.core.logger import LoggerFactory
from repoguard.core.config import RepoGuardConfig, ProjectConfig
from repoguard.core.validator import ConfigValidator
from repoguard.tools.base import Tool


class Configuration(Tool):
    """
    Contains all command line tools for configuration validation and 
    representation.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        
        Tool.__init__(self, "Configuration Tools v0.1")
        
    @Tool.command_method(
        command = "validate",
        description = "Allows the validation of main files",
        usage = "\n  repoguard validate [options] path\n" \
              + "Arguments:\n" \
              + "  path\t\tPath to the configuration file that has to be " \
              + "validated."
    )
    def validate(self, parser):
        """
        Validates repoguard configuration files.
        
        :param parser: Command line parser.
        :type parser: optparse object.
        """
        
        parser.add_option(
            "-q", "--quiet", action="store_false", dest="verbose",
            help="be vewwy quiet (I'm hunting wabbits).", 
            default=True
        )
        options, args = parser.parse_args()
        
        if len(args) != 2:
            parser.print_help()
            return 1
        
        path = args[1]
        
        logging.basicConfig(format="%(message)s")
        logger = LoggerFactory().create('%s.tools.config' % constants.NAME)
        if options.verbose:
            level = logger.level
        else:
            level = logging.CRITICAL
        main_config = RepoGuardConfig(constants.CONFIG_PATH)
        config_validator = ConfigValidator(override=level)
        config_obj = ProjectConfig(path, template_dirs=main_config.template_dirs)
        for extend, path in config_obj.extended.iteritems():
            logger.info("Extending %s (%s)", extend, path)
        else:
            logger.info("Nothing to extend.")
        if config_validator.validate(config_obj):
            return 0
        else:
            return 1
    
    @Tool.command_method(
        command="show",
        description="Shows the extended presentation of the configuration",
        usage="\n  repoguard show [options] path\n" \
             + "Arguments:\n" \
             + "  path\t\tPath to the configuration file that has to be " \
             + "shown merged"
    )
    def show(self, parser):
        """
        Shows a configuration in his complete view with all extentions.
        
        :param parser: Parser associated with this tool.
        :type parser: optparse object.
        """
        
        args = parser.parse_args()[1]
        if len(args) != 2:
            parser.print_help()
            return 1
            
        path = args[1]
        hooks = os.path.dirname(os.path.abspath(path))
        main_config = RepoGuardConfig(constants.CONFIG_PATH)
        config_obj = ProjectConfig(path, hooks, main_config.template_dirs)
        config_obj.filename = None
        
        i = 0
        for line in config_obj.write():
            tmp = line.count('[') - 1
            if tmp > -1:
                i = tmp
            print ' ' * 3 * i + line
        return 0
