import os
import subprocess
import textwrap
import json



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

    def __init__(self, tasks):
        self.tasks = tasks
        for t in tasks:
            t['description'] = task_with_annotations(t)
        self.projects = self.projects()
        self.tags = self.tags()
        self.task_dict = self.uuids()
        self.uuids = self.task_dict.keys()


    def projects(self):
        res = set()
        for task in self.tasks:
            if 'project' in task.keys():
                res.add(task['project'])
        return res

    def tags(self):
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

    def uuids(self):
        res = {}
        for task in self.tasks:
            res[task['uuid']] = task
        return res


if __name__ == '__main__':

    print(get_udas_from_task_process())

