from __future__ import annotations

import logging
from typing import Dict, Union, List
from collections import OrderedDict
import metrics

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
            else:
                succeeded = self.model.persist(documents)
            # succeeded += 1
        except Exception as e:
            logger.debug("Failed saving document to %s", self.model)
            failed.append(e)

        if len(failed) > 0:
            logger.error(
                "Failed saving %s documents to %s -- %s",
                len(failed),
                self.model,
                failed,
                extra={"faiure_messages": failed},
            )
        return succeeded
        # metrics.post(f"persistance.failed.{self.model_name}", len(failed))
        # metrics.post(f"persistance.success.{self.model_name}", succeeded)


if __name__ == "__main__":
    # pylint: disable-all

    from ihs import create_app

    from config import get_active_config
    from collector import XMLParser, Endpoint
    from collector.tasks import run_endpoint_task, get_job_results, submit_job, collect
    from util import to_json
    from time import sleep
    from collector.transformer import WellboreTransformer
    from api.models import WellHorizontal

    app = create_app()
    app.app_context().push()

    logging.basicConfig(level=20)

    conf = get_active_config()
    endpoints = Endpoint.load_from_config(conf)

    endpoint_name = "well_master_horizontal"
    task_name = "sync"
    job_config = [
        x for x in run_endpoint_task(endpoint_name, task_name) if x is not None
    ][0]

    job = submit_job(**job_config)
    xml = get_job_results(job)

    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml)
    new = WellboreTransformer.extract_from_collection(document)
    new = new[0]
    existing = WellHorizontal.objects.get(api14="42461409160000")

    new["date_creation"] = existing.date_creation
    new["date_creation"]

    existing.md5 == WellboreTransformer.add_document_hash(new)["md5"]

    import json

    to_json(json.loads(existing.to_json()), "test/data/existing_example.json")
    to_json(new, "test/data/incomming_example.json")

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

