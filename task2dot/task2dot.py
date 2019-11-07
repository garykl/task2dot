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
import os
import json

import task_lib
import edges
import net2dot


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

    tasks = json_from_task_stdin()
    
    task_data = task_lib.TaskwarriorExploit(tasks)
    
    (nodes_to_be_excluded, edges_to_be_excluded, edge_addition) = exclusion_from_command_line()
    edge_data = edges.connector(task_data, task_lib.get_udas_from_task_config())
    
    more_edges = set()
    for e_a in edge_addition:
        [kind_1, kind_2] = e_a.split('-')
        more_edges.update(edges.add_indirect_edges(edge_data, kind_1, kind_2))
    
    edge_data = edges.filter_network(
            edge_data, nodes_to_be_excluded, edges_to_be_excluded)
    
    edge_data.update(more_edges)


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
            'bgcolor': '#111519'}
    
    print(net2dot.generate_dot_source(edge_data,
        {
            'people': node_styles[1],
            'tags': node_styles[0],
            'outcome': node_styles[0],
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


if __name__ == "__main__":
    main()