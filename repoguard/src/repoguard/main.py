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
The repoguard command line tool.
Contains the whole repoguard functionality for the command line.
Also allows the integration of the basic repoguard functionality in other
software systems.
"""


import sys

import pkg_resources

from optparse import OptionParser


def main(argv=sys.argv):
    """
    Main method that is responsible for the tool initialisation.
    
    :param argv: Arguments that has to be parsed.
    :type argv: list of command line arguments.
    """
    
    usage = "\n  repoguard [options] mode\n\n" \
          + "Following 'mode'-values are accepted:\n"
          
    tools = dict()
    
    entrypoints = dict()
    for entrypoint in pkg_resources.iter_entry_points("repoguard.tools"):
        entrypoints[entrypoint.name] = entrypoint.load()()
    names = entrypoints.keys()
    names.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
    for name in names:
        tool = entrypoints[name]
        descriptors = tool.descriptors.items()
        descriptors.sort(cmp=lambda x, y: cmp(x[0].lower(), y[0].lower()))
        
        usage += "%-18s\t%s\n" % (name, tool.description)
        for command, descriptor in descriptors:
            if tools.has_key(command):
                msg = "Command '%s' from tool '%s' already exists."
                raise KeyError(msg % (command, name))
            usage += "  %-18s\t%s\n" % (command, descriptor.description)
            tools[command] = (tool, descriptor)
        
    usage += "Write repoguard mode -h to get more help for every option"
    version = pkg_resources.require("repoguard")[0].version
    full_name = "RepoGuard Command Line Tools v" + version
    parser = OptionParser(usage=usage, version=full_name)
    if not argv[1:] or not tools.has_key(argv[1]):
        parser.parse_args()
        parser.print_help()
        return 1    
    
    tool, descriptor = tools[argv[1]]
    full_name = tool.__class__.__name__ + " Tools v" + version
    parser = OptionParser(usage=descriptor.usage, version=full_name)
    return getattr(tool, descriptor.method)(parser) or 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
