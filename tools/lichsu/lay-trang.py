"""Tải một trang web và lưu chữ hiển thị (bỏ script, style) để đối chiếu câu trích của sổ số liệu.

Dùng: python -I lay-trang.py <url> <thư mục lưu>
Ghi <thư mục>/<tên-từ-url>.txt; dòng đầu là "URL: <url>", sau đó là chữ của trang.
In đường dẫn file đã lưu. Mã thoát 1 khi tải lỗi hoặc trang gần như rỗng (< 500 ký tự).
Chỉ dùng thư viện chuẩn. Chữ thô là dữ liệu chưa tin cậy: chỉ để đọc, không chạy.
"""
import gzip
import hashlib
import http.cookiejar
import html
import re
import sys
import urllib.request
import zlib
from html.parser import HTMLParser
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
BO_THE = {"script", "style", "noscript", "svg", "template"}
KHOI = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "td", "th",
        "section", "article", "figcaption", "blockquote"}


class LayChu(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sau = 0
        self.manh = []

    def handle_starttag(self, tag, attrs):
        if tag in BO_THE:
            self.sau += 1
        elif tag in KHOI:
            self.manh.append("\n")

    def handle_endtag(self, tag):
        if tag in BO_THE and self.sau:
            self.sau -= 1
        elif tag in KHOI:
            self.manh.append("\n")

    def handle_data(self, data):
        if not self.sau:
            self.manh.append(data)


def ten_file(url: str) -> str:
    goc = re.sub(r"^https?://(www\.)?", "", url).split("?")[0].strip("/")
    goc = re.sub(r"[^A-Za-z0-9._-]+", "_", goc)[-80:]
    return f"{goc}-{hashlib.sha1(url.encode()).hexdigest()[:8]}.txt"


def giai_nen(du_lieu: bytes, kieu: str) -> bytes:
    if kieu == "gzip":
        return gzip.decompress(du_lieu)
    if kieu == "deflate":
        return zlib.decompress(du_lieu)
    return du_lieu


def tai(url: str) -> str:
    """Tải có giữ cookie (qdnd.vn đặt cookie trong bước chuyển hướng 302).
    Trang lỗi chứng chỉ SSL thì báo lỗi, không bỏ qua kiểm chứng chỉ: tìm nguồn chính thống khác."""
    mo = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    yc = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "vi,en;q=0.8", "Accept-Encoding": "gzip, deflate"})
    with mo.open(yc, timeout=40) as tl:
        tho = giai_nen(tl.read(), tl.headers.get("Content-Encoding", ""))
        bang_ma = tl.headers.get_content_charset() or "utf-8"
    return tho.decode(bang_ma, errors="replace")


def chu_hien_thi(trang: str) -> str:
    bo = LayChu()
    bo.feed(trang)
    chu = html.unescape("".join(bo.manh))
    dong = [re.sub(r"[ \t ]+", " ", d).strip() for d in chu.splitlines()]
    return "\n".join(d for d in dong if d)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    url, thu_muc = sys.argv[1], Path(sys.argv[2])
    try:
        chu = chu_hien_thi(tai(url))
    except Exception as loi:  # báo lỗi tải cho người gọi, không nuốt
        print(f"LỖI TẢI {url}: {loi}", file=sys.stderr)
        return 1
    if len(chu) < 500:
        print(f"TRANG GẦN RỖNG ({len(chu)} ký tự): {url}", file=sys.stderr)
        return 1
    thu_muc.mkdir(parents=True, exist_ok=True)
    dich = thu_muc / ten_file(url)
    dich.write_text(f"URL: {url}\n{chu}\n", encoding="utf-8")
    print(dich)
    return 0


if __name__ == "__main__":
    sys.exit(main())
