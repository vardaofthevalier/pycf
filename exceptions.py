class CloudFoundryError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class CloudFoundryModuleError(CloudFoundryError):
    def __init__(self, msg):
        super(CloudFoundryModuleError, self).__init__(msg)