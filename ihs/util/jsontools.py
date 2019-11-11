import json
from datetime import datetime, date


class DateTimeEncoder(json.JSONEncoder):
    # pylint: disable=arguments-differ, method-hidden
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
