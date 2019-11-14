from __future__ import annotations

import logging
from typing import Dict, Union, List
from collections import OrderedDict

from collector.endpoint import Endpoint

logger = logging.getLogger(__name__)


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    def __init__(self, model):
        self.model = model

    def save(self, documents: List[OrderedDict]):
        succeeded = 0
        failed = []
        for doc in documents:
            try:
                self.model(**doc).save()
                succeeded += 1
            except Exception as e:
                failed.append(e)

        if len(failed) > 0:
            logger.error("Failed saving %s documents to %s", len(failed), self.model)
        logger.info("Saved %s documents to %s", succeeded, self.model)


if __name__ == "__main__":
    from ihs import create_app
    from api.models import Well, Production
    from collector.export_parameter import ExportParameter
    from collector.builder import ExportBuilder, ExportRetriever
    from collector.endpoint import load_from_config
    from config import get_active_config
    from collector.xmlparser import XMLParser
    from collector.transformer import WellboreTransformer
    from util import to_json
    from time import sleep

    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    url = conf.API_BASE_URL
    endpoints = load_from_config(conf)

    # # ? well example
    # endpoint = endpoints["wells"]
    # c = Collector(endpoint)
    # requestor = ExportBuilder(url, endpoint, functions={})
    # task = endpoint.tasks["driftwood"]
    # ep = ExportParameter(**task.options)
    # jid = requestor.submit(ep)

    # retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)

    # sleep(5)
    # xml = retr.get()
    # parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    # document = parser.parse(xml)
    # wellbores = WellboreTransformer.extract_from_wellset(document)
    # to_json(wellbores, "test/data/wellbores_parsed.json")
    # print(f"Parsed {len(wellbores)} wellbores")

    # for wb in wellbores:
    #     Well(**wb).save()

    # ? production example
    endpoint = endpoints["production"]
    c = Collector(endpoint)
    requestor = ExportBuilder(url, endpoint, functions={})
    task = endpoint.tasks["driftwood"]
    ep = ExportParameter(**task.options)
    jid = requestor.submit(ep)

    retr = ExportRetriever(jid, base_url=url, endpoint=endpoint)

    sleep(5)
    xml = retr.get()
    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml, parse_dtypes=False)
    to_json(document, "test/data/production_unparsed.json")
    document = parser.parse(xml, parse_dtypes=True)
    to_json(document, "test/data/production_parsed.json")
    # production = ProductionTransformer.extract_from_wellset(document)
    # print(f"Parsed {len(production)} production records")

    # for wb in production:
    #     Production(**wb).save()
