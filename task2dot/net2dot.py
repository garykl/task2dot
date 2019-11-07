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
import textwrap

import edges as edges


def generate_dot_source(
        connections, node_conf, edge_conf, graph_conf):
    """
    node_conf is a disctionary with keys being a possible type of a node.
    edge_conf is a dictionary with keys being a possible type of an edge.
    The values of the dictionaries are dictionaries with settings.
    edges is a list of Edge instances.
    """

    header = "digraph  dependencies {"

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
