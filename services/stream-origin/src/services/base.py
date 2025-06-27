from src.interfaces.storage import AbstractStorage


class BaseService:
    def __init__(self, storage: AbstractStorage):
        self.storage = storage
