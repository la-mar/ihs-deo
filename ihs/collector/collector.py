from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Dict, List, Union

import metrics
from util import query_dict

logger = logging.getLogger(__name__)


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    def __init__(self, model):
        self.model = model
        self.model_name = model.__name__

    def save(self, documents: List[OrderedDict], replace: bool = True):
        succeeded = 0
        failed = []
        if not isinstance(documents, list):
            documents = [documents]  # type: ignore

        try:
            if replace:
                succeeded = self.model.replace(documents)
                logger.debug(f"({self.model_name}) replaced {succeeded} documents")
            else:
                succeeded = self.model.persist(documents)
                logger.debug(f"({self.model_name}) updated {succeeded} documents")
            # succeeded += 1
        except Exception as e:
            logger.debug("Failed saving document to %s", self.model)
            failed.append(e)

        if len(failed) > 0:
            meta_keys = ["identification", "api14", "api10", "ihs_last_update_date"]
            failed_meta = [
                {k: v for k, v in doc.items() if k in meta_keys} for doc in documents
            ]
            logger.error(
                f"Failed saving {len(failed)} documents to {self.model.__name__} -- {failed}",
                extra={"error.messages": failed, "error.meta": failed_meta},
            )
        return succeeded


if __name__ == "__main__":
    # pylint: disable-all

    from ihs import create_app

    from config import get_active_config
    from api.models import WellHorizontal, WellVertical

    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    conf = get_active_config()

    collector = Collector(WellVertical)

    # collector.save([{"identification": "123", "api14": "456"}], replace=True)

    # import loggers
    # loggers.config(formatter='json')
    # collector.save(
    #     [
    #         {"identification": "789", "api14": "457"},
    #         {"identification": "789", "api14": "456"},
    #         {"identification": "789", "api14": "456"},
    #         {"identification": "789", "api14": "456"},
    #     ],
    #     replace=True,
    # )
