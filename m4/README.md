# Automation Suite — Basic Version (m4)

A CLI automation toolkit for **Month 4** of py-works.  
Combines a **File Organizer** (sort files into category folders) and a **Web Scraper** (extract links, text, headings, and images from any public web page).

---

## Project Structure

```
complete-tasks/m4/
├── README.md
├── requirements.txt
├── main.py                  ← CLI entry point (interactive menu + argparse)
├── modules/
│   ├── __init__.py
│   ├── file_organizer.py    ← FileOrganizer class
│   └── scraper.py           ← WebScraper class
├── config/
│   └── settings.json        ← default configuration
├── logs/
│   └── automation.log       ← created at runtime
├── examples/
│   └── usage_examples.md
└── docs/
    └── user_guide.md
```

---

## Setup

```bash
cd complete-tasks/m4
pip install -r requirements.txt
```

---

## Running

### Interactive menu

```bash
python main.py
```

```
========================================
  AUTOMATION SUITE
========================================
  1. File Organizer
  2. Web Scraper
  3. Exit
========================================
```

### Command-line (non-interactive)

```bash
# Preview what would be organized
python main.py organize /path/to/folder --preview

# Organize files
python main.py organize /path/to/folder

# Undo last organize run
python main.py organize /path/to/folder --undo

# Scrape links from a page
python main.py scrape https://example.com --mode links

# Scrape headings and save to JSON
python main.py scrape https://example.com --mode headings --save results.json
```

---

## Features

### File Organizer

| Feature | Details |
|---|---|
| Auto-categorize | Documents, Images, Videos, Music, Archives, Code, Others |
| Duplicate handling | Appends timestamp to prevent overwriting |
| Preview mode | Shows plan without moving anything |
| Undo | Reads `.organizer_undo.json` and restores files |
| Statistics | Counts per category in destination |

### Web Scraper

| Feature | Details |
|---|---|
| `scrape_links` | All unique href links (absolute URLs) |
| `scrape_text` | All `<p>` paragraph text |
| `scrape_headings` | h1 / h2 / h3 headings with level labels |
| `scrape_images` | All `<img src>` URLs |
| `save_results` | Persist any result to JSON |
| Rate limiting | Configurable delay between requests |
| Retry logic | Exponential back-off on transient failures |

---

## Configuration (`config/settings.json`)

```json
{
  "file_organizer": {
    "categories": { "Documents": [".pdf", ".txt", ...], ... },
    "log_operations": true
  },
  "scraper": {
    "default_delay": 1.0,
    "timeout": 10,
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 ..."
  }
}
```

---

## Usage Examples

```python
from modules.file_organizer import FileOrganizer
from modules.scraper import WebScraper

# Organize a folder
fo = FileOrganizer("~/Downloads")
fo.preview()
fo.organize()

# Scrape a page
ws = WebScraper("https://example.com")
result = ws.scrape_links("https://example.com")
ws.save_results(result, "links.json")
```

See [`examples/usage_examples.md`](examples/usage_examples.md) for more.
