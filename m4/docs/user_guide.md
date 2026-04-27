# User Guide — Automation Suite (m4)

---

## Table of Contents

1. [Setup & Installation](#setup--installation)
2. [File Organizer](#file-organizer)
3. [Web Scraper](#web-scraper)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

---

## Setup & Installation

### Requirements

- Python 3.10 or later
- pip

### Install dependencies

```bash
cd complete-tasks/m4
pip install -r requirements.txt
```

The following packages are installed:

| Package | Purpose |
|---|---|
| `requests` | HTTP client for the web scraper |
| `beautifulsoup4` | HTML parsing |
| `lxml` | Fast HTML/XML parser backend |

### Verify installation

```bash
python -c "from modules.file_organizer import FileOrganizer; print('OK')"
python -c "from modules.scraper import WebScraper; print('OK')"
```

---

## File Organizer

### Overview

The File Organizer moves loose files from a **source folder** into named subfolders
(categories) inside a **destination folder**.

Default categories:

| Category | Extensions |
|---|---|
| Documents | `.pdf` `.doc` `.docx` `.txt` `.xlsx` `.csv` `.pptx` |
| Images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.svg` `.webp` |
| Videos | `.mp4` `.avi` `.mov` `.wmv` `.mkv` |
| Music | `.mp3` `.wav` `.aac` `.flac` `.ogg` |
| Archives | `.zip` `.rar` `.7z` `.tar` `.gz` |
| Code | `.py` `.js` `.html` `.css` `.java` `.cpp` `.ts` |
| Others | everything else |

### Interactive usage

```
python main.py
→ Choose option 1 (File Organizer)
→ Enter the source folder path
→ Optionally enter a destination folder (or press Enter for default)
→ Choose an action: Preview / Organize / Undo / Statistics
```

### CLI usage

```bash
# See what would be moved (no changes made)
python main.py organize /path/to/source --preview

# Move the files
python main.py organize /path/to/source

# Specify a custom destination
python main.py organize /path/to/source --dest /path/to/dest

# Show statistics (counts per category in destination)
python main.py organize /path/to/source --stats

# Undo the last organize run
python main.py organize /path/to/source --undo
```

### How duplicates are handled

If a file with the same name already exists in the destination category folder,
a timestamp suffix is appended:

```
photo.jpg        → Organized/Images/photo.jpg
photo.jpg (dup)  → Organized/Images/photo_20240601_153012.jpg
```

### Undo

After each `organize()` run, a hidden file `.organizer_undo.json` is written inside
the destination folder.  Running `--undo` reads this log and moves every file back
to its original location.

> **Note:** The undo log is deleted after a successful undo. You cannot undo twice.

### Programmatic API

```python
from modules.file_organizer import FileOrganizer

fo = FileOrganizer(source_folder="/path/to/source")
fo.preview()                    # returns {category: [filenames]}
summary = fo.organize()         # returns {moved, skipped, errors, categories}
stats   = fo.get_statistics()   # returns {category: count}
result  = fo.undo_last_run()    # returns {restored, errors}
```

---

## Web Scraper

### Overview

The Web Scraper fetches a URL using `requests` and parses the HTML with
`BeautifulSoup`.  It extracts four types of data: links, paragraph text,
headings, and images.

### Ethical guidelines

- **Respect `robots.txt`** — always check whether scraping is permitted.
- **Use a polite delay** — the default is 1 second between requests.
- **Do not hammer servers** — increase `delay` for large crawls.
- **Identify yourself** — the default User-Agent string includes `EducationalScraper`.
- **Do not scrape personal data** without a lawful basis.

### Interactive usage

```
python main.py
→ Choose option 2 (Web Scraper)
→ Enter the target URL
→ Choose what to scrape: Links / Text / Headings / Images
→ Optionally save results to a JSON file
```

### CLI usage

```bash
# Links (default)
python main.py scrape https://example.com

# Paragraph text
python main.py scrape https://example.com --mode text

# Headings
python main.py scrape https://example.com --mode headings

# Images
python main.py scrape https://example.com --mode images

# Save results to JSON
python main.py scrape https://example.com --mode links --save output.json

# Custom delay
python main.py scrape https://example.com --delay 2.5
```

### Return structure

Every scrape method returns a dict:

```json
{
  "url": "https://example.com",
  "count": 12,
  "links": ["https://...", "https://..."]
}
```

On error:

```json
{
  "url": "https://...",
  "count": 0,
  "links": [],
  "error": "Failed to fetch page"
}
```

### Programmatic API

```python
from modules.scraper import WebScraper

ws = WebScraper("https://example.com", delay=1.0, timeout=10, max_retries=3)

ws.scrape_links("https://example.com")      # links
ws.scrape_text("https://example.com")       # paragraphs
ws.scrape_headings("https://example.com")   # headings
ws.scrape_images("https://example.com")     # images

ws.save_results(data, "output/result.json") # save any result
```

---

## Configuration

Edit `config/settings.json` to change defaults:

```json
{
  "file_organizer": {
    "categories": {
      "Documents": [".pdf", ".txt"],
      "MyCustom":  [".xyz"]
    },
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

The interactive menu and CLI both load this file automatically.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install -r requirements.txt` |
| `ValueError: Source folder does not exist` | Check the path; use absolute paths to be safe |
| Scraper returns `"error": "Failed to fetch page"` | Check internet connection; verify URL is public; increase `max_retries` |
| Scraper is blocked (HTTP 403/429) | Increase `delay`; some sites block scrapers by policy |
| Log file not created | Ensure the `logs/` directory exists (a `.gitkeep` is included) |
| Undo does not work | The undo log is stored in `<dest>/.organizer_undo.json` — do not delete it |
