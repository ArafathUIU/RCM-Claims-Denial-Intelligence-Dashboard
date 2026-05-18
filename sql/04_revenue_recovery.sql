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
