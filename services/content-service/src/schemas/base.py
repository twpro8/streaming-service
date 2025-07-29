from pydantic import BaseModel, ConfigDict, model_validator

from src.exceptions import AtLeastOneFieldRequiredException


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AtLeastOneFieldRequired:
    @model_validator(mode="after")
    def check_some_field(self):
        if not any(getattr(self, field) is not None for field in self.__annotations__):
            raise AtLeastOneFieldRequiredException
        return self
