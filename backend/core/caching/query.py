from sqlalchemy import orm

from core.db_caching.strategies import InMemoryCacheStrategy


class CachingQuery(orm.Query):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.caching_strategy = InMemoryCacheStrategy()

    def __iter__(self):
        return self.caching_strategy.exec(super())