from typing import List, Dict, Tuple, Union
import logging


from config import get_active_config

logger = logging.getLogger(__name__)
conf = get_active_config()
logger.setLevel(int(conf.LOG_LEVEL))

datadog = None


def load_datadog():

    # print("Loading Datadog")
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


def send(name: str, points: Union[int, float, List[Tuple]]):
    """ Send a metric through the Datadog http apiself.

        Example:
                    api.Metric.send(
                        metric='my.series',
                        points=[
                            (now, 15),
                            (future_10s, 16)
                        ]
                    )

    Arguments:
        name {str} -- metric name
        points {Union[int, float, List[Tuple]]} -- metric value(s)
    """
    try:
        if datadog:
            result = datadog.api.Metric.send(metric=name, points=points)
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


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(10)
    load_datadog()
    name = "app.test"
    points = 15
    send(name, points)
