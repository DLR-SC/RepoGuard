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
Main tool to handle pre and post commits.
"""


import os
import tempfile

import validate

from repoguard.core import constants
from repoguard.core.checker import RepoGuard
from repoguard.core.config import RepoGuardConfig
from repoguard.core.logger import LoggerFactory

from repoguard.tools.base import Tool


_DESCRIPTION = "Runs the %s as %s." % (constants.NAME, '%s')
_USAGE = """
  repoguard %s [options] repo_path [txn_name]
Arguments:
  repo_path\tThe path to this repository.
  txn_name\tThe name of the transaction about to be committed or
  \t\tthe revision number. If you omit the option, the HEAD
  \t\trevision will be used. 
"""

os.environ['PYTHON_EGG_CACHE'] = tempfile.gettempdir()

class Checker(Tool):
    """
    Tool for the repoguard execution on transaction base.
    """
    
    def __init__(self):
        Tool.__init__(self, "Checker tools v0.2")
        
    @Tool.command_method(
        command = constants.PRECOMMIT, 
        description = _DESCRIPTION % constants.PRECOMMIT, 
        usage = _USAGE % constants.PRECOMMIT
    )
    @Tool.command_method(
        command = constants.POSTCOMMIT, 
        description = _DESCRIPTION % constants.POSTCOMMIT,
        usage = _USAGE % constants.POSTCOMMIT
    )
    def commit(self, parser):
        """
        Parses the incoming command line.
        
        :param parser: Parser for the current command line.
        :type parser: optparse object.
        
        :return: The return code.
        :rtype: 0 for success else error.
        """
        
        parser.add_option(
            "-p", "--profile", dest="profile_name", default=None,
            help="Concrete profile which should be executed."
        )
        parser.add_option(
            "--halt-on-exception", action="store_true", default=False, dest="halt_on_exception",
            help=(
                "Causes the hook to return an error when an unexpected exception occurs.\n"
                "Default behavior: Exception are logged but the hook succeeds.")
        )
        
        options, args = parser.parse_args()
        if len(args) == 3:
            hook, repo_path, txn_name = args
        elif len(args) == 2:
            hook, repo_path = args
            txn_name = None
        else:
            parser.print_help()
            return 1
        
        return self.checker(hook, repo_path, txn_name, options.profile_name, options.halt_on_exception)
    
    @staticmethod
    def checker(hook, repo_path, txn_name, profile_name, halt_on_exception):
        """
        Function to singularize the repoguard in precommit or postcommit mode.
        
        :param hook: Execute the repoguard as pre- or postcommit.
        :type hook: string
        
        :param repo_path: The path to the repository.
        :type repo_path: string
        
        :param txn_name: The name of the current transaction.
        :type txn_name: string
        
        :param halt_on_exception: Flag which indicates whether we halt on unexpected exceptions or not.
        :type halt_on_exception: boolean
        """
        
        logger = LoggerFactory().create('%s.tools.checker' % constants.NAME)
        try:
            hooks_path = os.path.abspath(os.path.join(repo_path, "hooks"))
            project_config = os.path.join(hooks_path, constants.CONFIG_FILENAME)
            os.chdir(hooks_path)
            
            logger.debug("RepoGuard initializing...")
            repoguard = RepoGuard(hook, repo_path)
        
            logger.debug("Loading transaction...")
            repoguard.load_transaction(txn_name)
    
            logger.debug("Loading configuration...")
            main_config = RepoGuardConfig(constants.CONFIG_PATH)
            repoguard.load_config(main_config.template_dirs, project_config)
            
            logger.debug("Validating configuration...")
            if main_config.validate:
                repoguard.validate()
            else:
                logger.warning("Validation skipped.")
            
            logger.debug("RepoGuard running...")
            if profile_name:
                result = repoguard.run_profile(profile_name)
            else:   
                result = repoguard.run()

            logger.debug("RepoGuard finished with %s.", result)
            if result == constants.SUCCESS:
                return 0
            else:
                return 1
        except validate.ValidateError:
            logger.exception("The configuration is invalid!")
            return 1
        except: # pylint: disable=W0702
            logger.exception(
                "An unexpected error occurred during the RepoGuard run! Halt on exception is '%s'." % halt_on_exception)
            if not halt_on_exception:
                return 0
            else:
                return 1
