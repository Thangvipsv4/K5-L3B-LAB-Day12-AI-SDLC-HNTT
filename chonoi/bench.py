"""Benchmark CÓ RENDER cảnh lặn (Test Contract v1.3, docs/phase4.md mục 1.1).

    python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json [--warmup 3] [--show] [--browser PATH]

Cách đo:
  1. Dựng cửa sổ chơi trực tiếp (`chonoi.live`) ở cảnh `gather` lõi với seed cho trước: cá bơi/sinh,
     Cá Sấu Năm Chèo, hiệu ứng mặc định; Út Sen đứng yên tại bến (không có input).
  2. Mở trình duyệt Chromium/Chrome/Edge ở 1280×720 tới trang `/?bench=1` (mặc định headless; `--show` để thấy cửa sổ).
  3. Trang tự làm nóng `--warmup` giây rồi đo `--duration` giây bằng requestAnimationFrame, gửi số liệu về `/bench`.
  4. Ghi `bench.json` đúng 5 trường: avg_fps, p1_low_fps, frames, measured_s, load_ms.

  frames, measured_s : số khung hình và số giây thật đo được SAU làm nóng
  avg_fps            : frames / measured_s
  p1_low_fps         : max(1, ceil(1% frames)) khung chậm nhất -> 1 / (thời gian khung trung bình của chúng)
  load_ms            : từ lúc lệnh này khởi chạy tới khung hình đầu tiên của cảnh đo

Mã thoát: 0 thành công; 2 tham số sai; 1 không tìm thấy trình duyệt / quá giờ / lỗi chạy.
Chỉ dùng thư viện chuẩn Python + một trình duyệt họ Chromium đã cài (đặt CHONOI_BROWSER nếu ở chỗ lạ).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

START_EPOCH_MS = time.time() * 1000.0   # mốc "khởi chạy chương trình" cho load_ms

from .contract import load_contract    # noqa: E402  (đo mốc thời gian trước khi import nặng)
from .errors import BadInput           # noqa: E402
from .live import LiveGame, LiveServer  # noqa: E402

WIDTH, HEIGHT = 1280, 720
CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "microsoft-edge-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser(explicit=None):
    for c in [explicit, os.environ.get("CHONOI_BROWSER")] + CANDIDATES:
        if not c:
            continue
        path = c if os.path.isabs(c) else shutil.which(c)
        if path and os.path.exists(path):
            return path
    return None


def _positive(name, cast):
    def conv(s):
        try:
            v = cast(s)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{name} phải là số")
        if v <= 0:
            raise argparse.ArgumentTypeError(f"{name} phải > 0")
        return v
    return conv


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"lỗi: {message}\n")
        sys.exit(2)


def to_bench_json(r: dict, start_epoch_ms: float) -> dict:
    """Số liệu trang gửi về -> đúng 5 trường của bench.json."""
    frames = int(r["frames"])
    measured_s = float(r["measured_s"])
    if frames <= 0 or measured_s <= 0:
        raise ValueError("không đo được khung hình nào")
    return {
        "avg_fps": round(frames / measured_s, 2),
        "p1_low_fps": round(float(r["p1_low_fps"]), 2),
        "frames": frames,
        "measured_s": round(measured_s, 3),
        "load_ms": int(round(float(r["first_frame_epoch_ms"]) - start_epoch_ms)),
    }


def main(argv=None) -> int:
    p = _Parser(prog="chonoi.bench", description="Benchmark có render cảnh lặn (bench_cmd).")
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--duration", required=True, type=_positive("duration", float), help="số giây đo (sau làm nóng)")
    p.add_argument("--out", required=True)
    p.add_argument("--warmup", type=_positive("warmup", float), default=3.0)
    p.add_argument("--browser", help="đường dẫn trình duyệt Chromium/Chrome/Edge (mặc định tự tìm)")
    p.add_argument("--show", action="store_true", help="mở cửa sổ thấy được thay vì headless")
    a = p.parse_args(argv)

    browser = find_browser(a.browser)
    if not browser:
        sys.stderr.write("không tìm thấy Chrome/Chromium/Edge. Cài một trình duyệt họ Chromium hoặc đặt CHONOI_BROWSER=<đường dẫn>.\n")
        return 1
    try:
        tuning = load_contract()["tuning"]
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2

    # cảnh gather lõi mặc định (scenario rỗng): cá, Cá Sấu, hiệu ứng mặc định; không input -> đứng yên tại bến
    game = LiveGame("gather", tuning, {}, a.seed)
    server = LiveServer(game, "127.0.0.1", 0)
    server.start()
    profile = tempfile.mkdtemp(prefix="chonoi-bench-")
    url = f"{server.url}?bench=1&warm={a.warmup}&dur={a.duration}&w={WIDTH}&h={HEIGHT}"
    # cửa sổ rộng hơn một chút cho viền trình duyệt; trang tự vẽ canvas đúng WIDTH×HEIGHT px
    flags = [f"--user-data-dir={profile}", f"--window-size={WIDTH + 16},{HEIGHT + 100}", "--no-first-run",
             "--no-default-browser-check", "--disable-background-timer-throttling",
             "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
             "--disable-extensions", "--mute-audio"]
    flags += [f"--app={url}"] if a.show else ["--headless=new", "--hide-scrollbars", url]
    proc = subprocess.Popen([browser] + flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        timeout = a.warmup + a.duration + 60
        if not game.bench_done.wait(timeout):
            sys.stderr.write(f"quá {timeout:.0f}s mà trang chưa gửi kết quả đo (trình duyệt: {browser}).\n")
            return 1
        try:
            result = to_bench_json(game.bench_result, START_EPOCH_MS)
        except (KeyError, TypeError, ValueError) as e:
            sys.stderr.write(f"số liệu đo không hợp lệ: {e} ({game.bench_result!r})\n")
            return 1
        out_dir = os.path.dirname(os.path.abspath(a.out))
        os.makedirs(out_dir, exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(json.dumps(result, ensure_ascii=False))
        extra = game.bench_result
        if isinstance(extra, dict) and "draw_ms_avg" in extra:   # chẩn đoán, không ghi vào bench.json
            sys.stderr.write(f"(chẩn đoán) vẽ trung bình {float(extra['draw_ms_avg']):.2f} ms/khung, "
                             f"khung {extra.get('width')}x{extra.get('height')}\n")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        server.stop()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
