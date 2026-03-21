import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests

# Configuration
BASE_URL = "https://www.isaiminihq.com/music/ilayaraja-songs/"
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "Ilayaraja_Songs")

# Create download folder if it doesn't exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configure Chrome to download to our folder
chrome_options = Options()
prefs = {
    "download.default_directory": DOWNLOAD_FOLDER,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(30)

def download_movie_zip(movie_name):
    """Download the zip file for a movie"""
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
        print(f"  Warning: Could not find 'Download Single Zip' button for {movie_name}: {str(e)}")
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
            print(f"  Error: Could not find download button")
            return False

def scrape_page():
    """Get all movie links from current page"""
    try:
        # Wait for any links to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )
        
        # Find all links on the page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        # Filter for movie/content links (not navigation, pagination, etc)
        links = []
        for link in all_links:
            href = link.get_attribute("href")
            text = link.text.strip()
            
            # Skip empty links, pagination links, and navigation links
            if (href and text and 
                "isaiminihq.com" in href and 
                href != BASE_URL and
                not any(x in text.lower() for x in ["next", "previous", "home", "←", "→", "|"])):
                
                # Check if it's not a duplicate
                if not any(link[1] == href for link in links):
                    links.append((text, href))
        
        print(f"  Found {len(links)} movie links")
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
            time.sleep(3)
            return True
        else:
            return False
    except Exception as e:
        print(f"No next page found: {str(e)}")
        return False

def main():
    """Main automation function"""
    try:
        # Navigate to the starting URL
        print("Loading the webpage...")
        driver.get(BASE_URL)
        time.sleep(4)
        
        current_page = 1
        
        while True:
            print(f"\n{'='*60}")
            print(f"Processing Page {current_page}")
            print(f"URL: {driver.current_url}")
            print(f"{'='*60}")
            
            # Get all movie links on current page
            movie_links = scrape_page()
            
            if not movie_links:
                print("No movies found on this page. Exiting.")
                break
            
            print(f"Found {len(movie_links)} movies on this page\n")
            
            # Download each movie
            for idx, (movie_name, movie_url) in enumerate(movie_links, 1):
                print(f"[{idx}/{len(movie_links)}] Processing: {movie_name}")
                
                try:
                    # Click on the movie link
                    print(f"  Opening: {movie_url}")
                    driver.get(movie_url)
                    time.sleep(3)
                    
                    # Download the zip file
                    download_movie_zip(movie_name)
                    
                    # Close the new tab opened by download_movie_zip
                    if len(driver.window_handles) > 1:
                        driver.close()  # Close current tab
                        driver.switch_to.window(driver.window_handles[0])  # Switch back to main tab
                    print(f"  Going back to the music list...")
                    if driver.current_url != BASE_URL:
                        driver.get(BASE_URL)
                        time.sleep(3)
                    
                except Exception as e:
                    print(f"  Error processing {movie_name}: {str(e)}")
                    try:
                        driver.get(BASE_URL)
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
