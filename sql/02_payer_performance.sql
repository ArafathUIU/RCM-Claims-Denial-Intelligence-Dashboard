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
