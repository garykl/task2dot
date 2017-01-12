class Config:

    class NodeConfig:
        def __init__(self):
            self.tasks = True
            self.tags = True
            self.projects = True
            self.annotations = True

    class EdgeConfig:
        def __init__(self):
            self.tagVStags = False
            self.projectVStags = False

    ## fine tune node existence and connection creation
    class ExclusionConfig:
        def __init__(self):
            self.tags = [] # those nodes are supressed
            self.projects = []
            self.taskStatus = ['deleted'] # nodes removed
            self.taggedTaskStatus = set(['deleted']) # connection between tags and those are supressed
            self.annotationStatus = ['deleted']

    def __init__(self):
        self.nodes = self.NodeConfig()
        self.edges = self.EdgeConfig()
        self.excluded = self.ExclusionConfig()
        self.tagHierarchy = {}
