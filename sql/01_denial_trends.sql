-- ============================================================
-- 01 DENIAL TRENDS OVER TIME
-- ============================================================
-- Analyzes how denial rates and denied amounts trend
-- month-over-month and quarter-over-quarter.
-- ============================================================

-- -----------------------------------------------------------
-- 1.1 Monthly Denial Counts
-- -----------------------------------------------------------
-- Total claims, denied claims, and raw denial counts per month.
SELECT
    strftime('%Y-%m', service_date) AS year_month,
    COUNT(*)                        AS total_claims,
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims
FROM claims
GROUP BY strftime('%Y-%m', service_date)
ORDER BY year_month;

-- -----------------------------------------------------------
-- 1.2 Monthly Denial Rate %
-- -----------------------------------------------------------
-- Denial count + denial rate as a percentage per month.
SELECT
    strftime('%Y-%m', service_date) AS year_month,
    COUNT(*)                        AS total_claims,
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct
FROM claims
GROUP BY strftime('%Y-%m', service_date)
ORDER BY year_month;
