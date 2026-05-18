-- ============================================================
-- 04 REVENUE RECOVERY ANALYSIS
-- ============================================================
-- Tracks appeal success rates, recovered vs written-off
-- amounts, and recovery performance over time.
-- ============================================================

-- -----------------------------------------------------------
-- 4.1 Appeal Counts and Success Rate
-- -----------------------------------------------------------
-- How many denied claims get appealed, and what % succeed?
SELECT
    SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END)                                AS total_denied,
    SUM(appeal_flag)                                                                        AS appeals_filed,
    ROUND(100.0 * SUM(appeal_flag) / NULLIF(SUM(CASE WHEN claim_status != 'Paid' THEN 1 ELSE 0 END), 0), 2) AS appeal_rate_pct,
    SUM(CASE WHEN claim_status = 'Recovered' THEN 1 ELSE 0 END)                             AS appeals_won,
    SUM(CASE WHEN claim_status = 'Written Off' THEN 1 ELSE 0 END)                           AS appeals_lost,
    ROUND(100.0 * SUM(CASE WHEN claim_status = 'Recovered' THEN 1 ELSE 0 END)
          / NULLIF(SUM(appeal_flag), 0), 2)                                                 AS appeal_success_pct
FROM claims;

-- -----------------------------------------------------------
-- 4.2 Revenue Recovery: $ Recovered vs $ Written Off
-- -----------------------------------------------------------
-- Total financial outcome of denied claims.
SELECT
    ROUND(SUM(denied_amount), 2)                                               AS total_denied,
    ROUND(SUM(recovered_amount), 2)                                            AS total_recovered,
    ROUND(SUM(denied_amount) - SUM(recovered_amount), 2)                      AS total_written_off,
    ROUND(100.0 * SUM(recovered_amount) / NULLIF(SUM(denied_amount), 0), 2)  AS recovery_rate_pct
FROM claims
WHERE claim_status != 'Paid';

-- -----------------------------------------------------------
-- 4.3 Average Days to Recover
-- -----------------------------------------------------------
-- How long does it take (from denial date) to recover revenue?
SELECT
    ROUND(AVG(julianday(recovery_date) - julianday(denial_date)), 1) AS avg_days_to_recover,
    MIN(julianday(recovery_date) - julianday(denial_date))           AS min_days,
    MAX(julianday(recovery_date) - julianday(denial_date))           AS max_days,
    COUNT(*)                                                          AS recovered_claims
FROM claims
WHERE claim_status = 'Recovered'
  AND recovery_date != ''
  AND denial_date != '';

-- -----------------------------------------------------------
-- 4.4 Recovery Days by Claim Amount Bucket
-- -----------------------------------------------------------
-- Do larger denied amounts take longer to recover?
SELECT
    CASE
        WHEN denied_amount < 1000 THEN '< $1K'
        WHEN denied_amount < 5000 THEN '$1K-$5K'
        WHEN denied_amount < 10000 THEN '$5K-$10K'
        ELSE '> $10K'
    END AS amount_bucket,
    COUNT(*)                                                           AS claim_count,
    ROUND(AVG(julianday(recovery_date) - julianday(denial_date)), 1)  AS avg_recovery_days,
    ROUND(SUM(recovered_amount), 2)                                    AS total_recovered
FROM claims
WHERE claim_status = 'Recovered'
  AND recovery_date != ''
  AND denial_date != ''
GROUP BY amount_bucket
ORDER BY avg_recovery_days;

-- -----------------------------------------------------------
-- 4.5 Recovery Rate by Denial Reason
-- -----------------------------------------------------------
-- Which denial reasons have the best/worst recovery rates?
SELECT
    dr.reason_description,
    COUNT(*)                                                            AS denied_count,
    SUM(CASE WHEN c.claim_status = 'Recovered' THEN 1 ELSE 0 END)       AS recovered_count,
    ROUND(SUM(c.denied_amount), 2)                                      AS total_denied,
    ROUND(SUM(c.recovered_amount), 2)                                   AS total_recovered,
    ROUND(100.0 * SUM(c.recovered_amount) / NULLIF(SUM(c.denied_amount), 0), 2) AS recovery_rate_pct
FROM claims c
JOIN denial_reasons dr ON c.reason_code = dr.reason_code
WHERE c.claim_status != 'Paid'
  AND c.reason_code != ''
GROUP BY dr.reason_description
ORDER BY recovery_rate_pct DESC;

-- -----------------------------------------------------------
-- 4.6 Monthly Recovery Trends
-- -----------------------------------------------------------
-- How much is recovered each month vs how much was denied?
SELECT
    strftime('%Y-%m', COALESCE(c.recovery_date, c.denial_date)) AS year_month,
    COUNT(*)                                                     AS denied_claims,
    SUM(CASE WHEN c.claim_status = 'Recovered' THEN 1 ELSE 0 END) AS recovered_claims,
    ROUND(SUM(c.denied_amount), 2)                               AS total_denied,
    ROUND(SUM(c.recovered_amount), 2)                            AS total_recovered,
    ROUND(100.0 * SUM(c.recovered_amount) / NULLIF(SUM(c.denied_amount), 0), 2) AS recovery_rate_pct
FROM claims c
WHERE c.claim_status != 'Paid'
GROUP BY year_month
ORDER BY year_month;
