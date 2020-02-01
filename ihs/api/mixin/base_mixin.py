""" Basic mixin for MongoEngine backed data models """

from typing import Dict, List, Union, no_type_check
import logging

import mongoengine as me

from util.deco import classproperty

logger = logging.getLogger(__name__)


class BaseMixin:
    # @classproperty
    # @no_type_check
    # def primary_keys(self) -> List[str]:
    #     return [name for name, column in self._fields.items() if column.primary_key]

    # def primary_key_values(self) -> List[Dict]:
    #     pks = self.primary_keys
    #     data = [m for m in self.objects.only(*pks)]  # type: ignore
    #     unpacked = []
    #     for d in data:
    #         limited = {}
    #         for pk in pks:
    #             limited[pk] = d[pk]
    #         unpacked.append(limited)
    #     return unpacked

    # @classmethod
    # @no_type_check
    # def get(cls, **kwargs) -> Union[List, None]:
    #     """ Wraps cls.objects(), returning None if no matching objects
    #         are found and otherwise always returning a collection """

    #     try:
    #         # pylint: disable=no-member
    #         if kwargs.pop("paginate", False):
    #             return cls.objects.paginate(**kwargs)
    #         logger.debug(f"{kwargs}")
    #         return cls.objects(**kwargs)
    #     except me.errors.DoesNotExist:
    #         return None

    # #! TODO: override save() and check for document hash
    # #! if hash exists => discard
    # #! else:
    # #! replace existing record
    # #! post message to SNS

    @classproperty
    def primary_key_names(self) -> List[str]:
        """ Get a list of the model's fields marked as primary keys """
        return [name for name, column in self._fields.items() if column.primary_key]

    @classproperty
    def primary_key_values(self) -> List[Dict]:
        """ Get a list containing all primary keys in the current collection """
        pks = self.primary_key_names
        unpacked = []
        if len(pks) > 0:
            data = [m for m in self.objects.only(*pks)]  # type: ignore
            for d in data:
                limited = {}
                for pk in pks:
                    limited[pk] = d[pk]
                unpacked.append(limited)

        return unpacked

    @classproperty
    def pks(self) -> List[Dict]:
        """ Alias for `primary_key_values` Get a list containing all primary
        keys in the current collection. """
        return self.primary_key_values

    @classmethod
    def get(cls, **kwargs) -> Union[List, None]:
        """ Wraps cls.objects(), returning None if no matching objects are found and
        otherwise always returning a collection """
        logger.debug(f"kwargs={kwargs}")

        try:
            if kwargs.pop("paginate", False):
                result = cls.objects.paginate(**kwargs)
                logger.error(f"Paginated Result: result={result}")
            else:
                result = cls.objects(**kwargs)

            return result
        except me.errors.DoesNotExist:
            return None

    @classmethod
    def persist(cls, documents: Union[Dict, List[Dict]]) -> int:
        """Add or update one or more documents"""
        succeeded = 0
        failed = []

        if not isinstance(documents, list):
            documents = [documents]  # type: ignore

        for doc in documents:
            try:
                cls.objects(**cls.get_pks_from_doc(doc)).upsert_one(**doc)
                succeeded += 1
            except Exception as e:
                logger.debug("Failed saving document to %s", cls)
                failed.append(e)

        if len(failed) > 0:
            logger.error(
                "Failed saving %s documents to %s -- %s",
                len(failed),
                cls,
                failed,
                extra={"faiure_messages": failed},
            )
        return succeeded

    @classmethod
    def get_one(cls, document: Dict):
        return cls.objects(**cls.get_pks_from_doc(document)).first()

    @classmethod
    def get_pks_from_doc(cls, doc):
        pks = {}
        for pk in cls.primary_key_names:
            pks[pk] = doc.get(pk)

        return pks

    @classmethod
    def delete_many(cls, documents: Union[Dict, List[Dict]]) -> int:
        """Delete one or more documents by id. Documents without an id are ignore."""
        if not isinstance(documents, list):
            documents = [documents]  # type: ignore

        affected = 0
        for doc in documents:
            obj = cls.objects(**cls.get_pks_from_doc(doc)).first()
            if obj:
                obj.delete()
                affected += 1
        return affected

    @classmethod
    def replace(cls, documents: List[Dict]):
        """Atomically replace an existing document, or add it if it doesn't exist """
        if not isinstance(documents, list):
            documents = [documents]  # type: ignore

        ct = 0
        for doc in documents:
            pks = cls.get_pks_from_doc(doc)
            cls.objects(**pks).delete()
            cls(**doc).save()
            ct += 1

        return ct

