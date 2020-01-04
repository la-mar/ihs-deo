# pylint: disable=not-an-iterable, no-member, # pylint: disable=not-an-iterable, no-member, arguments-differ
import logging

import api.schema as schemas
from api.models import WellMasterHorizontal, WellHorizontal

from api.resources.base import IDResource, IDListResource
from api.resources.well.base import WellResource, WellListResource

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

    model = WellMasterHorizontal
    schema = schemas.WellFrac(many=True)


class HorizontalWellIDs(IDResource):
    """ List of Well IDs for an area"""

    model = WellMasterHorizontal
    schema = schemas.IDListSchema(many=True)


class HorizontalWellIDList(IDListResource):
    """ List of Well IDs for multiple areas"""

    model = WellMasterHorizontal
    schema = schemas.IDListSchema(many=True)
