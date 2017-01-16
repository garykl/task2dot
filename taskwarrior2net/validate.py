import textwrap


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
