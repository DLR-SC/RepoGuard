# pylint: disable=R0201, R0903
# R0201: Cannot make test methods static as nose would not find them anymore. 
# R0903: Currently, the test class has no additional methods.
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
Test methods for the Process class.
"""


from repoguard.core.process import execute, ProcessException


class TestProcess(object):
    """ Tests the process module. """
    
    def test_execute(self):
        """ Tests the execute method. """
        
        execute("svnlook help")

        try:
            execute("somecommand")
            assert False
        except ProcessException, error:
            assert error.exit_code != 0
            assert error.command == "somecommand"
            assert error.output != ""
