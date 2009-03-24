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

"""


import os
import tempfile

from validate import ValidateError

from repoguard.core import constants
from repoguard.core.checker import RepoGuard
from repoguard.core.config import RepoGuardConfig
from repoguard.core.logger import LoggerFactory

from repoguard.tools.base import Tool


description = "Runs the %s as %s." % (constants.NAME, '%s')
usage = """
  repoguard %s [options] repo_path txn_name
Arguments:
  repo_path\tThe path to this repository
  txn_name\tThe name of the transaction about to be committed
"""

os.environ['PYTHON_EGG_CACHE'] = tempfile.gettempdir()

class Checker(Tool):
    """
    Tool for the repoguard execution on transaction base.
    """
    
    def __init__(self):
        """
        Constructor.
        """
        
        Tool.__init__(self, "Checker tools v0.1")
        
    @Tool.command_method(
        command = constants.PRECOMMIT, 
        description = description % constants.PRECOMMIT, 
        usage = usage % constants.PRECOMMIT
    )
    @Tool.command_method(
        command = constants.POSTCOMMIT, 
        description = description % constants.POSTCOMMIT,
        usage = usage % constants.POSTCOMMIT
    )
    def commit(self, parser):
        """
        Parses the incoming command line.
        
        :param parser: Parser for the current command line.
        :type parser: optparse object.
        
        :return: The return code.
        :rtype: 0 for success else error.
        """
        
        args = parser.parse_args()[1]
        if len(args) != 3:
            parser.print_help()
            return 1
        
        hook, repo_path, txn_name = args
        return self.checker(hook, repo_path, txn_name)
    
    def checker(self, hook, repo_path, txn_name):
        """
        Function to singularize the repoguard in precommit or postcommit mode.
        
        :param hook: Execute the repoguard as pre- or postcommit.
        :type hook: string
        
        :param repo_path: The path to the repository.
        :type repo_path: string
        
        :param txn_name: The name of the current transaction.
        :type txn_name: string
        """
        
        logger = LoggerFactory().create('%s.tools.checker' % constants.NAME)
        
        hooks_path = os.path.abspath(os.path.join(repo_path, "hooks"))
        project_config = os.path.join(hooks_path, constants.CONFIG_FILENAME)
            
        # Working directory change to the hooks location.
        os.chdir(hooks_path)
        
        result = constants.ERROR
        logger.debug("RepoGuard initializing...")
        repoguard = RepoGuard(hook, repo_path)
        try:
            logger.debug("Loading transaction...")
            repoguard.load_transaction(txn_name)
    
            logger.debug("Loading configuration...")
            main_config = RepoGuardConfig(constants.CONFIG_PATH)
            repoguard.load_config(main_config.template_dirs, project_config)
            if main_config.validate:
                repoguard.validate()
            else:
                logger.warning("Validation skipped.")
            logger.debug("RepoGuard running...")
            result = repoguard.run()
        except ValidateError, exc:
            msg = "Configuration validation error cause: %s"
            logger.exception(msg, exc.message)
        except Exception, exc:
            msg = "%s exception cause: '%s'"
            logger.exception(msg, exc.__class__.__name__, exc.message)
        finally:
            logger.debug("RepoGuard finished with %s.", result)
            return 0 if result == constants.SUCCESS else 1
        