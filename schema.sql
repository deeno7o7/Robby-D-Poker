CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,           -- YYYY-MM-DD
    venue       TEXT    NOT NULL,
    game        TEXT    NOT NULL DEFAULT 'NLH',
    stakes      TEXT    NOT NULL,           -- e.g. 1/3
    start_time  TEXT,                       -- HH:MM, 24h local
    hours       REAL    NOT NULL CHECK (hours >= 0),
    buy_in      REAL    NOT NULL CHECK (buy_in >= 0),
    cash_out    REAL    NOT NULL CHECK (cash_out >= 0),
    net         REAL    GENERATED ALWAYS AS (cash_out - buy_in) STORED,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
