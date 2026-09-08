#!/usr/bin/env python3
"""Minimal SQLite session log for Robby-D-Poker.

Usage:
  python3 poker.py init                      # create poker.db, seed from sessions.csv if empty
  python3 poker.py add DATE VENUE STAKES HOURS BUY_IN CASH_OUT [--game NLH] [--start HH:MM] [--notes TEXT]
  python3 poker.py list
  python3 poker.py stats
  python3 poker.py export                    # rewrite sessions.csv from the database
"""
import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "poker.db"
SCHEMA_PATH = ROOT / "schema.sql"
CSV_PATH = ROOT / "sessions.csv"
CSV_COLUMNS = ["date", "venue", "game", "stakes", "start_time", "hours", "buy_in", "cash_out", "net", "notes"]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def insert(conn, date, venue, stakes, hours, buy_in, cash_out, game="NLH", start_time=None, notes=None):
    conn.execute(
        "INSERT INTO sessions (date, venue, game, stakes, start_time, hours, buy_in, cash_out, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (date, venue, game, stakes, start_time, float(hours), float(buy_in), float(cash_out), notes or None),
    )


def cmd_init(conn, _args):
    count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    if count:
        print(f"poker.db already has {count} session(s); nothing seeded.")
        return
    if not CSV_PATH.exists():
        print("poker.db created, sessions.csv not found, nothing seeded.")
        return
    with CSV_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        insert(conn, r["date"], r["venue"], r["stakes"], r["hours"], r["buy_in"], r["cash_out"],
               game=r.get("game") or "NLH", start_time=r.get("start_time") or None, notes=r.get("notes") or None)
    conn.commit()
    print(f"poker.db created, seeded {len(rows)} session(s) from sessions.csv.")


def cmd_add(conn, a):
    insert(conn, a.date, a.venue, a.stakes, a.hours, a.buy_in, a.cash_out,
           game=a.game, start_time=a.start, notes=a.notes)
    conn.commit()
    print("added.")


def cmd_list(conn, _args):
    rows = conn.execute("SELECT * FROM sessions ORDER BY date, id").fetchall()
    if not rows:
        print("no sessions.")
        return
    print(f"{'id':>3} {'date':10} {'venue':28} {'game':5} {'stakes':6} {'hrs':>5} {'buy_in':>8} {'cash_out':>8} {'net':>8}")
    for r in rows:
        print(f"{r['id']:>3} {r['date']:10} {r['venue'][:28]:28} {r['game']:5} {r['stakes']:6} "
              f"{r['hours']:>5.1f} {r['buy_in']:>8.0f} {r['cash_out']:>8.0f} {r['net']:>8.0f}")


def cmd_stats(conn, _args):
    r = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(hours),0) hours, COALESCE(SUM(net),0) net, "
        "SUM(CASE WHEN net > 0 THEN 1 ELSE 0 END) wins FROM sessions"
    ).fetchone()
    if not r["n"]:
        print("no sessions.")
        return
    per_hour = r["net"] / r["hours"] if r["hours"] else 0.0
    print(f"sessions: {r['n']}\nwinning sessions: {r['wins']}\nhours: {r['hours']:.1f}\n"
          f"net: {r['net']:+.0f}\nper hour: {per_hour:+.2f}")


def fmt(v):
    """CSV cell: blank for NULL, whole floats without a trailing .0."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return v


def cmd_export(conn, _args):
    rows = conn.execute("SELECT * FROM sessions ORDER BY date, id").fetchall()
    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: fmt(r[c]) for c in CSV_COLUMNS})
    print(f"wrote {len(rows)} session(s) to sessions.csv.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    a = sub.add_parser("add")
    for name in ("date", "venue", "stakes", "hours", "buy_in", "cash_out"):
        a.add_argument(name)
    a.add_argument("--game", default="NLH")
    a.add_argument("--start", default=None, help="HH:MM")
    a.add_argument("--notes", default=None)
    a.set_defaults(fn=cmd_add)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    sub.add_parser("export").set_defaults(fn=cmd_export)
    args = p.parse_args(argv)
    try:
        conn = connect()
        args.fn(conn, args)
    except (sqlite3.Error, ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
