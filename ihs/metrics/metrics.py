import logging
from typing import Dict, List, Tuple, Union

from config import get_active_config, project

logger = logging.getLogger(__name__)
conf = get_active_config()

datadog = None


def load():
    """ Load and initialize the Datadog library """
    try:
        parms = conf.datadog_params
        if parms.get("enabled"):
            logger.debug("Datadog Enabled")
            if parms.get("api_key") and parms.get("app_key"):
                global datadog  # pylint: disable=global-statement
                import datadog

                datadog.initialize(**parms)
                logger.info("Datadog initialized")
            else:
                missing_key = "api_key" if not parms.get("api_key") else "app_key"
                logger.error(
                    f"Failed to load Datadog configuration: missing {missing_key}"
                )
        else:
            logger.debug("Datadog disabled.")

    except Exception as e:
        logger.error(f"Failed to load Datadog configuration: {e}")


def post(
    name: str,
    points: Union[int, float, List[Tuple]],
    metric_type: str = "count",
    tags: list = None,
):
    """ Send a metric through the Datadog http api.

        Example:
                    api.Metric.post(
                        metric='my.series',
                        points=[
                            (now, 15),
                            (future_10s, 16)
                        ],
                        metric_type="count",
                        tags=["tag1", "tag2"]
                    )

    Arguments:
        name {str} -- metric name
        points {Union[int, float, List[Tuple]]} -- metric value(s)
    """
    try:
        name = f"{project}.{name}".lower()
        if datadog:
            result = datadog.api.Metric.send(
                metric=name,
                points=points,
                type=str(metric_type).lower(),
                tags=to_tags(conf.DATADOG_DEFAULT_TAGS) + to_tags(tags or []),
            )
            if result.get("status") == "ok":
                logger.debug(
                    "Datadog metric successfully sent: name=%s, points=%s",
                    name,
                    points,
                )
            else:
                logger.debug(
                    "Problem sending Datadog metric: status=%s, name=%s, points=%s",
                    result.get("status"),
                    name,
                    points,
                )
        else:
            logger.debug(
                "Datadog not configured. Suppressing metric name=%s, points=%s",
                name,
                points,
            )
    except Exception as e:
        logger.debug("Failed to send Datadog metric: %s", e)


def post_event(title: str, text: str, tags: Union[Dict, List, str] = None):
    """ Send an event through the Datadog http api. """
    try:
        if datadog:
            datadog.api.Event.create(title=title, text=text, tags=to_tags(tags or []))
    except Exception as e:
        logger.debug("Failed to send Datadog event: %s", e)


def post_heartbeat():
    """ Send service heartbeat to Datadog """
    logger.debug("posting heartbeat")
    return post("heartbeat", 1, metric_type="gauge")


def to_tags(values: Union[Dict, List, str], sep: str = ",") -> List[str]:
    """ Coerce the passed values into a list of colon separated key-value pairs.

        dict example:
            {"tag1": "value1", "tag2": "value2", ...} -> ["tag1:value1", "tag2:value2", ...]

        list example:
            ["tag1", "tag2", ...] -> ["tag1", "tag2", ...]

        str example (comma-delimited):
            "tag1:value1, tag2:value2", ..." -> ["tag1:value1", "tag2:value2", ...]

        str example (single):
            "tag1:value1" -> ["tag1:value1"]
    """
    result: List[str] = []
    if isinstance(values, dict):
        result = [
            f"{key}:{str(value).lower().replace(' ','_')}"
            for key, value in values.items()
            if isinstance(value, (str, int))
        ]
    elif isinstance(values, str):
        if "," in values:
            result = values.split(sep)
        else:
            result = [values]
    elif isinstance(values, list):
        result = values
    else:
        result = []

    return result


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(10)
    load()
    name = "app.test"
    points = 15
    post(name, points)

    d = {
        "job_options": {
            "name": "sequoia",
            "data_type": "Production Allocated",
            "template": "EnerdeqML Production",
            "criteria": {"hole_direction": "H"},
            "query_path": "production_by_api.xml",
            "api": "42461409160000",
        },
        "metadata": {
            "endpoint": "production_horizontal",
            "task": "sequoia",
            "url": "http://www.ihsenergy.com",
            "hole_direction": "H",
            "name": "sequoia",
            "data_type": "Production Allocated",
            "template": "EnerdeqML Production",
            "criteria": {"hole_direction": "H"},
            "query_path": "production_by_api.xml",
            "api": "42461409160000",
        },
    }

    to_tags(d["metadata"])
    to_tags(to_tags(d["metadata"]))
