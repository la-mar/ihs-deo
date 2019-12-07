from typing import List, Tuple, Union
import logging


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


def parse_tags(tags: list) -> List[str]:
    """ Ensure all tags are strings """
    result = []
    for x in tags:
        if isinstance(x, str):
            result.append(x.lower())
    return result


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
                tags=parse_tags(tags or []),
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


def post_heartbeat():
    return post("heartbeat", 1, metric_type="gauge")


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(10)
    load()
    name = "app.test"
    points = 15
    post(name, points)
