""" Source: https://github.com/karec/cookiecutter-flask-restful """

from typing import Union, Mapping, Dict
import logging
from requests import Request
from urllib.parse import urljoin
from flask import Response, request, url_for
from flask import jsonify

# from flask_restful import ResponseBase

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1
LINK_TEMPLATE = '<{url}>; rel="{rel}"'


def paginate(model, schema, **kwargs):
    page = int(request.args.get("page", DEFAULT_PAGE_NUMBER))
    page_size = int(request.args.get("page_size", DEFAULT_PAGE_SIZE))
    page_obj = model.get(paginate=True, page=page, per_page=page_size, **kwargs)
    other_request_kwargs = {
        k: v
        for k, v in request.args.items()
        if k not in ["page", "per_page", "page_size"]
    }

    if page > 1:
        prev = urljoin(
            request.url_root,
            url_for(
                request.endpoint,
                **other_request_kwargs,
                page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
                page_size=page_size,
                **request.view_args,
            ),
        )
    else:
        prev = None

    if page < page_obj.pages:
        next = urljoin(
            request.url_root,
            url_for(
                request.endpoint,
                **other_request_kwargs,
                page=page_obj.next_num if page_obj.has_next else page_obj.page,
                page_size=page_size,
                **request.view_args,
            ),
        )
    else:
        next = None

    first = urljoin(
        request.url_root,
        url_for(
            request.endpoint,
            **other_request_kwargs,
            page=1,
            page_size=page_size,
            **request.view_args,
        ),
    )

    last = urljoin(
        request.url_root,
        url_for(
            request.endpoint,
            **other_request_kwargs,
            page=page_obj.pages,
            page_size=page_size,
            **request.view_args,
        ),
    )

    current = urljoin(
        request.url_root,
        url_for(
            request.endpoint,
            **other_request_kwargs,
            page=page,
            page_size=page_size,
            **request.view_args,
        ),
    )

    links = [
        LINK_TEMPLATE.format(url=urljoin(request.url_root, prev), rel="prev")
        if prev
        else None,
        LINK_TEMPLATE.format(url=urljoin(request.url_root, next), rel="next")
        if next
        else None,
        LINK_TEMPLATE.format(url=urljoin(request.url_root, first), rel="first"),
        LINK_TEMPLATE.format(url=urljoin(request.url_root, last), rel="last"),
        LINK_TEMPLATE.format(url=urljoin(request.url_root, current), rel="current"),
    ]

    headers = {
        "Link": ",".join([x for x in links if x is not None]),
        "X-Total-Count": page_obj.total,
    }
    data = schema.dump(page_obj.items)
    response_body = {
        "total": page_obj.total,
        "pages": page_obj.pages,
        "next": next,
        "prev": prev,
        "data": schema.dump(page_obj.items),
    }
    # data = schema.dump(page_obj.items)
    # response_body = PaginatedResponse(
    #     response=data, per_page=page_size, current_page=page, total=page_obj.total
    # )
    # logger.debug(response_body)
    resp = jsonify(data)
    for k, v in headers.items():
        resp.headers[k] = v

    return resp


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config
    from api.models import WellHorizontal
    from api.schema import WellBaseSchema

    app = create_app()
    app.app_context().push()
    ctx = app.test_request_context("/well/h?api14=42461409160000&page=2&page_size=5")
    ctx.push()
    conf = get_active_config()

    api14 = "42461409160000"
    api14s = ["42461409160000", "42461009720100"]
    r = WellHorizontal().get(api14=api14)
    data = WellBaseSchema(many=True).dump(r)

    p = paginate(WellHorizontal, WellBaseSchema(many=True))

    # dir(p)
    # p.response, p.headers
    # p
    # urljoin(request.url_root, "/well/h?api14=42461409160000&page=2&page_size=5")

