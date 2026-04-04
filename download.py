import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json

# Configuration
BASE_URL = "https://www.isaiminihq.com/singer/shankar-mahadevan-songs/"
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "shankar_mahadevan_Songs")
DOWNLOAD_MODE = "individual"  # "individual" for MP3 songs, "zip" for movie zips

# Create download folder if it doesn't exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configure Chrome to download to our folder
chrome_options = Options()
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
prefs = {
    "download.default_directory": DOWNLOAD_FOLDER,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize WebDriver
print("Initializing webdriver...")
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.set_page_load_timeout(30)
driver.implicitly_wait(10)

print("Navigating to URL...")
driver.get(BASE_URL)
print("Waiting for page to load...")
time.sleep(10)

def download_movie_zip(movie_name):
    try:
        # Wait for the "Download Single Zip" button specifically
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Download Single Zip']"))
        )
        
        print(f"  Found 'Download Single Zip' button, clicking it...")
        download_button.click()
        
        # Wait for download to start
        time.sleep(5)
        
        print(f"  Download initiated for: {movie_name}")
        return True
    except Exception as e:
        print(f"  Warning: Could not find 'Download Single Zip' button for {movie_name}")
        # Try with more flexible matching
        try:
            download_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Download Single Zip')]"))
            )
            print(f"  Found button with flexible match, clicking it...")
            download_button.click()
            time.sleep(5)
            return True
        except:
            print(f"  Skipping: Download button not found (page may not have downloadable content)")
            return False

def scrape_download_links():
    """Get all individual download links from current page"""
    try:
        print("  Sleeping to load page...")
        time.sleep(10)
        print("  Scrolling to load all content...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        print("  Finding elements...")
        
        # Find all download links
        download_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, '/download/hash/')]")
        print(f"  Total download buttons found: {len(download_buttons)}")
        
        # Extract hrefs
        links = []
        for button in download_buttons:
            href = button.get_attribute("href")
            if href:
                full_url = "https://www.isaiminihq.com" + href if href.startswith('/') else href
                links.append(full_url)
        
        print(f"  Found {len(links)} download links")
        if links:
            print(f"  Sample: {links[0]}")
        return links
    except Exception as e:
        print(f"Error scraping download links: {str(e)}")
        return []

def scrape_page():
    """Get all movie links from current page"""
    try:
        # Wait for movie links to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'songs/')]"))
        )
        time.sleep(3)  # Additional wait for content to stabilize
        
        # Find all links on the page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"  Total links found: {len(all_links)}")
        
        # Filter for movie/content links (not navigation, pagination, etc)
        links = []
        for link in all_links:
            href = link.get_attribute("href")
            text = link.text.strip()
            
            # Skip empty links, pagination links, and navigation links
            if (href and text and 
                "isaiminihq.com" in href and 
                'songs/' in href and
                '?' not in href and
                not any(x in text.lower() for x in ["next", "previous", "home", "←", "→", "|"])):
                
                # Check if it's not a duplicate
                if not any(link[1] == href for link in links):
                    links.append((text, href))
        
        print(f"  Found {len(links)} movie links")
        if links:
            print(f"  Sample: {links[0]}")
        return links
    except Exception as e:
        print(f"Error scraping page: {str(e)}")
        return []

def go_to_next_page():
    """Navigate to the next page"""
    try:
        # Look for next page button - try multiple selectors
        next_button = None
        next_url = None
        
        selectors = [
            "//a[contains(@rel, 'next')]",
            "//a[contains(text(), 'Next')]",
            "//a.next",
            "//a[contains(text(), 'next')]",
            "//a[contains(@attr, 'next')]"
        ]
        
        for selector in selectors:
            try:
                next_button = driver.find_element(By.XPATH, selector)
                next_url = next_button.get_attribute("href")
                if next_url:
                    break
            except:
                continue
        
        if next_url:
            print(f"  Going to next page: {next_url}")
            driver.get(next_url)
            time.sleep(5)
            return True
        else:
            return False
    except Exception as e:
        print(f"No next page found: {str(e)}")
        return False

