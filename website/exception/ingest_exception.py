class IngestInvalidTypeException(Exception):
    def __init__(self, message="Ingest invalid filetype."):
        self.message = message
        super().__init__(self.message)