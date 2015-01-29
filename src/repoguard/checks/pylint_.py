# pylint: disable-msg=W0232,R0903,C0103
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
Python coding style check.
"""


import os
import StringIO
from tempfile import gettempdir

from pylint import lint
from pylint.reporters.text import TextReporter

from repoguard.core.module import Check, ConfigSerializer, Array, String


class Config(ConfigSerializer):
    """
    Configuration for PyLint check.
    """
    
    class types(ConfigSerializer.types):
        """
        Configurable parameters.
        """
        
        check_files = Array(String, optional=True, default=[".*\.py"])
        ignore_files = Array(String, optional=True, default=[])
        pylint_home = String(
            optional=True, default=os.path.join(gettempdir(), '.pylint.d')
        )
        pylintrc = String(optional=True)
    
class PyLint(Check):
    """
    Check that executes the code checking tool PyLint from logilab on all
    commited python files.
    """
    
    __config__ = Config
    
    def _run(self, config):
        """
        Run the pylint check with the given config.
        
        :param config: The config object described by Config.
        :type config: Config
        """
        
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        # Exit when no files has to be checked.
        if not files:
            self.logger.debug("PyLint check skipped. No files for check.")
            return self.success()
        
        # Defining pylint home directory.
        os.environ['PYLINTHOME'] = config.pylint_home
        self.logger.debug("PyLint Home is used at '%s'.", config.pylint_home)
        
        # Determine which pylintrc file is used for the validation.
        if config.pylintrc:
            self.logger.debug("Pylintrc is used at '%s'.", config.pylintrc)
            os.environ['PYLINTRC'] = config.pylintrc
        else:
            self.logger.debug("Default PyLintRC is used.")
        
        # Only added or updated files will be checked.
        files = [
            self.transaction.get_file(name) 
            for name, attr in files.iteritems() 
                if attr in ["A", "U", "UU"]
        ]
        
        if not files:
            self.logger.debug("No files to validate. PyLint check skipped.")
            return self.success()
        
        output = StringIO.StringIO()
        reporter = TextReporter(output)
        
        # Mock to prevent the sys.exit called by pylint.lint.Run.__init__
        lint.sys.exit = lambda _: 0
        
        self.logger.debug("PyLint is running...")
        lint.Run(["--reports=n"] + files, reporter=reporter)
    
        output = output.getvalue()
        self.logger.debug("PyLint output:\n %s", output)
        if output:
            return self.error(output)
        else:
            return self.success()
