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

################################################################################
#
# - This script expects json-output from taskwarrior as standard input.
# - Command line arguments are read.
#    - All arguments with a leading '-' lead to the exclusion of the specific
#      node.
#    - All arguments with a leading '--' lead to the exclusion of that node type
#
################################################################################
import sys
import os
import subprocess
import json
import textwrap



################################################################################
##
##  extracting the base structure of the tasks
##
################################################################################


class Node:

    def __init__(self, kind, label):
        self.kind = kind
        self.label = label.replace('"', '\\"')

    def __hash__(self):
        return hash(self.kind + self.label)

    def __repr__(self):
        return "Node('{0}', '{1}')".format(self.kind, self.label)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Edge:

    def __init__(self, n_1, n_2):
        self.node1 = n_1
        self.node2 = n_2

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self.node1) + str(self.node2))

    def __repr__(self):
        return "Edge({0}, {1})".format(self.node1, self.node2)

    def kind(self):
        return self.node1 + '-' + self.node2


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


    def task2task(task):
        res = set()
        if task['description']:
            if 'depends' in task:

                dependencies = task['depends']
                if type(dependencies) is not list:
                    dependencies = dependencies.split(',')

                for dep in dependencies:
                    
                    if dep in collections.uuids:
                        res.add(Edge(
                            Node('task', collections.task_dict[dep]['description']),
                            Node('task', task['description'])))
        return res


    def task2tags(task):
        res = set()
        if 'tags' in task:
            for tag in task['tags']:
                if task['status'] != 'deleted':
                    res.add(Edge(
                        Node('task', task['description']),
                        Node('tags', tag)))
        return res


    def task2projects(task, excludedTaskStatus):
        res = set()
        if task['description']:
            if 'project' in task.keys():
                if task['project'] in collections.projects:
                    if not task['status'] in excludedTaskStatus:
                        res.add(Edge(
                            Node('task', task['description']),
                            Node('project', task['project'])))
        return res


    def project2projects():
        """
        let's support subprojects.
        """
        res = set()
        
        all_projects = set(collections.projects)
        for p in collections.projects:
            if '.' in p:
                all_projects.add(p.split('.')[0])

        for p1 in all_projects:
            for p2 in all_projects:
                cond = p1 in p2 and p1 != p2
                if cond:
                    res.add(Edge(
                        Node('project', p2),
                        Node('project', p1)))
        return res


    res = set()
    res.update(project2projects())

    for t in collections.tasks:

        res.update(task2task(t))
        res.update(task2tags(t))
        res.update(task2uda(t, 'project'))

        for u in udas:
            res.update(task2uda(t, u))

    return res


def filter_nodes(es, nodes):
    """
    return edges from es that do not contain nodes from 'nodes'.
    """
    res = set()
    for e in es:
        if e.node1.label in nodes:
            continue
        if e.node2.label in nodes:
            continue
        res.add(e)
    return res


def filter_edges(es, edge_types):
    """
    return edges from es that are not of a type in edge_types and do not contain
    any nodes of that type.
    """
    res = set()
    for e in es:
        if e.node1.kind in edge_types:
            continue
        if e.node2.kind in edge_types:
            continue
        if e.node1.kind + '-' + e.node2.kind in edge_types:
            continue
        res.add(e)
    return res


def filter_network(es, nodes, edge_types):
    h = filter_nodes(es, nodes)
    return filter_edges(h, edge_types)


def add_indirect_edges(edges, kind_1, kind_2):
    """
    If a node has a connection to
    """
    res = set()

    for e_1 in edges:
        for e_2 in edges:

            if e_1.node1.kind == kind_1 and e_2.node1.kind == kind_2:
                if e_1.node2 == e_2.node2:
                    res.add(Edge(e_1.node1, e_2.node1))
            if e_1.node1.kind == kind_1 and e_2.node2.kind == kind_2:
                if e_1.node2 == e_2.node1:
                    res.add(Edge(e_1.node1, e_2.node2))
            if e_1.node2.kind == kind_1 and e_2.node1.kind == kind_2:
                if e_1.node1 == e_2.node2:
                    res.add(Edge(e_1.node2, e_2.node1))
            if e_1.node2.kind == kind_1 and e_2.node2.kind == kind_2:
                if e_1.node1 == e_2.node1:
                    res.add(Edge(e_1.node2, e_2.node2))

    return res



