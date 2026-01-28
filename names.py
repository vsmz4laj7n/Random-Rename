import sqlite3
import hashlib
import time
import requests
import os
import argparse
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# ────────────────────────────────────────────────
# Timezone setup (automatic detection)
# ────────────────────────────────────────────────
try:
    LOCAL_TZ = datetime.now().astimezone().utcoffset()
    LOCAL_TZ = timezone(LOCAL_TZ) if LOCAL_TZ else timezone(timedelta(hours=0))  # Fallback to UTC
except Exception:
    LOCAL_TZ = timezone(timedelta(hours=0))  # Fallback to UTC if detection fails

# ────────────────────────────────────────────────
# Complete usage code dictionary (all 250+ from BehindTheName)
# ────────────────────────────────────────────────
USAGE_CODES = {
    "afk": "Afrikaans",           "afr": "African",              "aka": "Akan",
    "alb": "Albanian",             "alg": "Algonquin",            "ame": "Indigenous American",
    "amem": "New World Mythology", "amh": "Amharic",              "anci": "Ancient",
    "apa": "Apache",               "ara": "Arabic",               "arm": "Armenian",
    "asm": "Assamese",             "ast": "Asturian",             "astr": "Astronomy",
    "aus": "Indigenous Australian","ava": "Avar",                 "aym": "Aymara",
    "aze": "Azerbaijani",          "bal": "Balinese",             "bas": "Basque",
    "bel": "Belarusian",           "bem": "Bemba",                "ben": "Bengali",
    "ber": "Berber",               "bhu": "Bhutanese",            "bibl": "Biblical (All)",
    "bos": "Bosnian",              "bre": "Breton",               "bsh": "Bashkir",
    "bul": "Bulgarian",            "bur": "Burmese",              "cat": "Catalan",
    "cela": "Ancient Celtic",      "celm": "Celtic Mythology",    "cew": "Chewa",
    "cha": "Chamorro",             "che": "Chechen",              "chi": "Chinese",
    "chk": "Cherokee",             "cht": "Choctaw",              "chy": "Cheyenne",
    "cir": "Circassian",           "cmr": "Comorian",             "com": "Comanche",
    "coo": "Cook Islands Māori",   "cop": "Coptic",               "cor": "Cornish",
    "cre": "Cree",                 "cro": "Croatian",             "crs": "Corsican",
    "cze": "Czech",                "dan": "Danish",               "dgs": "Dagestani",
    "dhi": "Dhivehi",              "drg": "Dargin",               "dut": "Dutch",
    "egya": "Ancient Egyptian",    "egym": "Egyptian Mythology",  "elf": "Xmas Elf",
    "eng": "English",              "enga": "Anglo-Saxon",         "esp": "Esperanto",
    "est": "Estonian",             "eth": "Ethiopian",            "ewe": "Ewe",
    "fae": "Faroese",              "fairy": "Fairy",              "fij": "Fijian",
    "fil": "Filipino",             "fin": "Finnish",              "fle": "Flemish",
    "fntsg": "Gluttakh",           "fntsm": "Monstrall",          "fntso": "Orinami",
    "fntsr": "Romanto",            "fntss": "Simitiq",            "fntst": "Tsang",
    "fntsx": "Xalaxxi",            "fre": "French",               "fri": "Frisian",
    "ful": "Fula",                 "gaa": "Ga",                   "gal": "Galician",
    "gan": "Ganda",                "geo": "Georgian",             "ger": "German",
    "gmca": "Ancient Germanic",    "goth": "Goth",                "gre": "Greek",
    "grea": "Ancient Greek",       "grem": "Greek Mythology",     "grn": "Greenlandic",
    "gua": "Guarani",              "guj": "Gujarati",             "hau": "Hausa",
    "haw": "Hawaiian",             "hb": "Hillbilly",             "heb": "Hebrew",
    "hin": "Hindi",                "hippy": "Hippy",              "hist": "History",
    "hmo": "Hmong",                "hun": "Hungarian",            "ibi": "Ibibio",
    "ice": "Icelandic",            "igb": "Igbo",                 "ind": "Indian",
    "indm": "Hindu Mythology",     "ing": "Ingush",               "ins": "Indonesian",
    "inu": "Inuit",                "iri": "Irish",                "iro": "Iroquois",
    "ita": "Italian",              "jap": "Japanese",             "jav": "Javanese",
    "jer": "Jèrriais",             "jew": "Jewish",               "kan": "Kannada",
    "kaz": "Kazakh",               "khm": "Khmer",                "kig": "Kiga",
    "kik": "Kikuyu",               "kk": "Kreatyve",              "kon": "Kongo",
    "kor": "Korean",               "kur": "Kurdish",              "kyr": "Kyrgyz",
    "lao": "Lao",                  "lat": "Latvian",              "lim": "Limburgish",
    "lite": "Literature",          "litk": "Arthurian Romance",   "lth": "Lithuanian",
    "luh": "Luhya",                "luo": "Luo",                  "mac": "Macedonian",
    "mag": "Maguindanao",          "mal": "Maltese",              "man": "Manx",
    "mao": "Māori",                "map": "Mapuche",              "may": "Mayan",
    "mbu": "Mbundu",               "medi": "Medieval",            "mlm": "Malayalam",
    "mly": "Malay",                "moh": "Mohawk",               "mol": "Moldovan",
    "mon": "Mongolian",            "morm": "Mormon",              "mrt": "Marathi",
    "mwe": "Mwera",                "myth": "Mythology",           "nah": "Nahuatl",
    "nav": "Navajo",               "nde": "Ndebele",              "neaa": "Ancient Near Eastern",
    "neam": "Near Eastern Mythology","nep": "Nepali",             "nor": "Norwegian",
    "nrm": "Norman",               "nuu": "Nuu-chah-nulth",       "occ": "Occitan",
    "odi": "Odia",                 "oji": "Ojibwe",               "one": "Oneida",
    "oro": "Oromo",                "oss": "Ossetian",             "pas": "Pashto",
    "pcd": "Picard",               "per": "Persian",              "perf": "Theatre",
    "pets": "Pet",                 "pin": "Pintupi",              "pol": "Polish",
    "popu": "Popular Culture",     "por": "Portuguese",           "pow": "Powhatan",
    "pun": "Punjabi",              "que": "Quechua",              "rap": "Rapa Nui",
    "rmn": "Romanian",             "roma": "Ancient Roman",       "romm": "Roman Mythology",
    "rus": "Russian",              "sam": "Sami",                 "sar": "Sardinian",
    "sax": "Low German",           "scaa": "Ancient Scandinavian","scam": "Norse Mythology",
    "sco": "Scottish",             "sct": "Scots",                "sen": "Seneca",
    "ser": "Serbian",              "sha": "Shawnee",              "sho": "Shona",
    "sic": "Sicilian",             "sik": "Siksika",              "sin": "Sinhalese",
    "sio": "Sioux",                "sla": "Slavic",               "slam": "Slavic Mythology",
    "slk": "Slovak",               "sln": "Slovene",              "smn": "Samoan",
    "som": "Somali",               "sor": "Sorbian",              "sot": "Sotho",
    "spa": "Spanish",              "sun": "Sundanese",            "swa": "Swahili",
    "swe": "Swedish",              "swz": "Swazi",                "tag": "Tagalog",
    "tah": "Tahitian",             "taj": "Tajik",                "tam": "Tamil",
    "tat": "Tatar",                "tau": "Tausug",               "tel": "Telugu",
    "tha": "Thai",                 "theo": "Theology",            "tib": "Tibetan",
    "tig": "Tigrinya",             "tkm": "Turkmen",              "tng": "Tonga",
    "ton": "Tongan",               "too": "Tooro",                "trans": "Transformer",
    "tsw": "Tswana",               "tua": "Tuareg",               "tum": "Tumbuka",
    "tup": "Tupi",                 "tur": "Turkish",              "ukr": "Ukrainian",
    "urd": "Urdu",                 "urh": "Urhobo",               "usa": "American",
    "uyg": "Uyghur",               "uzb": "Uzbek",                "vari": "Various",
    "vie": "Vietnamese",           "wel": "Welsh",                "witch": "Witch",
    "wln": "Walloon",              "wrest": "Wrestler",           "xho": "Xhosa",
    "yao": "Yao",                  "yol": "Yolngu",               "yor": "Yoruba",
    "zap": "Zapotec",              "zul": "Zulu"
}

