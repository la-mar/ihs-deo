from __future__ import annotations

import logging
from typing import Dict, Union, List
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    def __init__(self, model):
        self.model = model

    def save(self, documents: List[OrderedDict]):
        succeeded = 0
        failed = []
        if not isinstance(documents, list):
            documents = [documents]  # type: ignore
        for doc in documents:
            try:
                self.model(**doc).save()
                succeeded += 1
            except Exception as e:
                logger.debug("Failed saving document to %s", self.model)
                failed.append(e)

        if len(failed) > 0:
            logger.error(
                "Failed saving %s documents to %s -- %s",
                len(failed),
                self.model,
                failed,
            )
        logger.info("Saved %s documents to %s", succeeded, self.model)


if __name__ == "__main__":
    # pylint: disable-all

    from ihs import create_app
    from api.models import WellHorizontal
    from collector import (
        XMLParser,
        Endpoint,
        ExportParameter,
        ExportBuilder,
        ExportJob,
        ExportParameter,
        ExportRetriever,
        WellboreTransformer,
        ProductionTransformer,
    )
    from config import get_active_config
    from util import to_json
    from time import sleep
    from collector.identity_list import ProductionList

    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    url = conf.API_BASE_URL
    endpoints = Endpoint.load_from_config(conf)

    endpoint = endpoints["production_master_horizontal"]
    task = endpoint.tasks["sync"]

    #! Dont delete
    # import pandas as pd

    # dir(pd.io.json)

    # prod_json = document["production_set"]["producing_entity"][0]["production"]["year"]

    # df = pd.io.json.json_normalize(
    #     prod_json,
    #     record_path=["month"],
    #     record_prefix="month.",
    #     meta=["number"],
    #     meta_prefix="year.",
    #     # errors="ignore",
    # )

    # df.iloc[10].T

