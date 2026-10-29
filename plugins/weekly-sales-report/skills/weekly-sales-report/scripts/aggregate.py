"""판매내역 CSV를 주간 매출 리포트용 수치로 집계한다.

사용법:
  python -I -X utf8 aggregate.py <입력파일> [--today YYYY-MM-DD] > out.txt

<입력파일>은 구글 드라이브 download_file_content(text/csv)의 결과 JSON 파일
({"content": <base64>, ...}) 또는 일반 CSV 파일이다.
기간은 --today 기준 직전 월~일(지난주)과 그 전주이며, 생략하면 오늘 날짜를 쓴다.
출력은 JSON 한 덩어리다. 콘솔 인코딩 문제를 피하려면 파일로 리다이렉트해서 읽는다.
"""
import argparse
import base64
import csv
import datetime as dt
import io
import json
from collections import defaultdict

DAYS = "월화수목금토일"


def load_rows(path):
    raw = open(path, encoding="utf-8").read()
    try:
        raw = base64.b64decode(json.loads(raw)["content"]).decode("utf-8")
    except (ValueError, KeyError, TypeError):
        pass
    return list(csv.DictReader(io.StringIO(raw.lstrip("﻿"))))


def num(s):
    return int(s.replace(",", "") or 0)


def week_range(today):
    this_mon = today - dt.timedelta(days=today.weekday())
    mon = this_mon - dt.timedelta(days=7)
    return mon, mon + dt.timedelta(days=6)


def aggregate(rows, start, end):
    s, e = start.isoformat(), end.isoformat()
    sel = [r for r in rows if s <= r["주문일"] <= e]
    orders = {r["주문번호"] for r in sel}
    rev = sum(num(r["결제금액"]) for r in sel)
    ch = defaultdict(lambda: [0, set()])
    prod = defaultdict(int)
    day = defaultdict(int)
    for r in sel:
        c = ch[r["판매채널"]]
        c[0] += num(r["결제금액"])
        c[1].add(r["주문번호"])
        prod[r["상품명"]] += num(r["결제금액"])
        day[r["주문일"]] += num(r["결제금액"])
    return {
        "period": [s, e],
        "revenue": rev,
        "orders": len(orders),
        "qty": sum(num(r["수량"]) for r in sel),
        "aov": round(rev / len(orders)) if orders else 0,
        "shipping": sum(num(r["배송비"]) for r in sel),
        "channels": {k: {"revenue": v[0], "orders": len(v[1])} for k, v in sorted(ch.items())},
        "products": dict(sorted(prod.items(), key=lambda kv: -kv[1])),
        "daily": {d: day.get(d, 0) for d in (
            (start + dt.timedelta(days=i)).isoformat() for i in range(7))},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--today", default=dt.date.today().isoformat())
    a = ap.parse_args()
    rows = load_rows(a.path)
    mon, sun = week_range(dt.date.fromisoformat(a.today))
    out = {
        "rows": len(rows),
        "total_revenue_all_rows": sum(num(r["결제금액"]) for r in rows),
        "last_week": aggregate(rows, mon, sun),
        "prev_week": aggregate(rows, mon - dt.timedelta(days=7), sun - dt.timedelta(days=7)),
        "title": f"[주간 매출 리포트] {mon.month}/{mon.day}(월)~{sun.month}/{sun.day}(일)",
        "weekday_labels": {(mon + dt.timedelta(days=i)).isoformat(): DAYS[i] for i in range(7)},
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
