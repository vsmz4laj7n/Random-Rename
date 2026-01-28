# BehindTheName Random Name Generator (CLI)

A Python CLI tool that uses the **BehindTheName API** to generate random given names (and optional surnames) with support for:

- Gender filtering (feminine / masculine / unisex)
- Origin/usage codes (Italian, Japanese, Hawaiian, etc.)
- Rate limiting with local logging
- Interactive mode or one-shot CLI mode
- SQLite logging with timestamps and API key hashing

---

## ✨ Features

- 🌍 Supports **250+ usage/origin codes** from BehindTheName  
- 🚻 Gender filters: feminine (`f`), masculine (`m`), unisex/any (`u`)  
- 📦 Logs all API calls + responses to SQLite  
- 🕒 Local timezone detection & ISO timestamps  
- 🔐 API key is **never stored in plain text** (SHA-256 hash only)  
- 🧑‍💻 Interactive mode + one-command mode  

---

## 📦 Requirements

- Python **3.9+**
- An API key from:  
  👉 https://www.behindthename.com/api/

### Python dependencies

```bash
pip install requests python-dotenv
````

---

## 🔑 Setup

1. Clone or copy the script:

```bash
git clone https://github.com/vsmz4laj7n/Random-Rename
cd Random-Rename
```

2. Create a `.env` file:

```env
API_KEY=your_behindthename_api_key_here
```

Or pass it directly via CLI using `--key`.

---

## ▶️ Usage

### Interactive Mode (default)

```bash
python names.py
```

You’ll be prompted for:

* Number of given names (1–6)
* Gender (`f`, `m`, `u`)
* Usage/origin code (e.g. `ita`, `jap`, `haw`)
* Whether to include a random surname

---

### One-Shot Mode (`--once`)

```bash
python names.py --once
```

Default:

* Gender: `u`
* Usage: `ita`
* Number: `2`
* No surname

#### Examples

```bash
python names.py --once f jap
# Feminine Japanese names

python names.py --once u ita surname
# Unisex Italian names with surname

python names.py --once --number 3 m eng surname
# 3 Masculine English names with surname

python names.py --key YOUR_API_KEY --once
# Provide API key via command line
```

---

## 🧾 Output Example

```
══════════════════════════════════════════════════════════════════════
Feminine • Japanese
──────────────────────────────────────────────────────────────────────
Given name(s):  Aiko Haruka
Surname:        Tanaka
──────────────────────────────────────────────────────────────────────
Timestamp:      28 Jan 2025 08:53:17 +0700
ISO Timestamp:  2025-01-28T08:53:17+07:00
══════════════════════════════════════════════════════════════════════
```

---

## 🗃️ Database

This script creates a local SQLite database:

```
name_generator.db
```

### Tables

* `api_logs`
  Stores:

  * timestamp (unix)
  * iso_timestamp
  * human_timestamp
  * key_hash

* `generated_names`
  Stores:

  * timestamp
  * iso_timestamp
  * human_timestamp
  * key_hash
  * response_json

Your **API key is never saved**, only its SHA-256 hash.

---

## ⏱️ Rate Limits

Enforced locally based on BehindTheName’s API rules:

| Period   | Max Requests |
| -------- | ------------ |
| 1 second | 2            |
| 1 hour   | 400          |
| 1 day    | 4,000        |
| 1 year   | ~400,000     |

If exceeded, the script tells you how long to wait.

---

## 🧠 Usage Codes

Example usage/origin codes:

| Code | Meaning    |
| ---- | ---------- |
| ita  | Italian    |
| jap  | Japanese   |
| haw  | Hawaiian   |
| eng  | English    |
| vie  | Vietnamese |
| gre  | Greek      |

(Full list is embedded in the script as `USAGE_CODES`.)

---

## 🔐 Security

* API key is loaded from `.env` or `--key`
* Only a **hashed key** is stored in logs
* No plaintext secrets are written to disk

---

## 📜 License

Use freely for personal, educational, or creative projects.
BehindTheName API terms apply.

---

## ❤️ Credits

* Name data by: **BehindTheName.com**
* Script by: *AlzheimerDoll & Claude*

---
