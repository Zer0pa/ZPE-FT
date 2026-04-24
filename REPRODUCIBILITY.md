# Reproducibility

## Canonical Inputs

The retained repo-native corpus and contract inputs are:

- `data/ohlcv/*.csv.gz` - bounded delayed-feed OHLCV proxy corpus retained in git.
- `data/ticks/aapl_dukascopy_tick_20d_1h.csv.gz`
- `data/ticks/e-sandp-500_dukascopy_tick_20d_1h.csv.gz`
- `data/ticks/eurusd_dukascopy_tick_20d_1h.csv.gz`
- `proofs/phase06_inputs/series_gap_matrix.csv` - declared missing-input surface for the blocked Phase 06 benchmark.
- `docs/examples/phase06_benchmark_request.example.json` - retained request contract for the Phase 06 benchmark lane.

## Golden-Bundle Hash

Will be populated by the `receipt-bundle.yml` workflow in Wave 3.

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

- Python 3.11+ base package from the repo root.
- Python 3.11+ with the optional native helper via `python -m pip install -e ".[native]"` and `cd core && maturin develop --release`.
