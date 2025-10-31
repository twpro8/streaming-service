from pydantic import BaseModel, ConfigDict, model_validator

from src.exceptions import FieldRequiredException


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AtLeastOneFieldMixin(BaseModel):
    @model_validator(mode="after")
    def check_some_field(self):
        if not self.model_fields_set:
            raise FieldRequiredException
        return self
