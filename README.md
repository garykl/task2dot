# task2dot

This program helps with the creation of visualizations of todo
lists. It works as a simple filter between [taskwarrior](https://github.com/GothenburgBitFactory/taskwarrior) and [graphviz](http://www.graphviz.org/).

The code is now on https://pypi.org and can be installed via

    python3 -m pip install task2dot

if you prefer to work with installed software, compared to interpreted source code.
Otherwise execution is performed via python3 task2dot/task2dot.py.

# usage

At the command line write

    task export | task2dot | dot -Tsvg > test.svg

With this, all todo items that you have ever created are fed into
`task2dot`. Without any arguments, it just translates the export
into a format that is suitable for `graphviz` whose output is saved
in the file `test.svg`. We can expect this to result in an insanely
messy network graphics.

For clarity, I will not show the dot command and the output
redirection into a file in any the following code snippets. Note
that those have to be added for obtaining useful visualizations.

When exporting data from `taskwarrior` one has to explicitely state
that one only wants to export pending tasks:

    task status:pendung export | task2dot

See a working example:
![example graph from taskwarrior list](example.png)

## what are the nodes and edges

Tasks, tags and projects are nodes as well as user defined attributes!
User defined attributes are supported if the task configuration file is
`~/.taskrc` or can be found in the environment variable `$TASKRC`.

Edges are task dependencies and all connections from tasks to their project,
all of their tags as well as the values of their user defined attributes.

Note that if all node with all of its connections are shown in a graph with
a sufficiently many tasks, the resulting graph will become overwhelmingly messy.
Therefore, the following exclusion mechanisms are available.

## node and edge exclusion

### node exclusion

To exclude a specific node write

    task status:pending export | task2dot -node

Then there will be no node with the content 'node' in the output
graph.

So why is this useful? If you try to implement *Kanban* or something
similar you are very likely to have a certain tag or a user
defined attribute, like `todo` far too often for having it in a
graph visualization. Almost all tasks would be connected to it via
edges, which is useless. Also, if you export taskwarrior data,
which is filtered with a specific `tag` will cause the resulting
graph having a lot of connections to that tag. So the following
visualization would be useful:

    task status:pending +work | task2dot -work

### node type and edge exclusion

A specific type of node can be excluded by using two hyphens. For
example, not showing any project nodes looks like this:

    task status:pendung export | task2dot --project

Or not showing any tags:

    task status:pendung export | task2dot --tags

In my workflow, paths and emails ids are attached to tasks, so I
need to write

    task export | task2dot --path --email

It is also possible to exclude certain connections also by using
double hyphen. Let's get rid of all connections from tasks to
tags:

    task export | task2dot --task-tags

## more connections: overnext neighbors

It is possible to add additional edges than what taskwarrior
exports directly. One could for example add edges between projects
and tags because they are connected by tasks that have both. If one
then removes the tasks one can look at a graph that shows us which
'actions' are needed for certain projects, if the tags represent
'actions'. Similarly to edge exclusion, we use ++node1-node2 to add
additional edges.

    task export | task2dot ++tags-project --task

# colorscheme configuration

To adjust the colors to your needs, you will need to provide a file
`~/.task2dotrc.json` in your home directory. It contains a json string
with the following format:

``` json
{
    "nodes": {
        "tags": {
            "shape": "egg",
            "fillcolor": "#000000",
            "penwidth": "2pt",
            "style": "filled",
            "fontcolor": "white",
            "color": "white"
        },
        "outcome": {
            "shape": "egg",
            "fillcolor": "#000000",
            "penwidth": "2pt",
            "style": "filled",
            "fontcolor": "white",
            "color": "white"
        },
        "people": {
            "shape": "octagon",
            "style": "filled",
            "fillcolor": "#dd9900",
            "color": "white"
        },
        "project": {
            "shape": "diamond",
            "penwidth": "2pt",
            "color": "#22ff22",
            "fontcolor": "#ffffff",
            "style": "filled",
            "fillcolor": "#115500"
        },
        "task": {
            "shape": "box",
            "color": "white",
            "fontcolor": "white",
            "style": "rounded,filled",
            "fillcolor": "#222299",
            "fontsize": "16"
        },
        "default": {
            "shape": "box",
            "color": "white",
            "fontcolor": "white",
            "style": "rounded,filled",
            "fillcolor": "#222299",
            "fontsize": "16"
        },
        "annotation": {
            "shape": "note",
            "color": "white",
            "fontcolor": "white",
            "style": "filled",
            "fillcolor": "#111155"
        },
        "state": {
            "shape": "circle",
            "color": "white",
            "fontcolor": "white"
        }
    },
    "edges": {
        "default": {
            "color": "white"
        },
        "task-tags": {
            "color": "white",
            "style": "dotted",
            "penwidth": "5pt",
            "arrowsize": "0.1"
        },
        "project-project": {
            "color": "#22ff22",
            "penwidth": "2pt",
            "arrowhead": "odot",
            "arrowtail": "odot"
        },
        "task-project": {
            "color": "#aa2211"
        }
    },
    "graph": {
        "layout": "fdp",
        "splines": "ortho",
        "size": "30,30",
        "bgcolor": "#111519"        
    }
}
```

The parameters that are set in the configuration directly correspond to the
graphviz (see [graphviz](http://www.graphviz.org/)) settings available for nodes, edges and the graph as a whole. The
example configuration shown here corresponds to the color scheme used for
the example graphics referred to from within this README file.

If you want to provide color settings for your own user defined attribute, just
add a property to the `nodes` property with the name of your attribute and supply the parameters that shall deviate from the `default` configuration.