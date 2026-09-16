"""Three production incidents, at three genuinely different difficulties.

Synthetic, and deliberately from a delivery team's world rather than a textbook.
The difficulty gap between them is the whole experiment: if all three were easy,
every model would look identical and there would be nothing to decide.
"""

SIMPLE = """\
[P4] Disk usage alert on build-agent-07: /var/log at 81% (threshold 80%).
No build failures. Log rotation ran normally at 03:00."""

MODERATE = """\
[P2] Checkout API p99 latency 1.8s -> 6.4s over 40 minutes, error rate 0.3% -> 2.1%.
Deploy of payments-svc v4.12 went out 55 minutes ago. DB connection pool at 94% of max.
Two other services share that pool. No alerts from the payment provider."""

COMPLEX = """\
[P1] Order totals wrong for a subset of EU customers since the 14th.
Finance reports 0.4% of orders under-charged, avg -4.30 EUR; support has 31 tickets.
Three changes landed on the 14th: a tax-rules update, a currency-rounding library bump
(2.1.0 -> 3.0.0), and a caching layer in front of the pricing service.
The rounding library changelog mentions "banker's rounding is now the default".
The cache has a 6-hour TTL. Staging did not reproduce it; staging uses a fixed FX rate.
Rollback of the tax-rules update alone did not fix it."""
