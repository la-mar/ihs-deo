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

    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    url = conf.API_BASE_URL
    endpoints = Endpoint.load_from_config(conf)

    # # ? well example
    endpoint = endpoints["well_horizontal"]
    task = endpoint.tasks["sequoia"]
    requestor = ExportBuilder(url, endpoint, functions={})
    ep = ExportParameter(**list(task.options)[0])

    #
    jid = requestor.submit(ep)

    retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)

    xml = retr.get()
    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml, parse_dtypes=False)
    wellbores = WellboreTransformer.extract_from_well_set(document)
    to_json(wellbores, "test/data/wellbore_example.json")
    print(f"Parsed {len(wellbores)} wellbores")
    c = Collector(endpoint)

    for wb in wellbores:
        Well(**wb).save()

    # ? production example
    # endpoint = endpoints["production"]
    # c = Collector(endpoint)
    # requestor = ExportBuilder(url, endpoint, functions={})
    # task = endpoint.tasks["driftwood"]
    # ep = ExportParameter(**task.options)
    # jid = requestor.submit(ep)

    # retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)

    # sleep(5)
    # xml = retr.get()
    # parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    # document = parser.parse(xml, parse_dtypes=False)
    # to_json(document, "test/data/production_unparsed.json")
    # document = parser.parse(xml, parse_dtypes=True)
    # to_json(document, "test/data/production_parsed.json")
    # production = ProductionTransformer.extract_from_wellset(document)
    # print(f"Parsed {len(production)} production records")

    # for wb in production:
    #     Production(**wb).save()

    # ep.template = "EnerdeqML 1.0 Well"
    # jid = requestor.submit(ep)
    # retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)
    # sleep(5)
    # xml = retr.get()
    # parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    # document = parser.parse(xml, parse_dtypes=True)
    # to_json(document, "test/data/wellML.json")

    # ep.template = "EnerdeqML 1.0 Production"
    # jid = requestor.submit(ep)
    # retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)
    # sleep(5)
    # xml = retr.get()
    # parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    # document = parser.parse(xml, parse_dtypes=True)
    # to_json(document, "test/data/wellML.json")

    ep = ExportParameter(
        **{
            "data_type": "Well",
            "template": "Well ID List",
            "query_path": "config/queries/well_upton_all.xml",
        }
    )
    ep.template = "Well ID List"
    jid = requestor.submit(ep)
    retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)
    sleep(5)
    ids = retr.get()

    # to_json(document, "test/data/well_id_list_permian.json")

    import pandas as pd

    dir(pd.io.json)

    prod_json = document["production_set"]["producing_entity"][0]["production"]["year"]

    df = pd.io.json.json_normalize(
        prod_json,
        record_path=["month"],
        record_prefix="month.",
        meta=["number"],
        meta_prefix="year.",
        # errors="ignore",
    )

    df.iloc[10].T

