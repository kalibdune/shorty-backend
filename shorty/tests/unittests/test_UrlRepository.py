from datetime import datetime, timedelta
from uuid import UUID

import pytest

from shorty.db.models.url import Url
from shorty.repositories.url import UrlRepository


class TestUrlRepository:

    @pytest.mark.parametrize(
        "data",
        [
            {
                "url": "https://ya.ru/",
                "hash": "FFFFF",
                "expired_at": datetime.now() + timedelta(days=1),
            }
        ],
    )
    async def test_create_url(self, get_session, data: dict):
        repo = UrlRepository(get_session)
        res: Url = await repo.create(data)
        res = await repo.get_by_id(res.id)
        assert isinstance(res, Url)
        assert res.url == data["url"]
        assert res.hash == data["hash"]
        assert res.expired_at == data["expired_at"]
        assert isinstance(res.id, UUID)
        assert res.created_at <= datetime.now()
        assert res.updated_at <= datetime.now()
