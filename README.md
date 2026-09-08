# Robby-D-Poker

Live poker session log.

## sessions.csv

One row per session.

| Column | Meaning |
|---|---|
| date | Session date, YYYY-MM-DD |
| venue | Card room name |
| game | NLH, PLO, etc. |
| stakes | Blinds, e.g. 1/3 |
| start_time | Local start time, 24h HH:MM |
| hours | Hours played |
| buy_in | Total money put on the table |
| cash_out | Money taken off the table |
| net | cash_out minus buy_in |
| notes | Free text, optional |

## SQLite database

`poker.db` is the primary store. `sessions.csv` is an export of it, kept in git so the data is readable without tools. Schema is in `schema.sql`.

Requires Python 3 only (standard library).

```bash
python3 poker.py init      # create poker.db, seed from sessions.csv if the db is empty
python3 poker.py add 2026-09-07 "Thunder Valley Casino Resort" 1/3 3 300 0 --start 12:45
python3 poker.py list
python3 poker.py stats     # sessions, wins, hours, net, net per hour
python3 poker.py export    # rewrite sessions.csv from poker.db
```

`add` arguments in order: date, venue, stakes, hours, buy_in, cash_out. Options: `--game` (default NLH), `--start HH:MM`, `--notes`.
Run `export` after `add` so the CSV stays in sync before committing.
