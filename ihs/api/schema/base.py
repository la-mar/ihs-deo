import logging

from marshmallow import Schema, ValidationError, post_dump

logger = logging.getLogger(__name__)


class BaseSchema(Schema):
    def dump(self, *args, **kwargs):
        try:
            return super().dump(*args, **kwargs)
        except ValidationError as e:
            return e.valid_data
        except ValueError as ve:
            logger.error(f"{ve} args={args}, kwargs={kwargs}")
            raise ve

    @post_dump
    def nan_to_none(self, data, *args, **kwargs):
        return {
            key: None if value == float("inf") else value for key, value in data.items()
        }
