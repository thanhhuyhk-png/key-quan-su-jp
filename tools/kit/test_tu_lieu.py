"""Test lệnh tu-lieu không gọi mạng: đọc đúng dạng phản hồi NARA/Smithsonian, bỏ qua nguồn thiếu khoá."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tu_lieu  # noqa: E402


class R:
    def __init__(self, d):
        self._d, self.status_code, self.headers = d, 200, {}

    def json(self):
        return self._d


def _ns(**kw):
    p = argparse.ArgumentParser()
    tu_lieu.dang_ky(p)
    a = p.parse_args([])
    for k, v in kw.items():
        setattr(a, k, v)
    return a


NARA = {"body": {"hits": {"hits": [{"_source": {"record": {"naId": 1, "title": "Landing on Peleliu",
        "digitalObjects": [{"objectType": "Image (JPG)", "objectUrl": "https://x/a.jpg"}]}}}]}}}
SI = {"response": {"rows": [{"title": "Map", "content": {"descriptiveNonRepeating": {"record_ID": "s1", "record_link": "http://r",
      "online_media": {"media": [{"type": "Images", "content": "http://i", "usage": {"access": "CC0"}}]}}}}]}}


def test_doc_nara_si(monkeypatch, capsys):
    tham = {}
    monkeypatch.setattr(tu_lieu, "khoa", lambda t: "x")
    monkeypatch.setattr(tu_lieu, "co_khoa", lambda t: True)
    monkeypatch.setattr(tu_lieu, "goi_api", lambda m, url, **kw: tham.setdefault(url, kw["params"]) and (R(NARA) if "archives" in url else R(SI)))
    assert tu_lieu.chay(_ns(q="Peleliu", nguon="nara,si", chi_anh=True)) == 0
    out = capsys.readouterr().out
    assert "NAID 1\tLanding on Peleliu" in out and "https://x/a.jpg" in out
    assert "CC0 (Open Access)" in out
    nara = next(v for k, v in tham.items() if "archives" in k)
    assert nara["typeOfMaterials"].startswith("Photographs")
    assert "x" not in out.split("\n", 1)[1].split("\t")[0]


def test_thieu_khoa_bo_qua(monkeypatch, capsys):
    monkeypatch.setattr(tu_lieu, "co_khoa", lambda t: False)
    assert tu_lieu.chay(_ns(q="Peleliu", nguon="pexels")) == 0
    assert "thiếu khoá PEXELS_API_KEY" in capsys.readouterr().out
