from src.repositories.files import FilesRepository


class BaseService:
    def __init__(self, files_repo: FilesRepository):
        self.files = files_repo