# ────────────────────────────────────────────────
# Gender options
# ────────────────────────────────────────────────
GENDER_OPTIONS = {
    'f': 'Feminine only',
    'm': 'Masculine only',
    'u': 'Unisex / Any (no gender filter)',
}

# ────────────────────────────────────────────────
# SQLite database setup
# ────────────────────────────────────────────────
conn = sqlite3.connect('name_generator.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_logs (
        timestamp          REAL,          -- Unix timestamp (seconds since 1970 UTC)
        iso_timestamp      TEXT,          -- '2025-01-28T08:53:17+07:00'
        human_timestamp    TEXT,          -- '28 Jan 2025 08:53:17 +0700'
        key_hash           TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS generated_names (
        timestamp          REAL,
        iso_timestamp      TEXT,
        human_timestamp    TEXT,
        key_hash           TEXT,
        response_json      TEXT
    )
''')

cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_ts_hash ON api_logs (timestamp, key_hash)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_names_ts_hash ON generated_names (timestamp, key_hash)')
conn.commit()

# ────────────────────────────────────────────────
# Rate limits
# ────────────────────────────────────────────────
RATE_LIMITS = [
    (1,        2),       # 2 per second
    (3600,     400),     # 400 per hour
    (86400,    4000),    # 4,000 per day
    (365*86400, 400000)  # ~400,000 per year
]

def can_make_request():
    now = time.time()
    max_wait = 0.0

    for period, limit in RATE_LIMITS:
        cursor.execute(
            "SELECT timestamp FROM api_logs "
            "WHERE key_hash = ? AND timestamp > ? "
            "ORDER BY timestamp ASC",
            (key_hash, now - period)
        )
        times = [row[0] for row in cursor.fetchall()]

        if len(times) >= limit:
            wait = (times[0] + period) - now
            max_wait = max(max_wait, wait)

    return max_wait <= 0, max_wait

# ────────────────────────────────────────────────
# Function to generate names (core logic)
# ────────────────────────────────────────────────
def generate_names(api_key, gender_choice='u', usage='ita', number=2, random_surname=False):
    global key_hash
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Rate limit check
    allowed, wait_time = can_make_request()
    if not allowed:
        if wait_time < 90:
            wait_display = f"{wait_time:.1f} seconds"
        elif wait_time < 3600:
            wait_display = f"{wait_time/60:.1f} minutes"
        else:
            wait_display = f"{wait_time/3600:.1f} hours"
        print(f"\nRate limit reached. Please wait ≈ {wait_display}")
        return None

    # Map gender
    api_gender = None
    if gender_choice == 'f':
        api_gender = 'f'
    elif gender_choice == 'm':
        api_gender = 'm'

    # Build params
    params = {
        'key': api_key,
        'number': number,
        'randomsurname': 'yes' if random_surname else 'no'
    }
    if api_gender:
        params['gender'] = api_gender
    if usage:
        params['usage'] = usage

    try:
        response = requests.get("https://www.behindthename.com/api/random.json",
                                params=params, timeout=12)
        response.raise_for_status()
        data = response.json()

        # Timestamps
        ts = time.time()
        now_local = datetime.fromtimestamp(ts, tz=LOCAL_TZ)
        iso_timestamp = now_local.isoformat()
        human_timestamp = now_local.strftime("%d %b %Y %H:%M:%S %z")

        # Log
        cursor.execute("""
            INSERT INTO api_logs
            (timestamp, iso_timestamp, human_timestamp, key_hash)
            VALUES (?, ?, ?, ?)
        """, (ts, iso_timestamp, human_timestamp, key_hash))

        cursor.execute("""
            INSERT INTO generated_names
            (timestamp, iso_timestamp, human_timestamp, key_hash, response_json)
            VALUES (?, ?, ?, ?, ?)
        """, (ts, iso_timestamp, human_timestamp, key_hash, response.text))

        conn.commit()

        return data, gender_choice, usage, human_timestamp, iso_timestamp

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# ────────────────────────────────────────────────
# Display generated names and exit
# ────────────────────────────────────────────────
def display_and_exit(result, gender_choice, usage, human_timestamp, iso_timestamp):
    if not result:
        print("Generation failed. Goodbye!")
        conn.close()
        exit(1)

    print("\n" + "═" * 70)

    gender_label = GENDER_OPTIONS.get(gender_choice, GENDER_OPTIONS['u']).split()[0]
    origin_label = USAGE_CODES.get(usage, usage.upper())

    print(f"{gender_label} • {origin_label}")
    print("─" * 70)

    if 'names' in result and result['names']:
        print("Given name(s):  " + " ".join(result['names']))

    if 'surname' in result and result['surname']:
        print("Surname:        " + result['surname'])

    print("─" * 70)
    print(f"Timestamp:      {human_timestamp}")
    print(f"ISO Timestamp:  {iso_timestamp}")
    print("═" * 70 + "\n")

    print("Generated successfully! Goodbye!")
    conn.close()
    exit(0)

# ────────────────────────────────────────────────
# Interactive mode (original loop)
# ────────────────────────────────────────────────
def run_interactive(api_key):
    print("BehindTheName Random Name Generator")
    print(f"API key hash: {hashlib.sha256(api_key.encode()).hexdigest()[:16]}...")
    print("Press Enter to generate • type 'exit', 'q' or press Ctrl+C to quit\n")

    try:
        while True:
            action = input("Generate name(s)? [Enter = yes]: ").strip().lower()
            if action in ('exit', 'quit', 'q', 'x'):
                print("\nGoodbye!")
                break
            if action and action not in ('y', 'yes', 'generate'):
                continue

            # Number
            while True:
                n = input("Number of given names (1–6) [default 2]: ").strip()
                if not n:
                    number = 2
                    break
                try:
                    number = int(n)
                    if 1 <= number <= 6:
                        break
                    print("Please enter a number between 1 and 6.")
                except ValueError:
                    print("Invalid input.")

            # Gender
            print("\nGender options:")
            for code, desc in GENDER_OPTIONS.items():
                print(f"  {code:2} → {desc}")
            gender_choice = input("Gender (f/m/u) [default u]: ").strip().lower() or 'u'

            # Usage
            print("\nEnter usage code (or leave empty for any)")
            usage_input = input("Usage code [default 'ita']: ").strip().lower() or 'ita'
            usage = usage_input

            if usage in USAGE_CODES:
                print(f"→ {usage.upper()} = {USAGE_CODES[usage]}")
            else:
                print(f"→ Using custom/unknown code: {usage}")

            # Surname
            surname_choice = input("\nInclude random surname? (y/n) [default n]: ").strip().lower()
            random_surname = surname_choice in ('y', 'yes')

            result = generate_names(api_key, gender_choice, usage, number, random_surname)
            if result:
                data, _, _, human_ts, iso_ts = result
                gender_label = GENDER_OPTIONS.get(gender_choice, GENDER_OPTIONS['u']).split()[0]
                origin_label = USAGE_CODES.get(usage, usage.upper())

                print("\n" + "═" * 70)
                print(f"{gender_label} • {origin_label}")
                print("─" * 70)

                if 'names' in data and data['names']:
                    print("Given name(s):  " + " ".join(data['names']))

                if random_surname and 'surname' in data and data['surname']:
                    print("Surname:        " + data['surname'])

                print("─" * 70)
                print(f"Timestamp:      {human_ts}")
                print(f"ISO Timestamp:  {iso_ts}")
                print("═" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user (Ctrl+C). Goodbye!")

    finally:
        conn.close()
        print("Database connection closed.")

# ────────────────────────────────────────────────
# Command-line parser
# ────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description="BehindTheName Random Name Generator Script",
    epilog="""
Examples:
  python names.py                  # Run in interactive mode (default)
  python names.py --once           # Generate once with defaults (u ita, number=2, no surname)
  python names.py --once f jap     # Feminine Japanese, number=2, no surname
  python names.py --once u ita surname  # Unisex Italian with surname
  python names.py --once --number 3 m eng surname  # Masculine English, 3 names, with surname
  python names.py --key YOUR_API_KEY --once  # Provide API key via command line

Note: If --key is not provided, it falls back to API_KEY in .env file.
Gender: f (feminine), m (masculine), u (unisex/any, default)
Usage: Any valid code like 'ita', 'jap', 'haw' (default 'ita')
'surname' keyword: Include random surname (optional)
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument('--once', action='store_true', help="Run once with provided options and exit automatically.")
parser.add_argument('--key', type=str, help="Provide API key via command line (overrides .env).")
parser.add_argument('--number', type=int, default=2, help="Number of given names (1-6, default 2).")
parser.add_argument('args', nargs='*', help="For --once: [gender] [usage] [surname]")

args = parser.parse_args()

# Load API key (prefer --key, fallback to .env)
API_KEY = args.key
if not API_KEY:
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
if not API_KEY:
    print("Error: API_KEY not found in --key or .env file.")
    exit(1)

# Run mode
if args.once:
    # Parse positional args for --once
    pos_args = args.args
    gender_choice = 'u'
    usage = 'ita'
    random_surname = False
    number = args.number if args.number else 2

    if pos_args:
        # First arg: gender if f/m/u
        if pos_args[0].lower() in ('f', 'm', 'u'):
            gender_choice = pos_args[0].lower()
            pos_args = pos_args[1:]

    if pos_args:
        # Next: usage code
        usage = pos_args[0].lower()
        pos_args = pos_args[1:]

    if pos_args:
        # Next: 'surname' if present
        if pos_args[0].lower() == 'surname':
            random_surname = True

    # Validate number
    if not 1 <= number <= 6:
        print("Error: --number must be between 1 and 6.")
        exit(1)

    # Generate and exit
    result = generate_names(API_KEY, gender_choice, usage, number, random_surname)
    if result:
        display_and_exit(*result)
    else:
        print("Generation failed. Goodbye!")
        conn.close()
        exit(1)

else:
    # Interactive mode
    run_interactive(API_KEY)
