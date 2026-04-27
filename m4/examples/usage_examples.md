# Usage Examples — Automation Suite (m4)

All examples assume you are running from the `complete-tasks/m4/` directory.

---

## File Organizer

### Basic usage — organize Downloads

```python
from modules.file_organizer import FileOrganizer

organizer = FileOrganizer(
    source_folder="/home/user/Downloads",
    dest_folder="/home/user/Downloads/Organized",   # optional
)

# 1. Preview without moving anything
plan = organizer.preview()
# Output:
#   [Documents]
#     report.pdf
#   [Images]
#     photo.jpg
#     banner.png

# 2. Run the organizer
summary = organizer.organize()
print(summary)
# {'moved': 12, 'skipped': 0, 'errors': 0,
#  'categories': {'Documents': 3, 'Images': 7, 'Code': 2}}

# 3. Check what ended up where
stats = organizer.get_statistics()
# {'Code': 2, 'Documents': 3, 'Images': 7}

# 4. Undo if you change your mind
result = organizer.undo_last_run()
print(result)  # {'restored': 12, 'errors': 0}
```

### Custom categories

```python
from modules.file_organizer import FileOrganizer

organizer = FileOrganizer("/path/to/folder")

# Add a custom category for design files
organizer.file_categories["Design"] = [".psd", ".ai", ".sketch", ".fig"]
organizer.file_categories["eBooks"] = [".epub", ".mobi"]
organizer._rebuild_ext_map()  # apply changes

organizer.organize()
```

---

## Web Scraper

### Scrape links

```python
from modules.scraper import WebScraper

scraper = WebScraper("https://example.com", delay=1.5)

result = scraper.scrape_links("https://example.com")
print(result["count"])          # number of unique links
for link in result["links"]:
    print(link)

scraper.save_results(result, "output/links.json")
```

### Scrape headings

```python
from modules.scraper import WebScraper

scraper = WebScraper("https://docs.python.org")

data = scraper.scrape_headings("https://docs.python.org/3/tutorial/")
for h in data["headings"]:
    print(f"[{h['level']}] {h['text']}")
# [h1] The Python Tutorial
# [h2] Whetting Your Appetite
# ...
```

### Scrape paragraphs

```python
from modules.scraper import WebScraper

scraper = WebScraper("https://en.wikipedia.org")
data = scraper.scrape_text("https://en.wikipedia.org/wiki/Python_(programming_language)")

# Print the first 3 paragraphs
for para in data["paragraphs"][:3]:
    print(para)
    print("---")
```

### Scrape images

```python
from modules.scraper import WebScraper

scraper = WebScraper("https://example.com")
data = scraper.scrape_images("https://example.com")

for src in data["images"]:
    print(src)

scraper.save_results(data, "output/images.json")
```

### Graceful error handling

```python
from modules.scraper import WebScraper

scraper = WebScraper("https://nonexistent.invalid", max_retries=2)
result = scraper.scrape_links("https://nonexistent.invalid")

if "error" in result:
    print(f"Scraping failed: {result['error']}")
else:
    print(f"Got {result['count']} links")
```

---

## CLI Examples

```bash
# Interactive
python main.py

# File organizer
python main.py organize ~/Downloads --preview
python main.py organize ~/Downloads
python main.py organize ~/Downloads --stats
python main.py organize ~/Downloads --undo

# Web scraper
python main.py scrape https://example.com
python main.py scrape https://example.com --mode headings
python main.py scrape https://example.com --mode images --save results.json
python main.py scrape https://example.com --delay 2.0
```
