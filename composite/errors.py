"""ERRORS"""


class Error(Exception):
    """Main Error Class"""

    def __init__(self, message):
        self.message = message

    @property
    def serialize(self):
        return {
            'message': self.message
        }

class CompositeError(Error):
    pass

class GeostoreNotFound(Error):
    pass