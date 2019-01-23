from persistance.crud_repository import CrudRepository
from typing import *

T = TypeVar('T')


class WithDataBase(Generic[T]):
    Response = Tuple[str, int]

    def __init__(self, serializer: Callable[[T], str], deserializer: Callable[[str], T]):
        self.db = CrudRepository(serializer, deserializer)
