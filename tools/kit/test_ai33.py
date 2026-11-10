"""Test lệnh giong-ai33 không gọi mạng: xem trước không gửi lời, --yes gửi đúng ≥ 2 speakers, tải tệp về."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai33  # noqa: E402


class R:
    def __init__(self, d=None, code=200, content=b""):
        self._d, self.status_code, self.content, self.headers, self.text = d or {}, code, content, {}, ""

    def json(self):
        return self._d


def _ns(**kw):
    p = argparse.ArgumentParser()
    ai33.dang_ky(p)
    a = p.parse_args([])
    for k, v in kw.items():
        setattr(a, k, v)
    return a


def test_xem_truoc_khong_gui(monkeypatch, tmp_path, capsys):
    goi = []
    monkeypatch.setattr(ai33, "khoa", lambda ten: "x")
    monkeypatch.setattr(ai33, "goi_api", lambda m, url, **kw: goi.append((m, url)) or R({"credits": 1000}))
    rc = ai33.chay(_ns(voice="clone_1", text="Hello there.", out=str(tmp_path / "a.mp3")))
    assert rc == 0
    assert all(m == "GET" for m, _ in goi)
    assert "CHƯA ĐỌC" in capsys.readouterr().out


def test_doc_that(monkeypatch, tmp_path):
    gui = {}

    def goi_api(m, url, **kw):
        if url.endswith("/v1/credits"):
            return R({"credits": 10_000})
        gui.update(kw)
        return R({"task_id": "t1"})

    def gui_http(m, url, **kw):
        if "/v1/task/" in url:
            return R({"status": "done", "credit_cost": 9, "metadata": {"audio_url": "http://a/x.mp3"}})
        return R(content=b"MP3")

    monkeypatch.setattr(ai33, "khoa", lambda ten: "x")
    monkeypatch.setattr(ai33, "goi_api", goi_api)
    monkeypatch.setattr(ai33, "gui_http", gui_http)
    out = tmp_path / "b.mp3"
    assert ai33.chay(_ns(voice="clone_1", text="Line one.\nLine two.", out=str(out), yes=True)) == 0
    than = gui["data"].decode("utf-8")
    assert "A> Line one.\nA> Line two." in than
    sp = json.loads(than.split('name="speakers"\r\n\r\n')[1].split("\r\n")[0])
    assert len(sp) >= 2 and all(s["voice_id"] == "clone_1" for s in sp)
    assert out.read_bytes() == b"MP3"
    assert (tmp_path / "b.ai33_task.json").exists()