################################################################################
##
##  generate dot format from base structure
##
################################################################################



def generate_dot_source(
        connections, node_conf, edge_conf, graph_conf):
    """
    node_conf is a dictionary with keys being a possible type of a node.
    edge_conf is a dictionary with keys being a possible type of an edge.
    The values of the dictionaries are dictionaries with settings.
    edges is a list of Edge instances.
    """

    header = "digraph dependencies {"

    for (key, value) in graph_conf.items():
        header += "{0}=\"{1}\"; ".format(key, value)
    footer = "}"


    def node(n):
        label = '"' + n.label + '"'
        label += '[id="activate(\'{0}\', \'{1}\')"]'.format(n.kind, n.label)
        if n.kind in node_conf:
            label += "".join(["[{0}=\"{1}\"]".format(k, v) for
                (k, v) in node_conf[n.kind].items()])
        else:
            label += "".join(["[{0}=\"{1}\"]".format(k, v) for
                (k, v) in node_conf['default'].items()])
        return label


    def edge(e):
        line = '"{0}" -> "{1}"'.format(
                e.node1.label,
                e.node2.label)
        kind = e.node1.kind + '-' + e.node2.kind
        if kind in edge_conf:
            line += "".join(["[{0}=\"{1}\"]".format(k, v) for
                (k, v) in edge_conf[kind].items()])
        else:
            line += "".join(["[{0}=\"{1}\"]".format(k, v) for
                (k, v) in edge_conf['default'].items()])
        return line

    res = [header]

    # edges
    for e in connections:
        res.append(edge(e))
        res.append(node(e.node1))
        res.append(node(e.node2))

    res.append(footer)
    return "\n".join(res)



################################################################################
##
##  interact with the os environment
##
################################################################################



def json_from_task_process(task_query):
    """
    read input from taskwarrior via stdin,
    return list of dictionaries.
    """
    output = subprocess.check_output(task_query.split(' '))
    tasks = ','.join(str(output, 'utf-8').split('\n')[:-1])
    return json.loads('[' + tasks + "]")


def get_udas_from_task_config():
    """
    read udas from configuration file.
    """
    udas = set()

    if os.environ.get('TASKRC') is None:
        config_file = '{0}/.taskrc'.format(os.environ['HOME'])
    else:
        config_file = os.environ['TASKRC']

    with open(config_file, 'r') as rc:

        lines = [line for line in rc.readlines() if 'uda' == line[:3]]
        for line in lines:
            udas.add(line.split('.')[1])

    return udas


def get_uda_values_from_tasks(tasks, uda):
    res = set()
    for task in tasks:
        if uda in task:
            res.add(task[uda])
    return res


def get_udas_from_task_process():
    udas = get_udas_from_task_config()
    tasks = json_from_task_process('task status:pending export')
    return {u: get_uda_values_from_tasks(tasks, u)
            for u in udas}


def task_with_annotations(task):

    def wrap_text(strng, chars_per_line=25):
        lines = textwrap.wrap(strng, width=chars_per_line)
        return "\\n".join(lines)

    res = wrap_text(task['description'], chars_per_line=25) + '\n'
    if 'annotations' in task:
        for anno in task['annotations']:
            res += anno['entry'] +':\n'
            res += wrap_text(anno['description'], chars_per_line=20) + '\n'
    return res


class TaskwarriorExploit(object):

    def __init__(self, tasks, suppress_annotations=False):
        self.tasks = tasks
        if not suppress_annotations:
            for t in tasks:
                t['description'] = task_with_annotations(t)
        self.projects = self.get_projects()
        self.tags = self.get_tags()
        self.task_dict = self.get_uuids()
        self.uuids = self.task_dict.keys()


    def get_projects(self):
        res = set()
        for task in self.tasks:
            if 'project' in task.keys():
                res.add(task['project'])
        return res

    def get_tags(self):
        """
        data is list of dictionaries, containing data from
        the export function of taskwarrior.
        return a set with the keys.
        """
        allTags = set()
        for task in self.tasks:
            if 'tags' in task.keys():
                for tag in task['tags']:
                    if tag not in allTags:
                        allTags.add(tag)
        return allTags

    def get_uuids(self):
        res = {}
        for task in self.tasks:
            res[task['uuid']] = task
        return res



