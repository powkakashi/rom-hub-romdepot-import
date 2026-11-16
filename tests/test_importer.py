import sys
import types as pytypes

import pytest

pytest.importorskip("rom_hub_sdk")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_manifest_declares_search_and_importer():
    text = (ROOT / "manifest.toml").read_text()
    assert 'importer = "romdepot_import.importer:Importer"' in text
    assert "session_cookie" in text


def test_importer_refuses_without_a_cookie():
    from romdepot_import.importer import ImportRefused, Importer

    ctx = pytypes.SimpleNamespace(config={"catalog_path": "", "session_cookie": ""})
    try:
        Importer(ctx).plan(pytypes.SimpleNamespace(source_id="Nintendo DS/US/x.zip"))
    except ImportRefused as exc:
        assert "session cookie" in str(exc)
    else:
        raise AssertionError("expected ImportRefused")
