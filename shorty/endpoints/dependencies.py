from shorty.db.session import session_manager


async def get_session():
    async with session_manager.session() as session:
        yield session
