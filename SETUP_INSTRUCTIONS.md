# Ilayaraja Songs Downloader - Setup Instructions

## Prerequisites

This script requires Python 3.7+ and several dependencies.

### Step 1: Install Python
If you don't have Python installed, download from https://www.python.org/downloads/

### Step 2: Install Required Libraries

Open Command Prompt (cmd) or PowerShell and run:

```bash
pip install selenium
```

### Step 3: Download ChromeDriver

The script uses Selenium with Chrome browser. You need ChromeDriver:

1. Check your Chrome version:
   - Open Chrome
   - Click the three-dot menu → Help → About Google Chrome
   - Note the version number

2. Download matching ChromeDriver:
   - Go to https://googlechromelabs.github.io/chrome-for-testing/
   - Download the ChromeDriver version matching your Chrome version
   - Extract the `chromedriver.exe` file

3. Add ChromeDriver to your PATH or keep it in the script folder

### Step 4: Run the Script

Open Command Prompt in the script directory and run:

```bash
python download_ilayaraja.py
```

## How It Works

1. Opens the Ilayaraja songs page in Chrome
2. Extracts all movie/album links from the page
3. For each movie:
   - Clicks on the movie link
   - Clicks "Download Single Zip" button
   - Downloads the file to `Downloads/Ilayaraja_Songs/`
   - Goes back to the previous page
4. After all movies on a page, goes to the next page
5. Repeats until all pages are processed

## Output

Downloaded files will be saved to:
```
C:\Users\[YourUsername]\Downloads\Ilayaraja_Songs\
```

## Troubleshooting

### Common Issues:

1. **"ChromeDriver not found"**
   - Make sure chromedriver.exe is in your PATH or script directory

2. **"Element not found" error**
   - The website structure may have changed
   - Update the CSS selectors in the script (lines with `find_elements`)

3. **Downloads not starting**
   - Check if pop-ups are being blocked
   - Ensure Chrome is not blocking downloads

4. **Script runs too fast**
   - Increase `time.sleep()` values if pages aren't loading fully
   - Change `time.sleep(2)` to `time.sleep(3)` or higher

## Advanced Customization

### Change Download Folder:
```python
DOWNLOAD_FOLDER = "Your/Custom/Path/Here"
```

### Increase Wait Times:
```python
time.sleep(3)  # Wait 3 seconds instead of 2
```

### Add Headless Mode (run without opening browser):
Add to the script after `chrome_options = Options()`:
```python
chrome_options.add_argument("--headless")
```

## Notes

- Keep the browser window open while the script runs
- Don't click or interfere with the browser while it's running
- The script handles pagination automatically
- Each download will be retried if it fails
