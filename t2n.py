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
#    - All arument with a leading '--' lead to the exclusion of that node type
#
################################################################################
import sys
import json

import taskwarrior2net.validate as validate
import taskwarrior2net.edges as edges
import taskwarrior2net.net2dot as net2dot


def taskwarrior_json():
    """
    read input from taskwarrior via stdin,
    return list of dictionaries.
    """
    taskwarrioroutput = ','.join(sys.stdin.readlines())
    return json.loads('[' + taskwarrioroutput + "]")


def exclusion_from_input():
    """
    read command line arguments, return exclusion pattern.
    """
    arguments = sys.argv[1:]
    node_exclusion = [h[1:] for h in arguments if h[0] == '-' and h[1] != '-']
    edge_exclusion = [h[2:] for h in arguments if h[0] == '-' and h[1] == '-']
    return (node_exclusion, edge_exclusion)


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


tasks = taskwarrior_json()

task_data = validate.TaskwarriorExploit(tasks)

(n, et) = exclusion_from_input()
edge_data = filter_network(
        edges.connector(task_data, ['people']),
        n, et)


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
            'penwidth': '8pt',
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
        'bgcolor': '#111519'}

print(net2dot.generate_dot_source(edge_data,
    {
        'people': node_styles[1],
        'tags': node_styles[0],
        'project': node_styles[2],
        'task': node_styles[3],
        'annotation': node_styles[4],
        'state': node_styles[5],
        'default': node_styles[3]},
    {
        'default': edge_styles[0],
        'task-tags': edge_styles[1],
        'project-project': edge_styles[2],
        'task-project': edge_styles[3]}, graph_styles))
#     {
#         'tag': {},
#         'task': {},
#         'project': {},
#         'annotation': {},
#         'state': {},
#         'path': {},
#         'people': {}},
#     {
#         'task2tag': {},
#         'task2project': {},
#         'task2annotation': {},
#         'task2state': {},
#         'task2path': {},
#         'task2people': {},
#         'project2project': {},
#         'project2tag': {},
#         'tag2tag': {},
#         'task2task': {}}))
