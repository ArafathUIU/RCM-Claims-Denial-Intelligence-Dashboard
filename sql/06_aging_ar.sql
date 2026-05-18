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

-- -----------------------------------------------------------
-- 6.3 Average Aging Days by Payer
-- -----------------------------------------------------------
-- Which payers take the longest to resolve denials?
SELECT
    p.payer_name,
    p.payer_type,
    COUNT(*)                                    AS denied_claims,
    ROUND(AVG(c.aging_days), 1)                 AS avg_aging_days,
    ROUND(SUM(c.denied_amount), 2)              AS total_denied,
    ROUND(SUM(c.denied_amount) - SUM(c.recovered_amount), 2) AS outstanding_ar
FROM claims c
JOIN payers p ON c.payer_id = p.payer_id
WHERE c.claim_status != 'Paid'
GROUP BY p.payer_name
ORDER BY avg_aging_days DESC;

-- -----------------------------------------------------------
-- 6.4 Average Aging Days by Department
-- -----------------------------------------------------------
-- Which clinical departments have the most aged denied claims?
SELECT
    pr.department,
    COUNT(*)                                    AS denied_claims,
    ROUND(AVG(c.aging_days), 1)                 AS avg_aging_days,
    ROUND(SUM(c.denied_amount), 2)              AS total_denied,
    ROUND(SUM(c.denied_amount) - SUM(c.recovered_amount), 2) AS outstanding_ar
FROM claims c
JOIN providers pr ON c.provider_id = pr.provider_id
WHERE c.claim_status != 'Paid'
GROUP BY pr.department
ORDER BY avg_aging_days DESC;
