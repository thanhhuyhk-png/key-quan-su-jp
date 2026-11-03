"""Test cho heatmap.py: đọc đường "Được phát lại nhiều nhất" (Most replayed) từ JSON yt-dlp."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import heatmap as hm  # noqa: E402


def mau(values, dur=1000.0):
    step = dur / len(values)
    return [{"start_time": i * step, "end_time": (i + 1) * step, "value": v} for i, v in enumerate(values)]


def test_doc_tu_json_yt_dlp(tmp_path):
    p = tmp_path / "v.info.json"
    p.write_text(json.dumps({"id": "abc", "duration": 1000, "heatmap": mau([0.1] * 100)}), encoding="utf-8")
    info = hm.doc(p)
    assert info["id"] == "abc" and len(info["heatmap"]) == 100


def test_khong_co_heatmap_thi_bao_ro(tmp_path):
    p = tmp_path / "v.info.json"
    p.write_text(json.dumps({"id": "x", "duration": 500, "heatmap": None}), encoding="utf-8")
    kq = hm.phan_tich(hm.doc(p))
    assert kq["co_du_lieu"] is False
    assert "không trả heatmap" in kq["ghi_chu"]


def test_tim_dinh_bo_qua_doan_dau_va_xep_theo_do_cao():
    vals = [0.2] * 100
    vals[0] = 1.0           # đầu video luôn cao (người mới vào), mặc định bỏ 3 % đầu
    vals[40] = 0.9
    vals[75] = 0.6
    kq = hm.phan_tich({"id": "v", "duration": 1000, "heatmap": mau(vals)}, so_dinh=2)
    dinh = kq["dinh"]
    assert [d["phan_tram"] for d in dinh] == [40.5, 75.5]   # trung điểm khoảng
    assert dinh[0]["giay"] == 405          # trung điểm khoảng 400–410
    assert dinh[0]["gia_tri"] == 0.9
    assert dinh[0]["moc"] == "06:45"


def test_dinh_phai_cach_nhau_toi_thieu():
    vals = [0.1] * 100
    vals[50], vals[51], vals[52] = 0.8, 0.9, 0.85
    kq = hm.phan_tich({"id": "v", "duration": 1000, "heatmap": mau(vals)}, so_dinh=3, cach_phan_tram=5)
    assert len([d for d in kq["dinh"] if 45 <= d["phan_tram"] <= 57]) == 1


def test_ty_le_nua_sau_so_nua_dau():
    vals = [0.2] * 50 + [0.6] * 50
    kq = hm.phan_tich({"id": "v", "duration": 1000, "heatmap": mau(vals)})
    assert kq["nua_sau_chia_nua_dau"] == 3.0
