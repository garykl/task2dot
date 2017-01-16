# Copright 2014 Gary Klindt
#
# This file is part of dotwarrior.
#
# dotwarrior is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dotwarrio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dotwarrior.  If not, see <http://www.gnu.org/licenses/>.
class Node:

    def __init__(self, kind, label):
        self.kind = kind
        self.label = label

    def __hash__(self):
        return hash(self.kind + self.label)

    def __repr__(self):
        return "Node('{0}', '{1}')".format(self.kind, self.label)


class Edge:

    def __init__(self, n_1, n_2):
        self.node1 = n_1
        self.node2 = n_2

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self.node1) + str(self.node2))

    def __repr__(self):
        return "Edge({1}, {2})".format(self.node1, self.node2)



def connector(collections, udas):
    """
    generate data structure containing all data
    that is necessary for feeding the connections
    into the dot program.

    udas is a list UDA types. For each uda, check if there is a value in a task
    and save it as an edge.
    """



    def task2uda(task, uda):
        res = set()
        if uda in task.keys():
            for u in task[uda].split(','):
                res.add(Edge(
                    Node('task', task['description']),
                    Node(uda, u)))
        return res


    def taskVStask(task):
        res = set()
        if task['description']:
            if 'depends' in task:
                for dep in task['depends'].split(','):
                    if dep in collections.uuids:
                        res.add(Edge(
                            Node('task', collections.task_dict[dep]['description']),
                            Node('task', task['description'])))
        return res


    def task2list(task, uda):
        res = set()
        for tag in task['tags']:
            if not task['status'] is 'deleted':
                for elem in task[uda]:
                    res.add(Edge(
                        Node('task', task['description']),
                        Node(uda, elem)))
        return res


    def taskVSprojects(task, excludedTaskStatus):
        res = set()
        if task['description']:
            if 'project' in task.keys():
                if task['project'] in collections.projects:
                    if not task['status'] in excludedTaskStatus:
                        res.add(Edge(
                            Node('task', task['description']),
                            Node('project', task['project'])))
        return res


    def projectVSprojects():
        """
        let's support subprojects.
        """
        res = set()
        for p1 in collections.projects:
            for p2 in collections.projects:
                cond = p1 in p2 and p1 != p2
                if cond:
                    res.add(Edge(
                        Node('project', p2),
                        Node('project', p1)))
        return res


    res = set()
    res.update(projectVSprojects())

    for t in collections.tasks:

        res.update(taskVStask(t))
        res.update(task2list(t, 'tags'))
        res.update(task2uda(t, 'project'))

        for u in udas:
            res.update(task2uda(t, u))

    return res


def add_indirect_edges(edges, kind_1, kind_2):
    """
    If a node has a connection to
    """
    pass
