<div align="center">

# lzform-regbot

**Automated registration bot for lzform**  
Geetest v4 CAPTCHA solving + PoW proof-of-work bypass

[![Python](https://img.shields.io/badge/python-3.13-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/solver-FastAPI-009688?logo=fastapi)](https://gtv4.c0ffee.space)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)

</div>

## Overview

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  regbot     │────→│  gtv4-solver │────→│  form.lztech   │
│  (this repo)│     │  (FastAPI)   │     │  /api/auth/    │
│             │←────│  HF Spaces   │←────│  register      │
└─────────────┘     └──────────────┘     └────────────────┘
```

- **Geetest v4** solved remotely via [`gtv4.c0ffee.space`](https://gtv4.c0ffee.space)
- **PoW** (`_proof`) computed locally — lightweight SHA-256
- **Batch mode** — registers multiple accounts with random emails/passwords

## Quick Start

```bash
uv run python main.py <count>              # batch register N accounts
uv run python main.py <email> <password>   # single register
```

### Examples

```bash
# Register 5 random accounts
uv run python main.py 5

# Register one specific account
uv run python main.py "user@example.com" "MyP@ss1234"
```

## Batch Output

```
Batch registering 3 accounts...

[1/3] 7ri3n2hzzn5b6wym@proton.me ... 201 (2.6s)
[2/3] 1m3xzt7bz4gjvugd@163.com ... 201 (2.0s)
[3/3] nddn06o5klurmqr@proton.me ... 201 (2.1s)

Done: 3 success, 0 failed
```

## Architecture

| Component | Location | Description |
|-----------|----------|-------------|
| `main.py` | this repo | CLI regbot, batch/single mode |
| `solver` | [`gtv4.c0ffee.space`](https://gtv4.c0ffee.space) | Geetest v4 solving service (FastAPI) |
| `_proof` | local | SHA-256 PoW with `00` prefix |

## Remote Solver API

```bash
curl "https://gtv4.c0ffee.space/solve?captcha_id=9ee5ee5715144aca98e58280f20334fe"
```

Returns:

```json
{
  "geetestResult": {
    "captcha_id": "...",
    "lot_number": "...",
    "pass_token": "...",
    "gen_time": "...",
    "captcha_output": "..."
  },
  "_proof": { "challenge": "...", "nonce": 0 },
  "elapsed": 1.38
}
```

## License

AGPL-3.0
