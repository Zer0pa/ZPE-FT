# ZPE Finance Integration Pattern

## Scope

This note records the actual integration and packaging pattern visible in the
accessible local repos on 2026-03-21:

- Finance repo: `/Users/Zer0pa/ZPE/ZPE FT/zpe-finance`
- IMC repo: `/Users/Zer0pa/ZPE/ZPE-IMC`
- Robotics repo: `/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`

It is written to prevent plan drift. Where the closure brief assumes an
existing shared Rust/PyO3 pattern, this document records what is actually on
disk.

## Executive Truth

1. `zpe-finance` is currently a `setuptools` Python package with an optional,
   very small standalone PyO3 helper crate under `core/`.
2. The accessible `ZPE-IMC` repo does not expose a shared PyO3 finance-ready
   Rust core. Its live package surface is also `setuptools`-based Python, with
   a separate WASM tokenizer crate.
3. The accessible robotics workstream template is the inner repo
   `/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`, and it is also
   `setuptools`-based Python. It does not provide a released `maturin` or PyO3
   wheel pattern for finance to mirror.
4. The current cross-lane reusable pattern is therefore:
   Python package first, optional helper-native code second, explicit proof and
   receipt surfaces, and Comet project constants wired per lane.

## Finance Pattern

### Package layout

- Build backend: `setuptools.build_meta`
- Package root: `python/zpe_finance`
- Current package metadata source: `pyproject.toml`

### Finance build facts

- `pyproject.toml` uses `setuptools>=68` and `wheel`
- `requires-python = ">=3.11"`
- Editable installs are supported today via `pip install -e .`
- There is no current repo-level `maturin` build contract in `pyproject.toml`

### Finance Rust usage

- Rust crate path: `core/`
- Crate name: `zpe_finance_rs`
- Current exported Rust functions:
  - `version`
  - `pack_nibbles`
  - `unpack_nibbles`
  - `find_subsequence`
  - `fnv1a64`
- The finance Rust crate is a helper crate, not a shared IMC dependency
- `python/zpe_finance/rust_bridge.py` already provides deterministic Python
  fallbacks if the extension is absent

### Finance public API today

`python/zpe_finance/__init__.py` currently exports:

- `encode_ohlcv`
- `decode_ohlcv`
- `encode_ticks`
- `decode_ticks`
- `raw_bytes_ohlcv`
- `raw_bytes_tick`
- `PatternIndex`
- corpus-loading helpers
- Alpaca helpers

There is not yet a repo-native top-level `search_motif` or `compress_df`
export matching the closure brief.

## ZPE-IMC Pattern

### Accessible live package

The live package surface under `/Users/Zer0pa/ZPE/ZPE-IMC/v0.0/code` is:

- Build backend: `setuptools.build_meta`
- Package name: `zpe-multimodal`
- Python package: `zpe_multimodal`

### Exposed API shape

From `zpe_multimodal/__init__.py`, the accessible top-level exports are Python
symbols such as:

- `encode`
- `decode`
- `IMCEncoder`
- `IMCDecoder`
- `ZPETokenizer`

### Native code shape

- There is a Rust crate at `v0.0/code/rust/wasm_codec`
- That crate is WASM-oriented, using `wasm-bindgen`
- It is not a PyO3 crate
- It is not wired as the Python package build backend

### Consequence

The accessible IMC repo does not provide an existing packaged PyO3 shared core
that `zpe-finance` can depend on in the same way the brief assumes.

## Robotics Workstream Pattern

### Authoritative robotics repo

The usable robotics template is the inner repo:

- `/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`

The outer robotics workspace is not the source-of-truth code boundary.

### Robotics package structure

- Build backend: `setuptools.build_meta`
- Package name: `zpe-motion-kernel`
- Source layout: `src/zpe_robotics`
- Editable install path in docs:
  - `python -m pip install -e ".[dev,netnew]"`

### Robotics native-code status

- No `Cargo.toml` or PyO3 package build exists inside the inner robotics repo
- The accessible robotics release candidate is Python-first
- Robotics proof surfaces explicitly discuss a "no-rust-yet" result in current
  operations receipts rather than a released PyO3 wheel pipeline

### Robotics install UX

Per `README.md`, the user flow is:

1. Create a virtualenv
2. Upgrade `pip setuptools wheel`
3. `pip install -e ".[dev,netnew]"`
4. Run `pytest`

Immediate import surface:

- `from zpe_robotics import ZPBotCodec, REFERENCE_ROUNDTRIP_SHA256`

### Robotics Comet pattern

Robotics operational artifacts show a lane-specific Comet project, not a
generic shared one:

- workspace: `zer0pa`
- project: `zpe-robotics`
- experiment URLs are stored in proof artifacts and receipts

The visible pattern is: run work, record Comet URL in the repo evidence, and
keep the code package decoupled from board/status claims.

## Tracking Pattern For Finance

Finance already contains its own repo-native Comet adapter:

- file: `python/zpe_finance/comet_logging.py`
- default workspace: `zer0pa`
- default project: `zpe-ft`

Finance proof artifacts already confirm this lane-specific project:

- `https://www.comet.com/zer0pa/zpe-ft/...`

This is the canonical observability pattern visible in this workstream:

1. Lane-local defaults in code
2. Environment-variable override support
3. Status JSON written back into repo artifacts
4. Receipts and proof bundles, not prose, carry the decisive experiment URL

### Dual-tracker pattern recovered from robotics

The accessible robotics lane also contains the orchestrator-style dual-tracker
surface in `src/zpe_robotics/telemetry.py`:

- classic project default: `zpe-robotics`
- Opik project default: `zpe-robotics`
- Opik host default: `https://www.comet.com/opik/api`
- creation rule: verify-or-create the classic Comet and Opik projects first,
  then instantiate adapter objects
- runtime rule: degrade cleanly to inactive adapters when credentials or SDKs
  are unavailable

To keep finance aligned with that pattern, finance now has a matching lane-local
tracking bundle at `python/zpe_finance/tracking.py` with:

- classic project default: `zpe-ft`
- Opik project default: `zpe-ft`
- Opik host default: `https://www.comet.com/opik/api`
- the same verify/create -> adapter -> bundle flow as the robotics lane

This restores the canonical tracker-instantiation pattern without claiming that
the current finance scripts have already promoted Opik to an authority gate.

## Binary Contract Status

- Finance has a local packet contract and `.zpfin` surface under
  `docs/specs/ZPFIN_SPEC.md`
- The accessible IMC repo does not expose a matching shared `.zpfin` packet
  contract that finance is already consuming
- Any statement that the current finance package already follows an
  IMC-shared `.zpfin` binary dependency chain would be inaccurate

## Ratified Conclusion

The accessible local evidence does not support the claim that finance can close
by simply wiring into an already-established robotics-style PyO3 package
pattern from IMC.

The real pattern today is:

- package and proof surfaces are Python-first
- helper-native code is optional and lane-local
- Comet projects are lane-specific and recorded in repo artifacts
- source-of-truth boundaries are inner repos, not outer workspaces

Any finance closure plan must therefore choose one of two honest paths:

1. Continue on the existing Python-first package and proof surface, using the
   current helper crate only where it already adds value.
2. Design and implement a genuinely new shared Rust-core pattern, knowing that
   this is net-new engineering in this workspace rather than adoption of an
   already-shipped template.
