-- ============================================================
-- 06 AGING & ACCOUNTS RECEIVABLE ANALYSIS
-- ============================================================
-- Tracks how long denied claims remain unresolved,
-- segmented by aging buckets, payer, and department.
-- ============================================================

-- -----------------------------------------------------------
-- 6.1 Aging Bucket Distribution
-- -----------------------------------------------------------
-- How many denied claims fall into each aging bucket?
SELECT
    CASE
        WHEN aging_days <= 30  THEN '0-30 days'
        WHEN aging_days <= 60  THEN '31-60 days'
        WHEN aging_days <= 90  THEN '61-90 days'
        ELSE '90+ days'
    END AS aging_bucket,
    COUNT(*) AS claim_count
FROM claims
WHERE claim_status != 'Paid'
GROUP BY aging_bucket
ORDER BY MIN(aging_days);

-- -----------------------------------------------------------
-- 6.2 Aging Buckets with Dollar Amounts
-- -----------------------------------------------------------
-- Aging distribution + denied and recovered dollar amounts per bucket.
SELECT
    CASE
        WHEN aging_days <= 30  THEN '0-30 days'
        WHEN aging_days <= 60  THEN '31-60 days'
        WHEN aging_days <= 90  THEN '61-90 days'
        ELSE '90+ days'
    END AS aging_bucket,
    COUNT(*)                         AS claim_count,
    ROUND(SUM(denied_amount), 2)     AS total_denied,
    ROUND(SUM(recovered_amount), 2)  AS total_recovered,
    ROUND(SUM(denied_amount) - SUM(recovered_amount), 2) AS net_outstanding,
    ROUND(AVG(aging_days), 1)        AS avg_aging_days,
    ROUND(SUM(denied_amount) * 100.0 / SUM(SUM(denied_amount)) OVER (), 2) AS pct_of_total_denied
FROM claims
WHERE claim_status != 'Paid'
GROUP BY aging_bucket
ORDER BY MIN(aging_days);
