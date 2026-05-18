-- ============================================================
-- 05 PROVIDER & DEPARTMENT DRILL-DOWN
-- ============================================================
-- Identifies which providers and departments face the most
-- denials and lose the most revenue.
-- ============================================================

-- -----------------------------------------------------------
-- 5.1 Denial Counts by Provider
-- -----------------------------------------------------------
-- Which providers have the most denied claims?
SELECT
    pr.provider_name,
    pr.department,
    COUNT(*)                                                   AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)  AS denied_claims
FROM claims c
JOIN providers pr ON c.provider_id = pr.provider_id
GROUP BY pr.provider_name
ORDER BY denied_claims DESC;
