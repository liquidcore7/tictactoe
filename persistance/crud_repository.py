import redis
from uuid import uuid1
from typing import *
import json

import os
import urllib.parse

T = TypeVar('T')


class CrudRepository(Generic[T]):
    def __init__(self,
                 serialize: Callable[[T], str] = lambda t: json.dumps(t),
                 deserialize: Callable[[str], T] = lambda s: json.loads(s, cls=T),
                 timeout=60 * 60 * 2):
        self.db_connection = CrudRepository.__env_init__()
        self.serde = (serialize, deserialize)
        self.timeout = timeout

    @staticmethod
    def __env_init__() -> redis.Redis:
        urllib.parse.uses_netloc.append('redis')
        try:  # Heroku init from redis url
            redis_url = os.environ['REDIS_URL']
            url = urllib.parse.urlparse(redis_url)
        except:  # no env variable or it`s malformed
            url = urllib.parse.urlparse('redis://localhost:6379')  # REDIS defaults
        return redis.Redis(host=url.hostname, port=url.port, password=url.password)

    def get(self, uuid: str) -> Optional[T]:
        maybe_result = self.db_connection.get(uuid)
        if maybe_result is not None:
            maybe_result = self.serde[1](maybe_result)
        return maybe_result

    def create(self, empty_instance: T) -> Tuple[bool, str]:
        inserted_id = str(uuid1())
        status = self.db_connection.set(inserted_id, self.serde[0](empty_instance))
        status &= self.db_connection.expire(inserted_id, self.timeout)
        return status, inserted_id

    def update(self, uuid: str, new_instance: T, last_update: bool=False) -> Tuple[bool, T]:
        status = True
        if last_update:
            status &= self.delete(uuid)
        else:
            status &= self.db_connection.set(uuid, self.serde[0](new_instance))
        return status, new_instance

    def delete(self, uuid: str) -> bool:
        return self.db_connection.delete(uuid)
