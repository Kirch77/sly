Add importing from my bank's CSV exports. I have two banks:
- Bank A: `Date,Description,Amount` (dates like 2026-03-14, spending is negative)
- Bank B: `Transaction Date;Payee;Debit;Credit` (semicolons, dates like 14/03/2026)

Don't import the same transaction twice. Sample exports are in `data/`.
