""" Source: https://github.com/karec/cookiecutter-flask-restful """

import logging
from flask import url_for, request

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1


def paginate(model, schema, **kwargs):
    page = int(request.args.get("page", DEFAULT_PAGE_NUMBER))
    per_page = int(request.args.get("page_size", DEFAULT_PAGE_SIZE))
    page_obj = model.get(paginate=True, page=page, per_page=per_page, **kwargs)
    next = url_for(
        request.endpoint,
        page=page_obj.next_num if page_obj.has_next else page_obj.page,
        per_page=per_page,
        **request.view_args,
    )
    prev = url_for(
        request.endpoint,
        page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
        per_page=per_page,
        **request.view_args,
    )

    return {
        "total": page_obj.total,
        "pages": page_obj.pages,
        "next": next,
        "prev": prev,
        "data": schema.dump(page_obj.items),
    }

