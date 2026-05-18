-- ============================================================
-- 02 PAYER PERFORMANCE ANALYSIS
-- ============================================================
-- Compares denial rates, denied amounts, and recovery
-- performance across insurance payers.
-- ============================================================

-- -----------------------------------------------------------
-- 2.1 Denial Counts by Payer
-- -----------------------------------------------------------
-- Total and denied claim counts per payer.
SELECT
    p.payer_name,
    COUNT(*)                                                   AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)  AS denied_claims
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.payer_name
ORDER BY denied_claims DESC;

-- -----------------------------------------------------------
-- 2.2 Denial Rate % and Denied $ by Payer
-- -----------------------------------------------------------
-- Denial rate, average $ denied per denied claim, total denied $.
SELECT
    p.payer_name,
    p.payer_type,
    COUNT(*)                                                   AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)  AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(c.denied_amount), 2)                             AS total_denied_amount,
    ROUND(AVG(CASE WHEN c.claim_status != 'Paid' THEN c.denied_amount END), 2) AS avg_denied_per_claim
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.payer_name
ORDER BY denial_rate_pct DESC;

-- -----------------------------------------------------------
-- 2.3 Recovery Rate by Payer
-- -----------------------------------------------------------
-- How much of denied revenue is recovered through appeals, per payer.
SELECT
    p.payer_name,
    COUNT(*)                                                            AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)           AS denied_claims,
    SUM(CASE WHEN c.claim_status = 'Recovered' THEN 1 ELSE 0 END)       AS recovered_claims,
    SUM(CASE WHEN c.claim_status = 'Written Off' THEN 1 ELSE 0 END)     AS written_off_claims,
    ROUND(SUM(c.denied_amount), 2)                                      AS total_denied,
    ROUND(SUM(c.recovered_amount), 2)                                   AS total_recovered,
    ROUND(100.0 * SUM(c.recovered_amount) / NULLIF(SUM(c.denied_amount), 0), 2) AS recovery_rate_pct
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.payer_name
ORDER BY recovery_rate_pct DESC;

-- -----------------------------------------------------------
-- 2.4 Appeal Rate by Payer
-- -----------------------------------------------------------
-- What % of denied claims get appealed, and appeal success rate.
SELECT
    p.payer_name,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)                   AS total_denied,
    SUM(c.appeal_flag)                                                           AS appeals_filed,
    ROUND(100.0 * SUM(c.appeal_flag) / NULLIF(SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END), 0), 2) AS appeal_rate_pct,
    SUM(CASE WHEN c.claim_status = 'Recovered' THEN 1 ELSE 0 END)                AS appeals_won,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'Recovered' THEN 1 ELSE 0 END) / NULLIF(SUM(c.appeal_flag), 0), 2) AS appeal_success_pct
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
GROUP BY p.payer_name
ORDER BY appeal_rate_pct DESC;
