class NotFoundEntityException(Exception):
    def __init__(self, msg: str = "Entity not found"):
        super().__init__(msg)
        self.msg = msg


class ConflictEntityException(Exception):
    def __init__(self, msg: str = "Entity already exists"):
        super().__init__(msg)
        self.msg = msg


class BadRequestException(Exception):
    pass
