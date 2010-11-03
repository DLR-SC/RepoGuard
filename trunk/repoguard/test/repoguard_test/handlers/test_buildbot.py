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
Test case for the buildbot script.
"""


from configobj import ConfigObj

from repoguard.handlers.buildbot import BuildBot


_CONFIG_STRING = """
url=localhost
port=8007
user=admin
password=foo
""".splitlines()
    
    
class TestBuildBot(object):
    """ Tests the buildbot handler. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.buildbot = BuildBot(None)
        cls.config = ConfigObj(_CONFIG_STRING)
