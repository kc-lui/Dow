import hashlib

import pytest

from dowtheory.backtest import protocol as proto
from dowtheory.config import project_root


def test_scoped_hash_uses_line_anchored_marker(tmp_path):
    body = "intro mentions PROTOCOL-HASH-SCOPE in prose\nsecond line\n"
    f = tmp_path / "t.md"
    f.write_text(body + "PROTOCOL-HASH-SCOPE: everything above\ntail\n", encoding="utf-8")
    assert proto.scoped_sha256(f) == hashlib.sha256(body.encode()).hexdigest()
    f.write_text("only a PROTOCOL-HASH-SCOPE mention\n", encoding="utf-8")
    with pytest.raises(ValueError):
        proto.scoped_sha256(f)


def test_scoped_hash_reproduces_stored_value():
    table, hash_file = proto.protocol_paths(project_root())
    stored = proto.read_stored_hashes(hash_file)
    assert len(stored) == 2
    assert proto.sha256_file(table) == stored[0]
    assert proto.scoped_sha256(table) == stored[1]


def test_caveat_extraction_is_verbatim_and_has_bgk():
    table, _ = proto.protocol_paths(project_root())
    text = table.read_text(encoding="utf-8")
    assert proto.BGK_CAVEAT in text
    assert len(proto.coverage_caveats(text)) >= 6
    assert "R8" in proto.printed_caveats(text)
