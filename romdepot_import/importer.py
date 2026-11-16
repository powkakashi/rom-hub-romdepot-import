"""Import a file from The ROM Depot using the operator's own session.

The upstream plugin stops at `stream` because ROM Hub refuses a plugin-set
`Cookie` header. This one depends on the host patch that allows it: the cookies
live in this plugin's `secret` config, and the host only sends them to
theromdepot.com, which the manifest already allowlists.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from rom_hub_sdk import FetchFile, FetchPlan, ImportProvider, SearchResult

from .catalog import clean_path, load_catalog


class ImportRefused(RuntimeError):
    """The requested path is not in the catalogue, or no session is configured."""


class Importer(ImportProvider):
    def plan(self, result: SearchResult) -> FetchPlan:
        cookie = str(self.ctx.config.get("session_cookie") or "").strip()
        if not cookie:
            raise ImportRefused(
                "no session cookie configured: export it from a signed-in browser "
                "and set it with 'rom-hub plugin secret set romdepot-import session_cookie'"
            )
        try:
            source_id = clean_path(getattr(result, "source_id", "") or "")
        except ValueError as exc:
            raise ImportRefused(f"invalid The ROM Depot path: {exc}") from exc

        entries = {entry.path: entry for entry in
                   load_catalog(self.ctx.config.get("catalog_path"))}
        entry = entries.get(source_id)
        if entry is None:
            raise ImportRefused(
                f"{source_id!r} is not a file in the configured /api/getContents export"
            )
        if not entry.platform:
            raise ImportRefused(f"{entry.name!r} does not map to a ROMarr platform")

        name = PurePosixPath(entry.name).name
        return FetchPlan(
            files=[FetchFile(
                url=entry.download_url,
                filename=name,
                size_bytes=entry.size_bytes or None,
                headers={"Cookie": cookie},
            )],
            platform=entry.platform,
            collection=str(self.ctx.config.get("collection") or "The ROM Depot"),
        )
