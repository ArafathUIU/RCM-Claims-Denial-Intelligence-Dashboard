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
