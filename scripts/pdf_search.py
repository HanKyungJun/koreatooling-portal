"""
PDF 고속 텍스트 검색 유틸리티
- 첫 실행: PDF 전체를 병렬 추출 후 .cache.json 저장
- 이후 실행: 캐시에서 즉시 검색 (수초 이내)

Usage:
  python pdf_search.py <pdf_path> <keyword>
  python pdf_search.py <pdf_path> <keyword> --pages 5 59 60
  python pdf_search.py <pdf_path> <keyword> --rebuild   # 캐시 재생성
"""
import sys
import json
import time
import hashlib
import pdfplumber
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

PDF_PATH = None  # 워커 프로세스용 전역 변수


def _init_worker(pdf_path):
    global PDF_PATH
    PDF_PATH = pdf_path


def _extract_chunk(page_indices):
    results = {}
    with pdfplumber.open(PDF_PATH) as pdf:
        for i in page_indices:
            results[i] = pdf.pages[i].extract_text() or ""
    return results


def _cache_path(pdf_path):
    p = Path(pdf_path)
    return p.parent / (p.stem + ".cache.json")


def _pdf_hash(pdf_path):
    h = hashlib.md5()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache(pdf_path):
    """캐시 파일이 유효하면 로드, 없거나 PDF 변경 시 None 반환"""
    cache_file = _cache_path(pdf_path)
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("md5") == _pdf_hash(pdf_path):
            return data["pages"]  # {str(page_index): text}
    except Exception:
        pass
    return None


def build_cache(pdf_path, workers=4):
    """PDF 전체 텍스트를 병렬 추출 후 캐시 저장. 추출된 dict 반환."""
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)

    chunk_size = max(1, total // workers)
    chunks = [list(range(i, min(i + chunk_size, total))) for i in range(0, total, chunk_size)]

    all_text = {}
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(pdf_path,)) as ex:
        futures = [ex.submit(_extract_chunk, chunk) for chunk in chunks]
        for f in futures:
            all_text.update(f.result())

    cache_data = {"md5": _pdf_hash(pdf_path), "pages": {str(k): v for k, v in all_text.items()}}
    with open(_cache_path(pdf_path), "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False)

    return cache_data["pages"]


def get_pages(pdf_path, workers=4, rebuild=False):
    """캐시 우선 로드, 없으면 빌드"""
    if not rebuild:
        cached = load_cache(pdf_path)
        if cached is not None:
            return cached, True  # (pages_dict, from_cache)
    pages = build_cache(pdf_path, workers=workers)
    return pages, False


def search(pages, keyword):
    return sorted([int(k) + 1 for k, text in pages.items() if keyword in text])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PDF 고속 키워드 검색")
    parser.add_argument("pdf", help="PDF 파일 경로")
    parser.add_argument("keyword", help="검색 키워드")
    parser.add_argument("--pages", nargs="+", type=int, help="출력할 특정 페이지 번호")
    parser.add_argument("--workers", type=int, default=4, help="병렬 워커 수 (기본: 4)")
    parser.add_argument("--rebuild", action="store_true", help="캐시 강제 재생성")
    args = parser.parse_args()

    t0 = time.time()
    pages_dict, from_cache = get_pages(args.pdf, workers=args.workers, rebuild=args.rebuild)
    load_time = time.time() - t0

    source = "cache" if from_cache else f"built in {load_time:.1f}s, saved to cache"
    found_pages = search(pages_dict, args.keyword)
    print(f"[{source}] '{args.keyword}' found on pages: {found_pages}")

    pages_to_show = args.pages or found_pages
    if pages_to_show:
        print()
        for p in sorted(pages_to_show):
            text = pages_dict.get(str(p - 1), "")
            print(f"=== page {p} ===")
            print(text)
            print()
