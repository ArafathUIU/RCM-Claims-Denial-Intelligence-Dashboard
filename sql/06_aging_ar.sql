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
