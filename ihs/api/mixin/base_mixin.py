""" Basic mixin for MongoEngine backed data models """

from typing import Dict, List, Union, no_type_check

import mongoengine as me

from util.deco import classproperty


class BaseMixin:
    @classproperty
    @no_type_check
    def primary_keys(self) -> List[str]:
        return [name for name, column in self._fields.items() if column.primary_key]

    def primary_key_values(self) -> List[Dict]:
        pks = self.primary_keys
        data = [m for m in self.objects.only(*pks)]  # type: ignore
        unpacked = []
        for d in data:
            limited = {}
            for pk in pks:
                limited[pk] = d[pk]
            unpacked.append(limited)
        return unpacked

    @classmethod
    @no_type_check
    def get(cls, **kwargs) -> Union[List, None]:
        """ Wraps cls.objects(), returning None if no matching objects
            are found and otherwise always returning a collection """

        try:
            # pylint: disable=no-member
            return cls.objects(**kwargs)
        except me.errors.DoesNotExist:
            return None
