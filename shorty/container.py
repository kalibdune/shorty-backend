from shorty.config import config
from shorty.db.session import SessionManager
from shorty.repositories.url import UrlRepository
from shorty.services.url import UrlService


class Container:
    db = SessionManager(config.postgres.get_dsn)

    @classmethod
    def get_url_repository(cls) -> UrlRepository:
        return UrlRepository(cls.db.session)

    @classmethod
    def get_url_service(cls) -> UrlService:
        return UrlService(cls.get_url_repository())
