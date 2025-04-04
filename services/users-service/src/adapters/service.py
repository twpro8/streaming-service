from src.adapters.content import ContentAdapter


class ServiceAdapter:
    def __init__(self, content_service_url: str):
        self.content = ContentAdapter(content_service_url)
