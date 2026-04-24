# Reproducibility

## Canonical Inputs

- `proofs/reruns/2026-03-19_alpaca_demo_smoke/buyer_exports/spy_1m_20260317_bars.csv`
- `proofs/reruns/2026-03-19_alpaca_demo_smoke/buyer_exports/aapl_quotes_20260317_open_quotes.csv`
- `proofs/artifacts/real_market_benchmarks/minute_30d/fetch_manifest.json`
- `proofs/artifacts/real_market_benchmarks/tick_20_sessions/fetch_manifest.json`
- `proofs/phase06_inputs/series_gap_matrix.csv`

## Golden-Bundle Hash

This field will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
git clone https://github.com/Zer0pa/ZPE-FT.git
cd ZPE-FT
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python - <<'PY'
import zpe_finance
from zpe_finance.rust_bridge import rust_version
print("exports", sorted(zpe_finance.__all__))
print("rust_bridge", rust_version())
PY
```

## Supported Runtimes

- Python 3.11+ package surface
- Optional Rust helper via `python -m pip install -e ".[native]"` and `cd core && maturin develop --release`
- Repo-local proof runners via `python -m pip install -e ".[test,proof]"`
