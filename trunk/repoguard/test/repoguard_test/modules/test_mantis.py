# pylint: disable=C0103,R0903
# C0103: Necessary to ignore argument of mock method parameters.
# R0903: Some mocks have to few method but they are only data object mocks
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
Tests the Mantis module.
"""


from configobj import ConfigObj

from repoguard.modules.mantis import Mantis, Config


_CONFIG_STRING = """
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
"""

_COMMIT_MESSAGE = """
mantis id 3662
Test1
MANTIS ID 3883
Test2
"""


class _ServiceMock(object):
    """ Mocks the Mantis web service. """ 

    _issue_data = None
    
    def __init__(self):
        """ Initializes the issue data structure. """
        
        custom_field = _CustomFieldDataMock()
        self._issue_data = _IssueDataMock(custom_fields=\
                                           {custom_field: custom_field})

    @staticmethod
    def mc_issue_exists(_, __, ___):
        """ Always returns C{True}. """
        
        return True
    
    def mc_issue_get(self, _, __, ___):
        """ Returns the prepared issue data. """
        
        return self._issue_data
    
    def mc_issue_note_add(self, _, __, ___, ____):
        """ Does nothing. """
        
        pass
    
    def mc_issue_update(self, _, __, ___, ____):
        """ Does nothing. """
        
        pass


class _ObjectRefDataMock(object):
    """ Mocks the Mantis web service data structure C{ObjectRef}. """
     
    def __init__(self, id_=0, name=""):
        """ Initializes properties. """
        
        self.id = id_
        self.name = name
        
    def __getitem__(self, index):
        """ Implements indexing. """
        
        if index == 0:
            return self.id
        elif index == 1:
            return self.name
        else:
            raise IndexError("")


class _CustomFieldDataMock(object):
    """ Mocks the Mantis web service data structure 
    C{CustomFieldValueForIssueDataArray}. """
    
    def __init__(self, field=_ObjectRefDataMock(name="SVNRevision"), value=""):
        """ Initializes properties. """
        
        self.field = field
        self.value = value

class _AccountDataMock(object):
    """ Mocks the Mantis web service data structure C{AccountData}. """
    
    def __init__(self, id_=1, name="", real_name="", email=""):
        """ Initializes properties. """
        
        self.id = id_
        self.name = name
        self.real_name = real_name
        self.email = email

class _IssueDataMock(object):
    """ Mocks the Mantis web service data structure C{IssueData}. """
    
    def __init__(self, id_=0, handler=_AccountDataMock(), 
                 status=_ObjectRefDataMock(), 
                 custom_fields=None):
        """ Initializes properties. """
        
        self.id = id_
        self.handler = handler
        self.status = status
        self.custom_fields = custom_fields
    

class _NoteData(object):
    """ Mocks (simplified )the Mantis web service 
    data structure C{IssueNoteData}. """
            
    def __init__(self, text):
        """ Initializes properties. """
    
        self.text = text

        
class _ClientMock(object):
    """" Mocks the Mantis web service client. """
    
    service = _ServiceMock()
    
    class _FactoryMock(object):
        """ Mocks the factory instance. """
        
        @staticmethod
        def create(data):
            """ Mocks method for issue note data creation. """
            
            return _NoteData(data)
        
    factory = _FactoryMock()
    
    def __init__(self, _):
        """ Does nothing. """
        
        pass
    

class _ImportMock(object):
    """ Mocks the Import class used for name space binding. """
    
    @classmethod
    def bind(cls, _):
        """ Does nothing. """
        
        pass


class TestMantis(object):
    """ Tests the Mantis connector module. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        config = ConfigObj(_CONFIG_STRING.splitlines())
        config = Config.from_config(config)
        from repoguard.modules import mantis
        mantis.Import = _ImportMock
        mantis.Client = _ClientMock
        cls.mantis = Mantis(config)
        
    def test_pattern(self):
        """ Tests message extraction. """
        
        assert self.mantis.extract_issues(_COMMIT_MESSAGE) == ["3662", "3883"]

    def test_issue_exists(self):
        """ Checks issue existence. """
        
        assert self.mantis.issue_exists(1)
        assert self.mantis.issue_exists(2)

    def test_issue_get_status(self):
        """ Checks issue status determination. """
        
        self.mantis.issue_get_status("1")

    def test_issue_get_handler(self):
        """ Tests handler determination. """
        
        self.mantis.issue_get_handler("1")
        self.mantis.issue_get_handler("2")

    def test_issue_add_note(self):
        """" Tests adding a note. """
        
        self.mantis.issue_add_note("1", "test")
        
    def test_issue_set_custom_field(self):
        """ Tests setting a custom field. """
        
        self.mantis.issue_set_custom_field("1", "SVNRevision", "123")
