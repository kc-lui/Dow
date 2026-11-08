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


def test_r1_caveat_uses_run_numbers():
    import datetime as dt

    ref = proto.r1_caveat(33, "DJ", 0.0055, 0.69, reference=True)
    assert "n = 33" in ref and "0.0055" in ref and "0.65 to 0.69" in ref
    other = proto.r1_caveat(20, "SP_IYT", 0.0123, 0.7, reference=False)
    assert "n = 20" in other and "0.0123" in other and "SP_IYT" in other
    assert "0.65 to 0.69" not in other and "0.0085" not in other
    assert "Baseline not simulated for this run; see reports/backtest_audit.md" in other
    assert "p_sim = n/a" in proto.r1_caveat(1, "DJ", None)
    d = dt.date
    assert proto.is_reference_run("DJ", d(1992, 1, 2), d(2026, 11, 6), "pct0.03/0.08f15")
    assert not proto.is_reference_run("DJ", d(2020, 1, 2), d(2021, 2, 24), "pct0.03/0.08f15")
    assert not proto.is_reference_run("SP_IYT", d(1992, 1, 2), d(2026, 11, 6), "pct0.03/0.08f15")
