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
Constants definition for the whole repoguard.
"""

import os

NAME = "repoguard"

CHECKS = "checks"
HANDLERS = "handlers"

PRECOMMIT = "precommit"
POSTCOMMIT = "postcommit"
HOOKS = (PRECOMMIT, POSTCOMMIT)

SUCCESS = "success"
WARNING = "warning"
DELAYONERROR = "delayonerror"
ABORTONERROR = "abortonerror"
EXCEPTION = "exception"
ERROR = "error"
INTERPS = (WARNING, DELAYONERROR, ABORTONERROR)

CHECK_REGEX = "(?P<name>[A-Za-z]{1}[\w]*)\.?(?P<config>[\w]+)?\.?(?P<interp>%s|%s|%s)?" % INTERPS
HANDLER_REGEX = "(?P<name>[A-Za-z]{1}[\w]*)\.?(?P<config>[\w]+)?"

CONFIG_POSTFIX = ".conf"
TEMPLATE_POSTFIX = ".tpl.conf"
CONFIG_FILENAME = "repoguard" + CONFIG_POSTFIX
LOGGER_FILENAME = "logger" + CONFIG_POSTFIX

BUILDIN_TPL_PATH = 'cfg/templates'

#changes here has no effect on the setup.py file.
WIN32_CONFIG_HOME = os.path.join(os.path.expanduser("~") , '.repoguard')
LINUX_CONFIG_HOME = '/usr/local/share/repoguard'

WIN32_CONFIG_PATTERN = "%s %s %%1 %%2 || exit 1"
LINUX_CONFIG_PATTERN = "%s %s $1 $2 || exit 1"

WIN32_PRECOMMIT_FILENAME = "pre-commit.bat"
LINUX_PRECOMMIT_FILENAME = "pre-commit"

WIN32_POSTCOMMIT_FILENAME = "post-commit.bat"
LINUX_POSTCOMMIT_FILENAME = "post-commit"

#OS dependend constants generation.
CONFIG_HOME = LINUX_CONFIG_HOME
CONFIG_PATTERN = LINUX_CONFIG_PATTERN
PRECOMMIT_FILENAME = LINUX_PRECOMMIT_FILENAME
POSTCOMMIT_FILENAME = LINUX_POSTCOMMIT_FILENAME
if os.name == 'nt':
    CONFIG_HOME = WIN32_CONFIG_HOME
    CONFIG_PATTERN = WIN32_CONFIG_PATTERN
    PRECOMMIT_FILENAME = WIN32_PRECOMMIT_FILENAME
    POSTCOMMIT_FILENAME = WIN32_POSTCOMMIT_FILENAME
    
CONFIG_PATH = os.path.join(CONFIG_HOME, CONFIG_FILENAME)
LOGGER_PATH = os.path.join(CONFIG_HOME, LOGGER_FILENAME)