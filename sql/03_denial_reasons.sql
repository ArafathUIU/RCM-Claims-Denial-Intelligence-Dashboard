-- ============================================================
-- 03 DENIAL REASON ANALYSIS
-- ============================================================
-- Identifies the most common denial reasons, their
-- financial impact, and category-level patterns.
-- ============================================================

-- -----------------------------------------------------------
-- 3.1 Denial Reason Frequency
-- -----------------------------------------------------------
-- Count of denied claims per reason code.
SELECT
    c.reason_code,
    dr.reason_description,
    COUNT(*) AS denial_count
FROM claims c
JOIN denial_reasons dr ON c.reason_code = dr.reason_code
WHERE c.claim_status != 'Paid'
  AND c.reason_code != ''
GROUP BY c.reason_code
ORDER BY denial_count DESC;
