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

-- -----------------------------------------------------------
-- 1.3 Monthly Denied $ and Recovery $
-- -----------------------------------------------------------
-- Denial rate alongside total denied and recovered dollar amounts.
SELECT
    strftime('%Y-%m', service_date) AS year_month,
    COUNT(*)                        AS total_claims,
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(denied_amount), 2)    AS total_denied_amount,
    ROUND(SUM(recovered_amount), 2) AS total_recovered_amount,
    ROUND(SUM(denied_amount) - SUM(recovered_amount), 2) AS net_unrecovered
FROM claims
GROUP BY strftime('%Y-%m', service_date)
ORDER BY year_month;

-- -----------------------------------------------------------
-- 1.4 Quarterly Denial Summary
-- -----------------------------------------------------------
-- Aggregated by quarter for higher-level trend analysis.
SELECT
    strftime('%Y', service_date) || '-Q' || ((CAST(strftime('%m', service_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
    COUNT(*)                                                                   AS total_claims,
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END)                    AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(denied_amount), 2)                                               AS total_denied,
    ROUND(SUM(recovered_amount), 2)                                            AS total_recovered,
    ROUND(100.0 * SUM(recovered_amount) / NULLIF(SUM(denied_amount), 0), 2)   AS recovery_rate_pct
FROM claims
GROUP BY quarter
ORDER BY quarter;
