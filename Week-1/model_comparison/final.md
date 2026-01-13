# SQL Query Evaluation - Comparison

| Criteria | Gemini 3 | DeepSeek v3.2 | Claude Opus | GPT-5 |
|----------|----------|---------------|-------------|-------|
| **QUERY 1: TOTAL REVENUE PER USER** |
| Correctness | WRONG (INNER JOIN) | Correct | Correct | Mostly correct |
| Join Type | INNER JOIN (excludes users) | LEFT JOIN | LEFT JOIN | LEFT JOIN |
| NULL Handling | None | COALESCE | COALESCE | Missing COALESCE |
| Filter Placement | WHERE clause | ON clause | ON clause | ON clause |
| Q1 Score | **2/10** | **9/10** | **10/10** | **7/10** |
| **QUERY 2: USERS WITHOUT ORDERS** |
| Correctness | Correct | Correct | Correct | Correct |
| Approach | LEFT JOIN + NULL | LEFT JOIN + NULL | LEFT JOIN + NOT EXISTS alt | LEFT JOIN + NULL |
| Additional Features | Basic | Orders by created_at | Alternative method + reasoning | Basic |
| Performance Notes | None | Optimizer efficiency noted | Large table scenario discussed | None |
| Q2 Score | **7/10** | **8/10** | **10/10** | **7/10** |
| **QUERY 3: TOP 5 USERS (LAST 30 DAYS)** |
| Correctness | Correct | Correct | Correct | Correct |
| Approach | Direct INNER JOIN | CTE + LEFT JOIN | Direct INNER JOIN | Direct INNER JOIN |
| Complexity Level | Simple | Over-engineered | Simple | Simple |
| Edge Cases | None | NULLS LAST handling | <5 users & tie-breaking docs | None |
| DB Portability | Single syntax | Single syntax | Multi-DB notes | Single syntax |
| Q3 Score | **7/10** | **6/10** | **10/10** | **8/10** |
| **QUERY 4: ABOVE AVERAGE ORDER VALUE** |
| Correctness | Correct | Correct | Correct | Correct |
| Approach | Subquery in HAVING | CTE + CROSS JOIN | CTE + CROSS JOIN + alt | CTE + CROSS JOIN |
| Performance | Re-executes subquery | CTE evaluates once | CTE + tradeoff discussion | CTE evaluates once |
| Output Transparency | Basic fields | Includes order count | Shows both averages | Basic fields |
| Alternatives | None | None | Subquery version included | None |
| Q4 Score | **6/10** | **9/10** | **10/10** | **8/10** |
| **OVERALL ASSESSMENT** |
| Total Correctness | 3/4 queries | 4/4 queries | 4/4 queries | 4/4 queries |
| Code Quality | Simple but flawed | Good, over-engineered | Excellent | Clean & concise |
| Documentation | Basic | Good | Comprehensive | Good |
| Performance Awareness | Low | Medium | High | Medium |
| Production Ready | No | Mostly | Yes | Mostly |
| Index Recommendations | None | None | Yes | None |
| Portability Notes | None | None | PostgreSQL/MySQL/SQL Server | None |
| Edge Case Handling | Minimal | Good | Excellent | Basic |
| Alternative Solutions | None | None | Yes (2 queries) | None |
| **FINAL SCORES** |
| Overall Score | **55/100** | **80/100** | **95/100** | **82/100** |
| Rank | 4th | 3rd | 1st | 2nd |
| Best For | Not recommended | Solid with safety checks | Production & learning | Quick clean code |
| Critical Issue | Q1 fundamentally wrong | Over-engineering Q3 | None | Minor NULL handling |
| Recommendation | **AVOID** | Use with review | **RECOMMENDED** | Good choice |