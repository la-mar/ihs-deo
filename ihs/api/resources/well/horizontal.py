# pylint: disable=not-an-iterable, no-member, # pylint: disable=not-an-iterable, no-member, arguments-differ
import logging

import api.schema as schemas
from api.models import WellHorizontal, WellMasterHorizontal
from api.resources.base import IDListResource, IDResource
from api.resources.well.base import WellListResource, WellResource

logger = logging.getLogger(__name__)


class HorizontalWell(WellResource):
    """ All data for a well """

    model = WellHorizontal
    schema = schemas.WellFullSchema(many=True)


class HorizontalWellList(WellListResource):
    """ All data for a list of wells """

    model = WellHorizontal
    schema = schemas.WellFullSchema(many=True)


class HorizontalWellHeader(WellResource):
    """ Header data for a well """

    model = WellHorizontal
    schema = schemas.WellHeaderSchema(many=True)


class HorizontalWellHeaderList(WellListResource):
    """ Header data for a list of wells """

    model = WellHorizontal
    schema = schemas.WellHeaderSchema(many=True)


class HorizontalWellIPTest(WellResource):
    """ IP tests for a well """

    model = WellHorizontal
    schema = schemas.WellIPTestSchema(many=True)


class HorizontalWellIPTestList(WellListResource):
    """ IP tests for a list of wells """

    model = WellHorizontal
    schema = schemas.WellIPTestSchema(many=True)


class HorizontalWellSurvey(WellResource):
    """ Active survey of a well """

    model = WellHorizontal
    schema = schemas.SurveySchema(many=True)


class HorizontalWellSurveyList(WellListResource):
    """ Active survey for a list of wells """

    model = WellHorizontal
    schema = schemas.SurveySchema(many=True)


class HorizontalWellFrac(WellResource):
    """ Completion data for a well """

    model = WellHorizontal
    schema = schemas.WellFrac(many=True)


class HorizontalWellFracList(WellListResource):
    """ Completion data for a list of wells """

    model = WellHorizontal
    schema = schemas.WellFrac(many=True)


class HorizontalWellIDs(IDResource):
    """ List of Well IDs for an area"""

    model = WellMasterHorizontal
    schema = schemas.IDListSchema(many=True)


class HorizontalWellIDList(IDListResource):
    """ List of Well IDs for multiple areas"""

    model = WellMasterHorizontal
    schema = schemas.IDListSchema(many=True)


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config
    from api.helpers import paginate

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    api14 = "42461409160000"
    api14s = ["42461409160000", "42461009720100"]
    r = HorizontalWell().get(api14=api14)
