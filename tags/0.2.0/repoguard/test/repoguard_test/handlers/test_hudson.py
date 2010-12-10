# pylint: disable=R0903
# R0903: _UrlOpenResponseMock is just a mock and needs no more methods.
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
Test module for the Hudson handler.
"""


from configobj import ConfigObj

from repoguard.handlers import hudson
from repoguard_test.util import TestRepository, TestProtocol


_CONFIG_STRING = """
url='http://localhost/build'
token='test'
""".splitlines()


def _urlopen_mock(url, params):
    """ Mocks the urllib.urlopen function. """
    
    assert url == 'http://localhost/build'
    assert params == 'token=test'
    return _UrlOpenResponseMock()


class _UrlOpenResponseMock(object):
    """ Mocks the urllib.urlopen result. """
    
    def close(self):
        """ Does nothing. """
        
        pass


class TestHudson(object):
    """ Tests the Hudson handler. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        hudson.urlopen = _urlopen_mock
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        cls.handler = hudson.Hudson(cls.transaction)
        cls.config = ConfigObj(_CONFIG_STRING)
        
    def test_summarize(self):
        """ Tests the successful execution of the Hudson handler. """
        
        self.handler.summarize(self.config, TestProtocol(), True)
