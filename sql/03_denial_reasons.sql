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

-- -----------------------------------------------------------
-- 3.2 Denial Reason Financial Impact
-- -----------------------------------------------------------
-- Frequency + total denied $, avg $ per denial, and recovery $ by reason.
SELECT
    c.reason_code,
    dr.reason_description,
    dr.category,
    COUNT(*)                      AS denial_count,
    ROUND(SUM(c.denied_amount), 2) AS total_denied,
    ROUND(AVG(c.denied_amount), 2) AS avg_denied_per_claim,
    ROUND(SUM(c.recovered_amount), 2) AS total_recovered,
    ROUND(100.0 * SUM(c.recovered_amount) / NULLIF(SUM(c.denied_amount), 0), 2) AS recovery_rate_pct
FROM claims c
JOIN denial_reasons dr ON c.reason_code = dr.reason_code
WHERE c.claim_status != 'Paid'
  AND c.reason_code != ''
GROUP BY c.reason_code
ORDER BY total_denied DESC;

-- -----------------------------------------------------------
-- 3.3 Pareto Analysis (Cumulative Impact)
-- -----------------------------------------------------------
-- Running total of denial % to identify the vital few reasons.
-- Uses window functions to calculate cumulative percentage.
SELECT
    c.reason_code,
    dr.reason_description,
    COUNT(*)                      AS denial_count,
    ROUND(SUM(c.denied_amount), 2) AS total_denied,
    ROUND(100.0 * SUM(c.denied_amount) / SUM(SUM(c.denied_amount)) OVER (), 2) AS pct_of_total,
    ROUND(100.0 * SUM(SUM(c.denied_amount)) OVER (ORDER BY SUM(c.denied_amount) DESC)
          / SUM(SUM(c.denied_amount)) OVER (), 2) AS cumulative_pct
FROM claims c
JOIN denial_reasons dr ON c.reason_code = dr.reason_code
WHERE c.claim_status != 'Paid'
  AND c.reason_code != ''
GROUP BY c.reason_code
ORDER BY total_denied DESC;
