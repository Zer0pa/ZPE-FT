# ZPFIN_SPEC

## Version
- Magic: `ZPFN1`
- Version: `1`

## Header Layout (Little Endian)
- `magic`: 5 bytes (`ZPFN1`)
- `version`: u8
- `kind`: u8 (`1` = OHLCV, `2` = tick)
- `flags`: u8
- `count`: u32
- `tick_size`: f64
- `base_tick`: i64
- `base_aux`: i64 (start timestamp)
- `interval_ms`: u32 (OHLCV cadence; 0 for tick)
- `nibble_count`: u32
- `nibble_len`: u32
- `overflow_len`: u32
- `instrument_hash`: u32
- `crc32`: u32 over header-without-crc + nibble + overflow payload

## Payload
- `nibble stream`: packed 4-bit channels.
- `overflow stream`: unsigned varints for escaped signed/unsigned channel values.

## OHLCV Channel Order (5 nibbles per row)
1. `do`: open delta vs previous close (signed)
2. `dc`: close delta vs open (signed)
3. `dh`: high excess vs max(open, close) (unsigned)
4. `dl`: low deficit vs min(open, close) (unsigned)
5. `vol_log`: log2(volume+1) quantized to nibble

## Tick Channel Order (5 nibbles per row)
1. `dt`: timestamp delta ms (unsigned)
2. `dbid`: bid delta ticks (signed)
3. `dask`: ask delta ticks (signed)
4. `bid_size_log`: log2(bid_size+1) quantized nibble
5. `ask_size_log`: log2(ask_size+1) quantized nibble

## Determinism Rules
- Identical input arrays + identical seed must produce byte-identical packet outputs.
- CRC mismatch is a hard decode error.
- Overflow decoding must consume all overflow bytes.
