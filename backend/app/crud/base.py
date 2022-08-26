from typing import Generic, TypeVar
from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDBase(Generic[ModelType]):

    def __init__(self, schema: ModelType):
        self.schema = schema
