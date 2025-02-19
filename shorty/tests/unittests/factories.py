import factory
from faker import Faker

from shorty.config import config
from shorty.db.models.url import Url
from shorty.db.session import SessionManager

session_manager = SessionManager(
    config.postgres.get_dsn_psycopg, config.postgres.debug, is_async=False
)
factory.Faker.override_default_locale("ru_RU")
fake = Faker()


class UrlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Url
        sqlalchemy_session = session_manager._session_factory()
        sqlalchemy_session_persistence = "commit"

    class Params:
        random_hash = False
        hash_len = 1

    url = factory.Faker("uri")
    expired_at = factory.Faker(
        "date_time_between", start_date="now", end_date="+10000s"
    )

    @factory.lazy_attribute
    def hash(self):
        if self.random_hash:
            return fake.bothify(
                text="?" * self.hash_len, letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )
        else:
            seq = UrlFactory._meta._counter.seq
            return "".join(
                chr(65 + (seq // (26**i) % 26))
                for i in range(self.hash_len - 1, -1, -1)
            )
