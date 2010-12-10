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
Test module foer the hudson handler.
"""

from configobj import ConfigObj

from repoguard.handlers import hudson
from repoguard.testutil import TestRepository, TestProtocol

config = """
url='http://localhost/build'
token='test'
""".splitlines()

def urlopen(url, params):
    assert url == 'http://localhost/build'
    assert params == 'token=test'
    return ResponseMock()

class ResponseMock(object):
    def close(self):
        pass

class TestHudson(object):
    
    @classmethod
    def setup_class(cls):
        hudson.urlopen = urlopen
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        cls.handler = hudson.Hudson(cls.transaction)
        cls.config = ConfigObj(config)
        
    def test_summarize(self):
        self.handler.summarize(self.config, TestProtocol(), True)