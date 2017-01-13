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
import json

import taskwarrior2net.validate as validate
import taskwarrior2net.edges as edges
import taskwarrior2net.config as config
import taskwarrior2net.net2dot as net2dot


def taskwarrior_json():
    """
    read input from taskwarrior via stdin,
    return list of dictionaries.
    """
    taskwarrioroutput = ','.join(sys.stdin.readlines())
    return json.loads('[' + taskwarrioroutput + "]")


tasks = taskwarrior_json()

conf = config.Config()

task_data = validate.TaskwarriorExploit(tasks, conf.excluded)

edges = edges.connector(task_data, ['state', 'path'], conf)

print(net2dot.generate_dot_source(edges,
    {
        'tag': {},
        'task': {},
        'project': {},
        'annotation': {},
        'state': {},
        'path': {}},
    {
        'task2tag': {},
        'task2project': {},
        'task2annotation': {},
        'task2state': {},
        'task2path': {}}))
