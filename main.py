#!/usr/bin/env python3
#
#
# Copright 2017 Gary Klindt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

import extern
import edges
import validate


inp = extern.interpreteInput(sys.argv[1:])
filename = inp['filename']
confKey = inp['conf']
tagExclude = inp['notags']

tasks = extern.taskwarriorJSON()

class NodeConfig:
    def __init__(self):
        self.tasks = True
        self.tags = True
        self.projects = True
        self.annotations = True

class EdgeConfig:
    def __init__(self):
        self.tagVStags = False
        self.projectVStags = False

## fine tune node existence and connection creation
class ExclusionConfig:
    def __init__(self):
        self.tags = [] # those nodes are supressed
        self.projects = []
        self.taskStatus = ['deleted'] # nodes removed
        self.taggedTaskStatus = set(['deleted']) # connection between tags and those are supressed
        self.annotationStatus = ['deleted']

class Config:
    def __init__(self):
        self.nodes = NodeConfig()
        self.edges = EdgeConfig()
        self.excluded = ExclusionConfig()
        self.tagHierarchy = {}

config = Config()
taskwarriordata = validate.TaskwarriorExploit(tasks, config.excluded)
edges = edges.connector(config, taskwarriordata)
for e in edges:
    print(e)
