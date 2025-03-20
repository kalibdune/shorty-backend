from datetime import datetime
from unittest import mock

import pytest

from shorty.db.schemas.url import UrlCreateSchema
from shorty.services.url import UrlService
from shorty.tests.unittests.factories import UrlFactory
from shorty.utils.exceptions import InsufficientStorage


@pytest.fixture
def create_all_hashs():
    print("generate all entities")
    for _ in range(26):
        UrlFactory(hash_len=1)
    print("ended generation")


class TestUrlService:

    def test_generate_random_hash(self, get_session):
        url_service = UrlService(get_session)
        short = url_service._generate_random_hash(2)
        assert len(short) == 2
        assert short.upper() == short

    @pytest.mark.parametrize(
        "data",
        [
            UrlCreateSchema(url="https://lol.com/", expiration_time=90),
            UrlCreateSchema(url="https://lolsdfsdfsd.com/", expiration_time=0),
        ],
    )
    async def test_create_url(self, get_session, data: UrlCreateSchema):
        url_service = UrlService(get_session)
        time = datetime.now()
        res = await url_service.create_url(data)
        res_db = await url_service.get_url_by_id(res.id)

        assert data.url == res_db.url
        assert time <= res_db.expired_at

    @pytest.mark.parametrize(
        "data", [UrlCreateSchema(url="https://someurl.ru/", expiration_time=90)]
    )
    async def test_create_url_overloaded(self, get_session, create_all_hashs, data):
        url_service = UrlService(get_session)

        with mock.patch.object(
            url_service, "_generate_random_hash"
        ) as mock_generate_random_hash:
            mock_generate_random_hash.return_value = "A"
            with pytest.raises(InsufficientStorage):
                await url_service.create_url(data)