def main():
    """Main automation function"""
    try:
        # Load downloaded list
        downloaded_list = []
        try:
            with open('downloaded_list.json', 'r') as f:
                downloaded_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Navigate to the starting URL
        print("Starting download process...")
        # driver.get(BASE_URL)  # Already done before main
        # time.sleep(10)
        print("Starting processing")
        
        current_page = 1
        
        if DOWNLOAD_MODE == "individual":
            print("Entering individual download mode...")
            # Download individual MP3 songs
            while True:
                current_page_url = driver.current_url
                print(f"\n{'='*60}")
                print(f"Processing Page {current_page}")
                print(f"URL: {current_page_url}")
                print(f"{'='*60}")
                
                # Get all download links on current page
                print("Scraping download links...")
                download_links = scrape_download_links()
                print(f"Scraped {len(download_links)} links")
                
                if not download_links:
                    print("No download links found on this page. Exiting.")
                    break
                
                print(f"Found {len(download_links)} download links on this page\n")
                
                # Download each song
                for idx, link in enumerate(download_links, 1):
                    if link in downloaded_list:
                        print(f"  Skipping {link} (already downloaded)")
                        continue
                    
                    print(f"[{idx}/{len(download_links)}] Downloading: {link}")
                    
                    # Find and click the download button
                    try:
                        href_attr = link.replace("https://www.isaiminihq.com", "")
                        button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[@href='{href_attr}']"))
                        )
                        original_handle = driver.current_window_handle
                        button.click()
                        time.sleep(5)  # Wait for download to start
                        
                        # Close the new tab if opened
                        if len(driver.window_handles) > 1:
                            new_handles = [h for h in driver.window_handles if h != original_handle]
                            if new_handles:
                                driver.switch_to.window(new_handles[0])
                                time.sleep(2)
                                driver.close()
                                driver.switch_to.window(original_handle)
                        
                        downloaded_list.append(link)
                        with open('downloaded_list.json', 'w') as f:
                            json.dump(downloaded_list, f, indent=2)
                    except Exception as e:
                        print(f"  Error clicking button for {link}: {str(e)}")
                        # Continue to next link
                
                # Try to go to next page
                print(f"\nGoing to next page...")
                current_page += 1
                next_url = BASE_URL + f"?page={current_page}"
                print(f"Navigating to: {next_url}")
                driver.get(next_url)
                time.sleep(5)
        else:
            # Download movie zips (original logic)
            while True:
                current_page_url = driver.current_url
                print(f"\n{'='*60}")
                print(f"Processing Page {current_page}")
                print(f"URL: {current_page_url}")
                print(f"{'='*60}")
                
                # Get all movie links on current page
                movie_links = scrape_page()
                
                if not movie_links:
                    print("No movies found on this page. Exiting.")
                    break
                
                print(f"Found {len(movie_links)} movies on this page\n")
                
                # Download each movie
                for idx, (movie_name, movie_url) in enumerate(movie_links, 1):
                    if movie_url in downloaded_list:
                        print(f"  Skipping {movie_name} (already downloaded)")
                        continue
                    
                    print(f"[{idx}/{len(movie_links)}] Processing: {movie_name}")
                    
                    try:
                        # Click on the movie link
                        print(f"  Opening: {movie_url}")
                        driver.get(movie_url)
                        time.sleep(3)
                        
                        # Download the zip file
                        download_success = download_movie_zip(movie_name)
                        
                        # Add to downloaded list only if download was successful
                        if download_success:
                            downloaded_list.append(movie_url)
                            with open('downloaded_list.json', 'w') as f:
                                json.dump(downloaded_list, f, indent=2)
                        
                        # Close the new tab opened by download_movie_zip
                        if len(driver.window_handles) > 1:
                            driver.close()  # Close current tab
                            driver.switch_to.window(driver.window_handles[0])  # Switch back to main tab
                        print(f"  Going back to the music list...")
                        driver.get(current_page_url)
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"  Error processing {movie_name}: {str(e)}")
                        # Do not add to list on error to allow retry
                        try:
                            driver.get(current_page_url)
                        except:
                            pass
                        time.sleep(2)
                
                # Try to go to next page
                print(f"\nLooking for next page...")
                if not go_to_next_page():
                    print("Reached the last page or no next button found. Exiting.")
                    break
                
                current_page += 1
        
        print("\n" + "="*60)
        print("Download process completed!")
        print(f"Files saved to: {DOWNLOAD_FOLDER}")
        print("="*60)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
