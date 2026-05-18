-- RCM Claims Denial Intelligence Dashboard - Database Schema
-- SQLite

-- ============================================================
-- PAYERS
-- ============================================================
CREATE TABLE IF NOT EXISTS payers (
    payer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    payer_name  TEXT NOT NULL UNIQUE,
    payer_type  TEXT NOT NULL CHECK (payer_type IN ('Commercial', 'Government', 'Managed Care')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- DENIAL REASONS
-- ============================================================
CREATE TABLE IF NOT EXISTS denial_reasons (
    reason_code        TEXT PRIMARY KEY,
    reason_description TEXT NOT NULL,
    category           TEXT NOT NULL CHECK (category IN (
        'Authorization', 'Medical Necessity', 'Coding', 'Timely Filing',
        'Eligibility', 'Duplicate', 'Non-Covered', 'Coordination of Benefits', 'Other'
    )),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- PROVIDERS
-- ============================================================
CREATE TABLE IF NOT EXISTS providers (
    provider_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL UNIQUE,
    department    TEXT NOT NULL CHECK (department IN (
        'Emergency Medicine', 'Cardiology', 'Orthopedics', 'Oncology',
        'Neurology', 'General Surgery', 'Radiology', 'Laboratory',
        'Physical Therapy', 'Internal Medicine', 'Pediatrics', 'OB/GYN'
    )),
    npi           TEXT UNIQUE,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- CLAIMS (main fact table)
-- ============================================================
CREATE TABLE IF NOT EXISTS claims (
    claim_id            TEXT PRIMARY KEY,
    patient_id          TEXT NOT NULL,
    provider_id         INTEGER NOT NULL,
    payer_id            INTEGER NOT NULL,
    reason_code         TEXT,
    service_date        DATE NOT NULL,
    billing_date        DATE NOT NULL,
    payment_date        DATE,
    denial_date         DATE,
    recovery_date       DATE,
    billed_amount       REAL NOT NULL CHECK (billed_amount > 0),
    allowed_amount      REAL NOT NULL CHECK (allowed_amount >= 0),
    denied_amount       REAL NOT NULL DEFAULT 0 CHECK (denied_amount >= 0),
    recovered_amount    REAL NOT NULL DEFAULT 0 CHECK (recovered_amount >= 0),
    claim_status        TEXT NOT NULL CHECK (claim_status IN (
        'Paid', 'Denied', 'Appealed', 'Recovered', 'Written Off'
    )),
    appeal_flag         INTEGER NOT NULL DEFAULT 0 CHECK (appeal_flag IN (0, 1)),
    aging_days          INTEGER NOT NULL DEFAULT 0 CHECK (aging_days >= 0),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    FOREIGN KEY (payer_id) REFERENCES payers(payer_id),
    FOREIGN KEY (reason_code) REFERENCES denial_reasons(reason_code)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_claims_payer        ON claims(payer_id);
CREATE INDEX IF NOT EXISTS idx_claims_provider     ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_reason       ON claims(reason_code);
CREATE INDEX IF NOT EXISTS idx_claims_status       ON claims(claim_status);
CREATE INDEX IF NOT EXISTS idx_claims_denial_date  ON claims(denial_date);
CREATE INDEX IF NOT EXISTS idx_claims_service_dt   ON claims(service_date);
CREATE INDEX IF NOT EXISTS idx_claims_billing_dt   ON claims(billing_date);
CREATE INDEX IF NOT EXISTS idx_claims_aging        ON claims(aging_days DESC);
CREATE INDEX IF NOT EXISTS idx_claims_payer_status ON claims(payer_id, claim_status);
CREATE INDEX IF NOT EXISTS idx_claims_provider_dt  ON claims(provider_id, service_date);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

CREATE VIEW IF NOT EXISTS v_claim_aging AS
SELECT
    claim_id,
    claim_status,
    CASE
        WHEN aging_days <= 30  THEN '0-30 days'
        WHEN aging_days <= 60  THEN '31-60 days'
        WHEN aging_days <= 90  THEN '61-90 days'
        ELSE '90+ days'
    END AS aging_bucket,
    aging_days,
    denied_amount,
    recovered_amount
FROM claims
WHERE claim_status IN ('Denied', 'Appealed', 'Written Off');

CREATE VIEW IF NOT EXISTS v_denial_summary AS
SELECT
    p.payer_name,
    p.payer_type,
    COUNT(*)                              AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(c.denied_amount), 2)        AS total_denied,
    ROUND(SUM(c.recovered_amount), 2)     AS total_recovered,
    ROUND(100.0 * SUM(c.recovered_amount) / NULLIF(SUM(c.denied_amount), 0), 2) AS recovery_rate_pct
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.payer_name
ORDER BY denial_rate_pct DESC;

CREATE VIEW IF NOT EXISTS v_provider_denials AS
SELECT
    pr.provider_name,
    pr.department,
    COUNT(*)                              AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(c.denied_amount), 2)        AS total_denied,
    ROUND(AVG(c.aging_days), 1)           AS avg_aging_days
FROM claims c
JOIN providers pr ON c.provider_id = pr.provider_id
GROUP BY pr.provider_name
ORDER BY denial_rate_pct DESC;

CREATE VIEW IF NOT EXISTS v_monthly_trends AS
SELECT
    strftime('%Y-%m', service_date) AS year_month,
    COUNT(*)                        AS total_claims,
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(denied_amount), 2)    AS total_denied,
    ROUND(SUM(recovered_amount), 2) AS total_recovered
FROM claims
GROUP BY year_month
ORDER BY year_month;
