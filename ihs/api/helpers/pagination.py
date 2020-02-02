""" Source: https://github.com/karec/cookiecutter-flask-restful """

import logging
from flask import url_for, request

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1


def paginate(model, schema, **kwargs):
    page = int(request.args.get("page", DEFAULT_PAGE_NUMBER))
    page_size = int(request.args.get("page_size", DEFAULT_PAGE_SIZE))
    page_obj = model.get(paginate=True, page=page, per_page=page_size, **kwargs)
    other_request_kwargs = {
        k: v
        for k, v in request.args.items()
        if k not in ["page", "per_page", "page_size"]
    }
    next = (
        url_for(
            request.endpoint,
            **other_request_kwargs,
            page=page_obj.next_num if page_obj.has_next else page_obj.page,
            page_size=page_size,
            **request.view_args,
        )
        if page < page_obj.pages
        else None
    )
    prev = (
        url_for(
            request.endpoint,
            **other_request_kwargs,
            page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
            page_size=page_size,
            **request.view_args,
        )
        if page > 1
        else None
    )

    return {
        "total": page_obj.total,
        "pages": page_obj.pages,
        "next": next,
        "prev": prev,
        "data": schema.dump(page_obj.items),
    }

