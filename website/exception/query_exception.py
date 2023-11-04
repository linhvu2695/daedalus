class MissingClauseException(Exception):
    def __init__(self, message="Query missing required clauses."):
        self.message = message
        super().__init__(self.message)