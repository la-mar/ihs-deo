# pylint: disable=not-an-iterable, no-member, arguments-differ
import logging

import api.schema as schemas
from api.models import WellMasterVertical, WellVertical
from api.resources.base import IDListResource, IDResource
from api.resources.well.base import WellListResource, WellResource

logger = logging.getLogger(__name__)


class VerticalWell(WellResource):
    """ All data for a well """

    model = WellVertical
    schema = schemas.WellFullSchema(many=True)


class VerticalWellList(WellListResource):
    """ All data for a list of wells """

    model = WellVertical
    schema = schemas.WellFullSchema(many=True)


class VerticalWellHeader(WellResource):
    """ Header data for a well """

    model = WellVertical
    schema = schemas.WellHeaderSchema(many=True)


class VerticalWellHeaderList(WellListResource):
    """ Header data for a list of wells """

    model = WellVertical
    schema = schemas.WellHeaderSchema(many=True)


class VerticalWellIPTest(WellResource):
    """ IP tests for a well """

    model = WellVertical
    schema = schemas.WellIPTestSchema(many=True)


class VerticalWellIPTestList(WellListResource):
    """ IP tests for a list of wells """

    model = WellVertical
    schema = schemas.WellIPTestSchema(many=True)


class VerticalWellSurvey(WellResource):
    """ Active survey of a well """

    model = WellVertical
    schema = schemas.SurveySchema(many=True)


class VerticalWellSurveyList(WellListResource):
    """ Active survey for a list of wells """

    model = WellVertical
    schema = schemas.SurveySchema(many=True)


class VerticalWellFrac(WellResource):
    """ Completion data for a well """

    model = WellVertical
    schema = schemas.WellFrac(many=True)


class VerticalWellFracList(WellListResource):
    """ Completion data for a list of wells """

    model = WellVertical
    schema = schemas.WellFrac(many=True)


class VerticalWellIDs(IDResource):
    """ List of Well IDs for an area"""

    model = WellMasterVertical
    schema = schemas.IDListSchema(many=True)


class VerticalWellIDList(IDListResource):

    model = WellMasterVertical
    schema = schemas.IDListSchema(many=True)
