#
# Copyright (c) 2026, Axius SDC, Inc.
# Licensed under the Apache License, Version 2.0.
#
"""
MCP stdio server for `sdcdcatap`: one tool, `write_catalog`, over the same function the CLI calls.

An agent that can read a published model with `sdcreader` can ask this server for its DCAT-AP 3.0.1 description.
The scaffold (JSON-RPC over stdio, protocol negotiation, `isError` results, the package cache) is `sdcreader.mcp`,
shared by every SDC projection server. No tool takes a URL: the catalog host is fixed at start with `--host`.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from sdcreader.mcp import PackageCache, Server, ToolError, source_properties, str_arg
from sdcreader.package import DEFAULT_HOST, fetch_package  # noqa: F401  (patched by tests)

from sdcdcatap import __version__
from sdcdcatap.dcatap import DeclaredInputError, build_catalog, load_declared

SERVER_NAME = "sdcdcatap"
ISSUES = "https://github.com/SemanticDataCharter/sdc_dcat3_ap/issues"

_HOST: str = DEFAULT_HOST
_CACHE: dict = {}

TOOLS = [
    {
        "name": "write_catalog",
        "description": (
            "Write a DCAT-AP 3.0.1 catalog describing one or more published Semantic Data Charter models as datasets, as Turtle or JSON-LD, each with the model's schema cited by URL and SHA-256. Validated in this package's CI with SEMIC's own SHACL shapes from a pinned snapshot."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                **source_properties(plural=True),
                "contact_name": {"type": "string", "description": "The publisher's contact point name; the package's declared default applies when omitted."},
                "contact_email": {"type": "string", "description": "The publisher's contact e-mail; the package's declared default applies when omitted."},
                "date": {"type": "string", "description": "The catalog date, YYYY-MM-DD; today when omitted."},
                "format": {"type": "string", "enum": ["turtle", "json-ld"], "default": "turtle", "description": "Serialization of the catalog."}
            },
            "additionalProperties": False,
        },
    },
]


def _cache() -> PackageCache:
    import sdcdcatap.mcp_server as me

    return PackageCache(host=_HOST, storage=_CACHE, fetcher=lambda ct_id, host: me.fetch_package(ct_id, host=host))


def _date(args: dict[str, Any]) -> date | None:
    v = str_arg(args, "date")
    if v is None:
        return None
    try:
        return date.fromisoformat(v)
    except ValueError as exc:
        raise ToolError("`date` must be YYYY-MM-DD.") from exc


def _format(args: dict[str, Any]) -> str:
    fmt = str_arg(args, "format", "turtle")
    if fmt not in ("turtle", "json-ld"):
        raise ToolError("`format` must be turtle or json-ld.")
    return fmt


def _handle_write(args: dict[str, Any]) -> Any:
    items = _cache().many(args)
    today = _date(args)
    fmt = _format(args)
    try:
        declared = load_declared(None, str_arg(args, "contact_name"), str_arg(args, "contact_email"))
    except DeclaredInputError as exc:
        raise ToolError(str(exc)) from exc
    g = build_catalog([m for _, m in items], declared, today=today)
    return {
        "standard": "DCAT-AP 3.0.1", "format": fmt, "datasets": len(items), "triples": len(g),
        "models": [{"ct_id": m.ct_id, "title": m.title, "schema_url_pinned": p.schema_url_pinned} for p, m in items],
        "document": g.serialize(format="turtle") if fmt == "turtle" else json.loads(g.serialize(format="json-ld")),
        "note": "Validated in this package's CI against SEMIC's DCAT-AP SHACL shapes from a pinned snapshot; the shapes are not shipped in the wheel.",
    }


TOOL_HANDLERS = {"write_catalog": _handle_write}


def _server() -> Server:
    return Server(
        name=SERVER_NAME, version=__version__, tools=TOOLS, handlers=TOOL_HANDLERS, issues_url=ISSUES,
        instructions=(
            "Describe published Semantic Data Charter models in DCAT-AP 3.0.1 terms. `write_catalog` takes "
            + ("model identifiers (ct_ids), fetched from " if True else "a model identifier (ct_id), fetched from ")
            + f"{_HOST}, or package directories on disk, and returns the catalog under `document` (Turtle text, or a JSON-LD object). "
            "Read-only apart from the document it returns; no account; no tool takes a URL."
        ),
    )


def _handle_request(request: Any) -> dict | None:
    return _server().handle(request)


def main(argv: list[str] | None = None) -> None:
    """Entry point for `sdcdcatap-mcp` and `sdcdcatap mcp`."""
    import argparse

    global _HOST

    parser = argparse.ArgumentParser(prog="sdcdcatap-mcp", description="MCP stdio server: DCAT-AP 3.0.1 descriptions of published Semantic Data Charter models.")
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help=f"The SDCStudio host whose public catalog is read, fixed here so a caller cannot redirect the server. Default {DEFAULT_HOST}.")
    args = parser.parse_args(argv)
    _HOST = args.host.rstrip("/")
    _server().run_stdio()


if __name__ == "__main__":
    main()
