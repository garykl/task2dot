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

    def __init__(self, kind, n_1, n_2):
        self.kind = kind
        self.node1 = n_1
        self.node2 = n_2

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.kind + str(self.node1) + str(self.node2))

    def __repr__(self):
        return "Edge('{0}', {1}, {2})".format(self.kind, self.node1, self.node2)

    #def __str__(self):
        #return repr(self)



def connector(collections, udas):
    """
    generate data structure containing all data
    that is necessary for feeding the connections
    into the dot program.

    udas is a list UDA types. For each uda, check if there is a value in a task
    and save it as an edge.
    """

    def taskVSuda(task):
        res = set()
        for uda in udas:
            if uda in task.keys():
                for u in task[uda].split(','):
                    res.add(Edge('task2{0}'.format(uda),
                        Node('task', task['description']),
                        Node(uda, u)))
        return res

    def taskVStask(task, uuids):
        res = set()
        if task['description']:
            if 'depends' in task:
                for dep in task['depends'].split(','):
                    if dep in uuids:
                        res.add(Edge('task2task',
                            Node('task', collections.task_dict[dep]),
                            Node('task', collections.task_dict[task['uuid']])))
        return res

    def taskVStags(task, tags, excludedTaggedTaskStatus):
        res = set()
        if task['description']:
            if 'tags' in task.keys():
                for tag in task['tags']:
                    if tag in tags and not task['status'] in excludedTaggedTaskStatus:
                        res.add(Edge('task2tag',
                            Node('tag', tag),
                            Node('task', collections.task_dict[task['uuid']])))
        return res

    def taskVSprojects(task, excludedTaskStatus):
        res = set()
        if task['description']:
            if 'project' in task.keys():
                if task['project'] in collections.projects:
                    if not task['status'] in excludedTaskStatus:
                        res.add(Edge('task2project',
                            Node('task', collections.task_dict[task['uuid']]),
                            Node('project', task['project'])))
        return res

    def taskVSannotations(task):
        res = set()
        if task['status'] is not 'deleted':
            if 'annotations' in task:
                for a in task['annotations']:
                    if 'Started task' in a['description']:
                        continue
                    if 'Stopped task' in a['description']:
                        continue
                    res.add(Edge('task2annotation',
                        Node('annotation', a['description']),
                        Node('task', collections.task_dict[task['uuid']])))
        return res

    def projectVStags(task):
        res = set()
        if 'project' in task:
            if task['project'] in collections.projects:
                if 'tags' in task:
                    for t in task['tags']:
                        if t in collections.tags:
                            res.add(Edge('project2tag',
                                Node('tag', t),
                                Node('project', task['project'])))
        return res

    def tagVStags(task):
        res = set()
        if 'tags' in task:
            for t1 in task['tags']:
                for t2 in task['tags']:
                    if t1 != t2:
                        res.add(Edge('tag2tag',
                            Node('tag', t1),
                            Node('tag', t2)))
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
                    res.add(Edge('project2project',
                        Node('project', p2),
                        Node('project', p1)))
        return res


    res = set()
    res.update(projectVSprojects())

    for t in collections.tasks:
        res.update(taskVStask(t, collections.uuids))
        res.update(taskVStags(t, collections.tags, ['deleted']))
        res.update(taskVSprojects(t, ['delted']))
        res.update(taskVSannotations(t))
        res.update(projectVStags(t))
        res.update(tagVStags(t))
        res.update(taskVSuda(t))

    return res
