CREATE TABLE IF NOT EXISTS mutual_funds (
    scheme_code BIGINT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS nav_history (
    scheme_code BIGINT NOT NULL REFERENCES mutual_funds(scheme_code) ON DELETE CASCADE,
    nav_date DATE NOT NULL,
    nav NUMERIC(18, 6) NOT NULL CHECK (nav > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (scheme_code, nav_date)
);

CREATE INDEX IF NOT EXISTS nav_history_scheme_date_desc_idx
    ON nav_history (scheme_code, nav_date DESC);
