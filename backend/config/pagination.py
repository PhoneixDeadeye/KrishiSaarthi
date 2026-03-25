"""Pagination helpers for APIView-based endpoints.

Backward-compatible behavior:
- Existing endpoints keep their original unpaginated payload unless the
  client explicitly supplies pagination params (`page` or `page_size`).
- This lets old clients continue working while enabling pagination for
  newer clients.
"""

from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


def get_optional_paginator(request):
    """Return a paginator only when client asks for pagination."""
    wants_pagination = (
        request.query_params.get("page") is not None
        or request.query_params.get("page_size") is not None
    )
    if not wants_pagination:
        return None
    return PageNumberPagination()
