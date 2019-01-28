from persistance.crud_repository import CrudRepository
from typing import *
import json

T = TypeVar('T')


class WithDataBase(Generic[T]):
    Response = Tuple[str, int]

    def __init__(self,
                 serializer: Callable[[T], str]=json.dumps,
                 deserializer: Callable[[str], T]=json.loads):
        self.db = CrudRepository(serializer, deserializer)