def read_visual_config():
    """
    read configuration file .task2dotrc.json in the home directory that
    contains configuration for the visual appearence of the resulting graph
    """
    config_file = '{0}/.task2dotrc.json'.format(os.environ['HOME'])
    if os.path.isfile(config_file):
        with open(config_file, 'r') as handle:
            return json.load(handle)
    
    node_styles = [
        {
            'shape': 'egg',
            'fillcolor': '#000000',
            'penwidth': '2pt',
            'style': 'filled',
            'fontcolor': 'white',
            'color': 'white'},
        {
            'shape': 'octagon',
            'style': 'filled',
            'fillcolor': '#dd9900',
            'color': 'white'},
        {
            'shape': 'diamond',
            'penwidth': '2pt',
            'color': '#22ff22',
            'fontcolor': '#ffffff',
            'style': 'filled',
            'fillcolor': '#115500'},
        {
            'shape': 'box',
            'color': 'white',
            'fontcolor': 'white',
            'style': 'rounded,filled',
            'fillcolor': '#222299',
            'fontsize': '16'},
        {
            'shape': 'note',
            'color': 'white',
            'fontcolor': 'white',
            'style': 'filled',
            'fillcolor': '#111155'},
        {
            'shape': 'circle',
            'color': 'white',
            'fontcolor': 'white'}]
    
    edge_styles = [
        {
            'color': 'white'},
        {
            'color': 'white',
            'style': 'dotted',
            'penwidth': '5pt',
            'arrowsize': '0.1'},
        {
            'color': '#22ff22',
            'penwidth': '2pt',
            'arrowhead': 'odot',
            'arrowtail': 'odot'},
        {
            'color': '#aa2211'}]
    
    graph_styles = {
        'layout': 'fdp',
        'splines': 'ortho',
        'size': '30,30',
        'bgcolor': '#111519'
    }
    
    return {
        "nodes": {
            'people': node_styles[1],
            'tags': node_styles[0],
            'outcome': node_styles[0],
            'project': node_styles[2],
            'task': node_styles[3],
            'annotation': node_styles[4],
            'state': node_styles[5],
            'default': node_styles[3]
        },
        "edges": {
            'default': edge_styles[0],
            'task-tags': edge_styles[1],
            'project-project': edge_styles[2],
            'task-project': edge_styles[3]
        },
        "graph": graph_styles
    }




################################################################################
##
##  main program
##
################################################################################



def json_from_task_stdin():
    """
    read input from taskwarrior via stdin,
    return list of dictionaries.
    """
    taskwarrioroutput = ''.join(sys.stdin.readlines())
    return json.loads(taskwarrioroutput)


def exclusion_from_command_line():
    """
    read command line arguments, return exclusion pattern.
    """
    arguments = sys.argv[1:]
    node_exclusion = [h[1:] for h in arguments if h[0] == '-' and h[1] != '-']
    edge_exclusion = [h[2:] for h in arguments if h[0] == '-' and h[1] == '-']
    edge_addition = [h[2:] for h in arguments if h[0] == '+' and h[1] == '+']
    return (node_exclusion, edge_exclusion, edge_addition)



def main():
    
    (nodes_to_be_excluded, edges_to_be_excluded, edge_addition) = exclusion_from_command_line()

    tasks = json_from_task_stdin()
    task_data = TaskwarriorExploit(tasks, 'annotation' in edges_to_be_excluded)
    edge_data = connector(task_data, get_udas_from_task_config())
    
    more_edges = set()
    for e_a in edge_addition:
        [kind_1, kind_2] = e_a.split('-')
        more_edges.update(add_indirect_edges(edge_data, kind_1, kind_2))
    
    edge_data = filter_network(
            edge_data, nodes_to_be_excluded, edges_to_be_excluded)
    
    edge_data.update(more_edges)

    visual_config = read_visual_config()
    
    print(
        generate_dot_source(
            edge_data,
            visual_config["nodes"],
            visual_config["edges"],
            visual_config["graph"]))

if __name__ == "__main__":
    main()
