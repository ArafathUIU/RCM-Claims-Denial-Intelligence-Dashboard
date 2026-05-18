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

-- -----------------------------------------------------------
-- 5.2 Denial Rate % and Denied $ by Provider
-- -----------------------------------------------------------
-- Providers ranked by denial rate and financial impact.
SELECT
    pr.provider_name,
    pr.department,
    COUNT(*)                                                   AS total_claims,
    SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END)  AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status != 'Paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS denial_rate_pct,
    ROUND(SUM(c.denied_amount), 2)                             AS total_denied,
    ROUND(AVG(CASE WHEN c.claim_status != 'Paid' THEN c.denied_amount END), 2) AS avg_denied_per_claim
FROM claims c
JOIN providers pr ON c.provider_id = pr.provider_id
GROUP BY pr.provider_name
ORDER BY denial_rate_pct DESC;
