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
Setup script for the RepoGuard distribution.
"""


import sys
import os

from setuptools import setup, find_packages


WIN32_CONFIG_HOME = os.path.join(os.path.expanduser("~"), '.repoguard')
LINUX_CONFIG_HOME = '/usr/local/share/repoguard'
CONFIG_HOME = WIN32_CONFIG_HOME if sys.platform == 'win32' else LINUX_CONFIG_HOME

setup(
    name='repoguard', 
    version='0.1',
    description='RepoGuard is a framework for Subversion hook scripts.',
    long_description='RepoGuard is a framework for Subversion pre-commit hooks in order to implement checks of the to be commited files before they are commited. For example, you can check for the code style or unit tests. The output of the checks can be send by mail or be written into a file or simply print to the console..',
    author='Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)',
    author_email='Malte.Legenhausen@dlr.de',
    maintainer='Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)',
    maintainer_email='malte.legenhausen@dlr.de',
    url='http://repoguard.tigris.org',
    classifiers=[
        'Development Status :: 3 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Version Control',
    ],
    
    namespace_packages=[
        'repoguard.checks',
        'repoguard.handlers',
        'repoguard.modules',
        'repoguard.tools'
    ],
    
    packages=find_packages('src', exclude=["*.tests", "*.testutil"]),
    package_dir={
        '' : 'src'
    },
    
    data_files=[
        (CONFIG_HOME, [
            'cfg/repoguard.conf',
            'cfg/logger.conf'
        ]),
        ('cfg/templates', [
            'cfg/templates/default.tpl.conf',
            'cfg/templates/python.tpl.conf'
        ])
    ],
    
    install_requires=[
        'configobj>=4.5.3',
        'pytz==2008c',
        'soaplib>=0.7.2dev-r27'
    ],
    
    extras_require={
        'pylint' : [
            'logilab-common>=0.33.0', 
            'logilab-astng>=0.17.2',
            'pylint>=0.14.0'
        ],
        'suds' : [
            'suds>=0.3.3'
        ],
        'twisted' : [
            'twisted>=8.1.0'
        ]
    },
    
    entry_points={
        'console_scripts': [
            'repoguard = repoguard.main:main'
        ],
                    
        'repoguard.checks' : [
            'AccessRights = repoguard.checks.accessrights:AccessRights',
            'ASCIIEncoded = repoguard.checks.asciiencoded:ASCIIEncoded',
            'CaseInsensitiveFilenameClash = repoguard.checks.caseinsensitivefilenameclash:CaseInsensitiveFilenameClash',
            'Checkout = repoguard.checks.checkout:Checkout',
            'Checkstyle = repoguard.checks.checkstyle:Checkstyle',
            'Keywords = repoguard.checks.keywords:Keywords',
            'Log = repoguard.checks.log:Log',
            'Mantis = repoguard.checks.mantis:Mantis [suds]',
            'PyLint = repoguard.checks.pylint_:PyLint [pylint]',
            'RejectTabs = repoguard.checks.rejecttabs:RejectTabs',
            'UnitTests = repoguard.checks.unittests:UnitTests',
            'XMLValidator = repoguard.checks.xmlvalidator:XMLValidator'
        ],
        
        'repoguard.handlers' : [
            'Mail = repoguard.handlers.mail:Mail',
            'Console = repoguard.handlers.console:Console',
            'File = repoguard.handlers.file:File',
            'Mantis = repoguard.handlers.mantis:Mantis [suds]',
            'BuildBot = repoguard.handlers.buildbot:BuildBot [twisted]',
            'Hudson = repoguard.handlers.hudson:Hudson'
        ],
        
        'repoguard.tools' : [
            'Checker = repoguard.tools.checker:Checker',
            'Configuration = repoguard.tools.config:Configuration',
            'Repository = repoguard.tools.repository:Repository'
        ],
        
        'svnchecker.modules' : [
            'Mantis = repoguard.modules.mantis:Mantis',
            'Trac = repoguard.modules.trac:Trac',
            'Bugzilla = repoguard.modules.bugzilla:Bugzilla',
            'GForge = repoguard.modules.gforge:GForge'
        ]
    }
)