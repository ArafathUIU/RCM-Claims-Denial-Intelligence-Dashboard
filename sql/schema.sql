-- RCM Claims Denial Intelligence Dashboard - Database Schema
-- SQLite

-- ============================================================
-- PAYERS
-- ============================================================
CREATE TABLE IF NOT EXISTS payers (
    payer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    payer_name  TEXT NOT NULL UNIQUE,
    payer_type  TEXT NOT NULL CHECK (payer_type IN ('Commercial', 'Government', 'Managed Care'))
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
    ))
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
    npi           TEXT UNIQUE
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
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    FOREIGN KEY (payer_id) REFERENCES payers(payer_id),
    FOREIGN KEY (reason_code) REFERENCES denial_reasons(reason_code)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_claims_payer      ON claims(payer_id);
CREATE INDEX IF NOT EXISTS idx_claims_provider   ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_reason     ON claims(reason_code);
CREATE INDEX IF NOT EXISTS idx_claims_status     ON claims(claim_status);
CREATE INDEX IF NOT EXISTS idx_claims_denial_date ON claims(denial_date);
CREATE INDEX IF NOT EXISTS idx_claims_service_dt ON claims(service_date);
