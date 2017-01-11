def excludeElementsFrom(toExclude, ll):
    """
    toExclude and ll are lists of elements.
    return a new list, containing all elements of ll,
    which are not in toExclude.
    """
    res = []
    for l in ll:
        if not l in toExclude:
            res.append(l)
    return res

def isTimed(task):
    """
    return time for task that is timed via task id start/stop.
    time is zero when it is not stopped.
    """
    def timeFromStamps(start, stop):
        if start[:8] != stop[:8]:
            return 0
        else:
            return int(stop[9:15]) - int(start[9:15])

    starts = []
    stops = []
    time = 0
    if 'annotations' in task:
        for a in task['annotations']:
            if 'Started task' in a['description']:
                starts.append(a['entry'])
            if 'Stopped task' in a['description']:
                stops.append(a['entry'])
    for (start, stop) in zip(starts, stops):
        time += timeFromStamps(start, stop)


class Annotation(object):
    def __init__(self, entry, description):
        self.entry = entry
        self.description = description


class TaskwarriorExploit(object):

    def __init__(self, tasks, excluded):
        self.tasks = tasks
        self.projects = excludeElementsFrom(excluded.projects, self.projects())
        self.tags = excludeElementsFrom(excluded.tags, self.tags())
        self.annotations = self.annotations(excluded.annotationStatus)
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
            res[task['uuid']] = task['description']
        return res

    def annotations(self, excludedAnnotationStatus):
        res = []
        for task in self.tasks:
            if 'annotations' in task and task['status'] not in excludedAnnotationStatus:
                for a in task['annotations']:
                    if 'Started task' in a['description']:
                        continue
                    if 'Stopped task' in a['description']:
                        continue
                    res.append(Annotation(a['entry'], a['description']))
        return res
