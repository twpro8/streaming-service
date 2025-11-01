from pydantic import BaseModel, ConfigDict, model_validator

from src.exceptions import FieldRequiredException


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    @property
    def picture_str(self):
        return str(self.picture_url)

    @property
    def normalized_email(self) -> str:
        return str(self.email).strip().lower()


class AtLeastOneFieldMixin(BaseModel):
    @model_validator(mode="after")
    def check_some_field(self):
        if not self.model_fields_set:
            raise FieldRequiredException
        return self
