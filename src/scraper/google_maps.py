"""
Google Maps Scraper with Anti-Detection
Uses Playwright with stealth techniques
"""
import asyncio
import random
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from src.utils.logging import Logger
from src.scraper.stealth import apply_stealth_techniques


class GoogleMapsScraper:
    """Main scraper class for Google Maps"""
    
    # Windows desktop user agents (Chrome on Windows 10/11)
    WINDOWS_DESKTOP_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    ]
    
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        timeout: int = 30000,
        viewport_width: int = 1920,
        viewport_height: int = 1080
    ):
        """
        Initialize Google Maps scraper
        
        Args:
            headless: Run browser in headless mode
            proxy: Proxy URL (format: http://host:port)
            timeout: Page load timeout in milliseconds
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
        """
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.logger = Logger.get_logger("GoogleMapsScraper")
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def initialize(self):
        """Initialize browser and context"""
        try:
            self.playwright = await async_playwright().start()
            
            # Browser launch arguments
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
            
            # Launch browser
            launch_options = {
                'headless': self.headless,
                'args': browser_args,
                'timeout': 60000  # Increase launch timeout to 60 seconds
            }
            
            if self.proxy:
                launch_options['proxy'] = {'server': self.proxy}
                self.logger.info(f"Using proxy: {self.proxy}")
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Select random Windows desktop user agent
            user_agent = random.choice(self.WINDOWS_DESKTOP_USER_AGENTS)
            self.logger.info(f"Using Windows desktop user agent")
            
            # Create context with stealth settings
            self.context = await self.browser.new_context(
                viewport={
                    'width': self.viewport_width,
                    'height': self.viewport_height
                },
                user_agent=user_agent,
                locale='en-US',  # Force English locale
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',  # Force English language
                }
            )
            
            self.logger.info("Browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            raise
    
    async def create_page(self) -> Page:
        """Create a new page with stealth techniques applied"""
        if not self.context:
            await self.initialize()
        
        page = await self.context.new_page()
        page.set_default_timeout(self.timeout)
        
        # Apply stealth techniques
        await apply_stealth_techniques(page)
        
        return page
    
    async def search_location(self, page: Page, query: str):
        """
        Search for a location on Google Maps
        
        Args:
            page: Playwright page object
            query: Search query (e.g., "restaurants in New York")
        """
        try:
            self.logger.info(f"Searching for: {query}")
            
            # Navigate to Google Maps with ENGLISH LANGUAGE (append ?hl=en)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await page.goto(
                        'https://www.google.com/maps/?hl=en',  # Force English
                        wait_until='domcontentloaded',
                        timeout=60000  # 60 seconds
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Retry {attempt + 1}/{max_retries} for navigation")
                        await asyncio.sleep(2)
                    else:
                        raise
            
            # Random delay to appear human-like
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # Dismiss prompt by closing and recreating page if necessary
            page = await self._handle_app_prompt(page)
            
            # Find search box and type query
            await self._perform_search(page, query)
            
            self.logger.info("Waiting for search results to load...")
            
            # Wait for results to appear - try multiple strategies
            results_loaded = False
            
            # Strategy 1: Wait for the feed/results panel
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=15000)
                self.logger.info("Results feed loaded")
                results_loaded = True
            except:
                self.logger.warning("Feed selector timeout, trying alternative...")
            
            # Strategy 2: Wait for any result cards
            if not results_loaded:
                try:
                    await page.wait_for_selector('a[href*="/maps/place/"]', timeout=15000)
                    self.logger.info("Result cards detected")
                    results_loaded = True
                except:
                    self.logger.warning("Result cards timeout, trying alternative...")
            
            # Strategy 3: Wait for network to settle
            if not results_loaded:
                try:
                    await page.wait_for_load_state('networkidle', timeout=20000)
                    self.logger.info("Network settled")
                    results_loaded = True
                except:
                    self.logger.warning("Network idle timeout")
            
            # Additional wait for rendering
            await asyncio.sleep(random.uniform(3, 5))
            
            if results_loaded:
                self.logger.info(f"Search completed successfully for: {query}")
            else:
                self.logger.warning(f"Search may not have loaded completely for: {query}")
            
        except Exception as e:
            self.logger.error(f"Error searching location: {e}")
            raise
    
    async def extract_businesses(self, page: Page, max_results: int = 20) -> List[Dict]:
        """
        Extract business information from search results.
        Clicks on each listing to get full details from the detail panel.
        
        Args:
            page: Playwright page object
            max_results: Maximum number of results to extract
            
        Returns:
            List of dictionaries containing business data
        """
        try:
            self.logger.info(f"Extracting up to {max_results} results")
            
            results = []
            
            # Wait for results to load
            self.logger.info("Waiting for place listings...")
            await asyncio.sleep(3)
            
            # Wait for place links to appear
            try:
                await page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)
                self.logger.info("Place listings found")
            except:
                self.logger.error("No place listings found!")
                await page.screenshot(path="logs/debug_screenshot.png")
                return []
            
            # Hover over first result to ensure panel is active
            try:
                first_link = page.locator('a[href*="/maps/place/"]').first
                await first_link.hover()
                await asyncio.sleep(1)
            except:
                pass
            
            # Scroll to load all requested results
            self.logger.info(f"Scrolling to load {max_results} results...")
            previously_counted = 0
            scroll_attempts = 0
            max_scroll_attempts = 20
            
            while scroll_attempts < max_scroll_attempts:
                # Count current results
                current_count = await page.locator('a[href*="/maps/place/"]').count()
                self.logger.info(f"Currently found: {current_count} listings")
                
                # Stop if we have enough
                if current_count >= max_results:
                    self.logger.info(f"Reached target of {max_results} listings")
                    break
                
                # Stop if no new results after scroll
                if current_count == previously_counted:
                    self.logger.info("No new results found, stopping scroll")
                    break
                
                previously_counted = current_count
                
                # Scroll the results panel
                try:
                    await page.mouse.wheel(0, 10000)
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                    scroll_attempts += 1
                except Exception as e:
                    self.logger.warning(f"Scroll error: {e}")
                    break
            
            # Get all listing links (limit to max_results)
            all_links = await page.locator('a[href*="/maps/place/"]').all()
            total_found = len(all_links)
            listings_to_process = all_links[:max_results]
            
            self.logger.info(f"Total found: {total_found}, processing: {len(listings_to_process)}")
            
            # Click each listing and extract details
            for idx, listing_link in enumerate(listings_to_process):
                try:
                    self.logger.info(f"Processing listing {idx+1}/{len(listings_to_process)}")
                    
                    # Get the parent element (the actual clickable card)
                    listing = listing_link.locator('xpath=..')
                    
                    # Click the listing
                    await listing.click()
                    
                    # Wait for detail panel to load
                    try:
                        await page.wait_for_selector('h1.DUwDvf', timeout=10000)
                        await asyncio.sleep(random.uniform(1.5, 2.5))  # Let details load
                    except:
                        self.logger.warning(f"Detail panel timeout for listing {idx+1}")
                        continue
                    
                    # Extract data from detail panel
                    data = await self._extract_from_detail_panel(page)
                    
                    if data and data.get('name'):
                        results.append(data)
                        self.logger.info(f"+ Extracted: {data.get('name')}")
                    else:
                        self.logger.warning(f"- No data extracted for listing {idx+1}")
                    
                    # Small delay before next
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    self.logger.warning(f"Error processing listing {idx+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting businesses: {e}")
            return []
    
    async def _handle_app_prompt(self, page: Page):
        """
        Handle app prompt by closing and recreating page until proper interface loads.
        Detects multiple interface types:
        1. Standard desktop interface with input#searchboxinput (OLD - deprecated)
        2. New desktop interface with input[name="q"] and aria-controls (CURRENT)
        3. Mobile-like interface with div.JdG3E button (BAD - needs reload)
        4. Cookie/consent pages that need to be dismissed
        """
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            await asyncio.sleep(2.0)  # Wait for page to stabilize
            
            # First, handle any cookie/consent prompts
            await self._handle_cookie_consent(page)
            
            # Check if we have the NEW interface (current Google Maps)
            try:
                new_search_input = page.locator('input[name="q"][role="combobox"]').first
                if await new_search_input.is_visible(timeout=2000):
                    self.logger.info("+ New desktop interface loaded (with input[name='q'])")
                    return page
            except:
                pass
            
            # Check if we have the OLD interface (legacy)
            try:
                old_search_input = page.locator('input#searchboxinput').first
                if await old_search_input.is_visible(timeout=2000):
                    self.logger.info("+ Legacy desktop interface loaded (with searchboxinput)")
                    return page
            except:
                pass
            
            # Check if we have the BAD interface (mobile-like with button div)
            try:
                mobile_button = page.locator('div.JdG3E[role="button"]').first
                if await mobile_button.is_visible(timeout=2000):
                    self.logger.warning("- Mobile-like interface detected (no proper input element)")
                    # This is the wrong interface - need to reload
                    attempt += 1
                    self.logger.info(f"Recreating page to get desktop interface (attempt {attempt}/{max_attempts})...")
                    
                    # Close and recreate page
                    await page.close()
                    page = await self.context.new_page()
                    page.set_default_timeout(self.timeout)
                    
                    from src.scraper.stealth import apply_stealth_techniques
                    await apply_stealth_techniques(page)
                    
                    await page.goto(
                        'https://www.google.com/maps/?hl=en',
                        wait_until='domcontentloaded',
                        timeout=60000
                    )
                    
                    await asyncio.sleep(random.uniform(2.0, 3.0))
                    continue
            except:
                pass
            
            # Check for app prompt modals
            prompt_selectors = [
                'div.zc8u2b',  # Modal overlay
                'div.FovMle',  # Alternative modal  
                'button:has-text("Stay on web")',
                'button:has-text("Rester sur le Web")',
                'button.qgMOee',
                'button:has-text("Use the Google Maps app")',  # "Use app" prompt
            ]
            
            prompt_found = False
            for selector in prompt_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=1000):
                        prompt_found = True
                        self.logger.warning(f"App prompt detected: {selector}")
                        break
                except:
                    continue
            
            if prompt_found:
                # Prompt found - close page and create new one
                attempt += 1
                self.logger.info(f"Creating fresh page to avoid prompt (attempt {attempt}/{max_attempts})...")
                
                try:
                    await page.close()
                    page = await self.context.new_page()
                    page.set_default_timeout(self.timeout)
                    
                    from src.scraper.stealth import apply_stealth_techniques
                    await apply_stealth_techniques(page)
                    
                    await page.goto(
                        'https://www.google.com/maps/?hl=en',
                        wait_until='domcontentloaded',
                        timeout=60000
                    )
                    
                    await asyncio.sleep(random.uniform(2.0, 3.0))
                    
                except Exception as e:
                    self.logger.error(f"Error recreating page: {e}")
                    raise
            else:
                # No prompt and no clear interface detected - wait a bit more
                self.logger.warning("Interface unclear, waiting for elements to load...")
                await asyncio.sleep(2)
                attempt += 1
        
        # If still wrong interface after max attempts, log warning but continue
        self.logger.warning(f"Could not load proper interface after {max_attempts} attempts. Continuing anyway...")
        return page
    
    async def _handle_cookie_consent(self, page: Page):
        """
        Handle cookie/consent prompts that may appear on Google Maps
        """
        try:
            # Look for common cookie consent buttons and accept them
            consent_selectors = [
                'button:has-text("Accept all")',
                'button:has-text("Accept")', 
                'button:has-text("Agree")',
                'button:has-text("I agree")',
                'button[aria-label*="Accept"]',
                'button[aria-label*="Agree"]',
                'input[type="button"][value*="Accept"]',
                'div[role="button"]:has-text("Accept")',
                # Spanish alternatives
                'button:has-text("Aceptar todo")',
                'button:has-text("Aceptar")',
                # French alternatives  
                'button:has-text("Tout accepter")',
                'button:has-text("Accepter")',
            ]
            
            for selector in consent_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        self.logger.info(f"Clicking consent button: {selector}")
                        await button.click()
                        await asyncio.sleep(1.0)
                        break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error handling cookie consent: {e}")
            # Don't raise - this is a best-effort operation
    
    async def _perform_search(self, page: Page, query: str):
        """
        Perform search by finding input box and typing query.
        Handles multiple interface types:
        1. NEW interface with input[name="q"][role="combobox"] (current 2026)
        2. OLD interface with input#searchboxinput (legacy)
        3. Mobile-like interface with div button (fallback)
        """
        try:
            # STRATEGY 1: Try NEW interface first (current Google Maps 2026)
            new_search_selectors = [
                'input[name="q"][role="combobox"]',  # Current interface
                'input[aria-controls*="ucc-"]',  # Alternative new interface selector
                'input[name="q"]',  # Fallback for name attribute
            ]
            
            search_box = None
            for selector in new_search_selectors:
                try:
                    search_box = page.locator(selector).first
                    if await search_box.is_visible(timeout=3000):
                        self.logger.info(f"+ Found new search input: {selector}")
                        
                        # Type query with human-like delays
                        await search_box.click()
                        await asyncio.sleep(0.5)
                        await search_box.fill('')
                        await asyncio.sleep(0.3)
                        
                        for char in query:
                            await search_box.type(char, delay=random.randint(80, 200))
                        
                        await asyncio.sleep(1.0)
                        await search_box.press('Enter')
                        
                        self.logger.info("Search query submitted via new interface")
                        return
                        
                except:
                    continue
            
            # STRATEGY 2: Try OLD interface (legacy)
            old_search_selectors = [
                'input#searchboxinput',
                'input[name="q"]',
                'input[aria-label*="Search"]',
                'input[placeholder*="Search"]',
            ]
            
            for selector in old_search_selectors:
                try:
                    search_box = page.locator(selector).first
                    if await search_box.is_visible(timeout=3000):
                        self.logger.info(f"+ Found old search input: {selector}")
                        
                        # Type query with human-like delays
                        await search_box.click()
                        await asyncio.sleep(0.5)
                        await search_box.fill('')
                        await asyncio.sleep(0.3)
                        
                        for char in query:
                            await search_box.type(char, delay=random.randint(80, 200))
                        
                        await asyncio.sleep(1.0)
                        await search_box.press('Enter')
                        
                        self.logger.info("Search query submitted via old interface")
                        return
                        
                except:
                    continue
            
            # STRATEGY 3: Try mobile-like interface (button that opens search)
            self.logger.warning("Standard inputs not found, trying mobile-like interface...")
            
            try:
                # Look for the button-like div with "Find a place" text
                mobile_search_button = page.locator('div.JdG3E[role="button"]').first
                if await mobile_search_button.is_visible(timeout=3000):
                    self.logger.info("Found mobile-like search button, clicking to open input...")
                    
                    # Click the button to reveal actual input
                    await mobile_search_button.click()
                    await asyncio.sleep(1.0)
                    
                    # Now try to find the actual input that should appear
                    combined_selectors = new_search_selectors + old_search_selectors
                    for selector in combined_selectors:
                        try:
                            search_box = page.locator(selector).first
                            if await search_box.is_visible(timeout=2000):
                                self.logger.info(f"Input appeared after click: {selector}")
                                
                                # Type query
                                await search_box.fill('')
                                await asyncio.sleep(0.3)
                                
                                for char in query:
                                    await search_box.type(char, delay=random.randint(80, 200))
                                
                                await asyncio.sleep(1.0)
                                await search_box.press('Enter')
                                
                                self.logger.info("Search query submitted via mobile interface")
                                return
                        except:
                            continue
            except Exception as e:
                self.logger.error(f"Mobile interface fallback failed: {e}")
            
            # STRATEGY 4: Last resort - try any visible input
            self.logger.warning("Trying last resort - any visible input...")
            try:
                all_inputs = page.locator('input:visible')
                count = await all_inputs.count()
                for i in range(min(count, 10)):  # Check first 10 visible inputs
                    try:
                        search_box = all_inputs.nth(i)
                        input_type = await search_box.get_attribute('type')
                        if input_type in ['text', 'search', ''] or input_type is None:
                            self.logger.info(f"Trying fallback input {i} with type: {input_type}")
                            
                            await search_box.click()
                            await asyncio.sleep(0.5)
                            await search_box.fill('')
                            await asyncio.sleep(0.3)
                            
                            for char in query:
                                await search_box.type(char, delay=random.randint(80, 200))
                            
                            await asyncio.sleep(1.0)
                            await search_box.press('Enter')
                            
                            self.logger.info("Search query submitted via fallback input")
                            return
                    except:
                        continue
            except Exception as e:
                self.logger.error(f"Last resort fallback failed: {e}")
            
            # If we get here, nothing worked
            raise Exception("Could not find any search interface (tried new, old, mobile, and fallback strategies)")
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            # Take screenshot for debugging
            try:
                await page.screenshot(path="logs/search_error.png")
                self.logger.info("Screenshot saved to logs/search_error.png")
                # Log page HTML for debugging
                page_html = await page.content()
                with open("logs/search_error.html", "w", encoding="utf-8") as f:
                    f.write(page_html)
                self.logger.info("Page HTML saved to logs/search_error.html")
            except:
                pass
            raise
    
    async def _extract_from_detail_panel(self, page: Page) -> Optional[Dict]:
        """
        Extract business data from the detail panel (after clicking a listing).
        Uses stable XPath selectors based on working implementation.
        """
        try:
            import re
            data = {}
            
            # Name
            try:
                name_elem = page.locator('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]').first
                data['name'] = await name_elem.inner_text(timeout=2000)
            except:
                data['name'] = None
            
            # Address
            try:
                address_elem = page.locator('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]').first
                data['address'] = await address_elem.inner_text(timeout=2000)
            except:
                data['address'] = None
            
            # Website
            try:
                website_elem = page.locator('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]').first
                data['website'] = await website_elem.inner_text(timeout=2000)
            except:
                data['website'] = None
            
            # Phone
            try:
                phone_elem = page.locator('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]').first
                data['phone'] = await phone_elem.inner_text(timeout=2000)
            except:
                data['phone'] = None
            
            # Reviews Count
            try:
                reviews_elem = page.locator('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]').first
                reviews_text = await reviews_elem.get_attribute('aria-label', timeout=2000)
                if reviews_text:
                    # Remove special characters and parse
                    clean_text = reviews_text.replace('\xa0', '').replace('(', '').replace(')', '').replace(',', '')
                    match = re.search(r'(\d+)', clean_text)
                    if match:
                        data['reviews'] = match.group(1)
                else:
                    data['reviews'] = None
            except:
                data['reviews'] = None
            
            # Reviews Average (Rating)
            try:
                rating_elem = page.locator('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]').first
                rating_text = await rating_elem.inner_text(timeout=2000)
                if rating_text:
                    # Clean and parse rating
                    clean_rating = rating_text.replace(' ', '').replace(',', '.')
                    data['rating'] = clean_rating
                else:
                    data['rating'] = None
            except:
                data['rating'] = None
            
            # Category/Place Type
            try:
                type_elem = page.locator('//div[@class="LBgpqf"]//button[@class="DkEaL "]').first
                data['category'] = await type_elem.inner_text(timeout=2000)
            except:
                data['category'] = None
            
            # Hours/Opens At
            try:
                hours_elem = page.locator('//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]').first
                hours_text = await hours_elem.inner_text(timeout=2000)
                if hours_text:
                    # Parse "Open ⋅ Closes 10 PM" format
                    parts = hours_text.split('⋅')
                    if len(parts) > 1:
                        data['hours'] = parts[1].replace("\u202f", "").strip()
                    else:
                        data['hours'] = hours_text.replace("\u202f", "").strip()
                else:
                    # Try alternative selector
                    hours_elem2 = page.locator('//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]').first
                    hours_text2 = await hours_elem2.inner_text(timeout=2000)
                    if hours_text2:
                        parts = hours_text2.split('⋅')
                        if len(parts) > 1:
                            data['hours'] = parts[1].replace("\u202f", "").strip()
                        else:
                            data['hours'] = hours_text2.replace("\u202f", "").strip()
                    else:
                        data['hours'] = None
            except:
                data['hours'] = None
            
            # Price Level (from info sections)
            try:
                # Check LTs0Rc divs for price info
                for i in range(1, 4):
                    try:
                        info_elem = page.locator(f'//div[@class="LTs0Rc"][{i}]').first
                        info_text = await info_elem.inner_text(timeout=1000)
                        if info_text and '$' in info_text:
                            # Extract price symbols
                            price_match = re.search(r'(\$+|\$[\d\+\-–]+)', info_text)
                            if price_match:
                                data['price_level'] = price_match.group(1)
                                break
                    except:
                        continue
                
                if 'price_level' not in data:
                    data['price_level'] = None
            except:
                data['price_level'] = None
            
            # Introduction/Description
            try:
                intro_elem = page.locator('//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]').first
                data['introduction'] = await intro_elem.inner_text(timeout=2000)
            except:
                data['introduction'] = None
            
            # Service options (delivery, pickup, etc.)
            try:
                service_info = {
                    'store_shopping': 'No',
                    'in_store_pickup': 'No',
                    'store_delivery': 'No'
                }
                
                for i in range(1, 4):
                    try:
                        info_elem = page.locator(f'//div[@class="LTs0Rc"][{i}]').first
                        info_text = await info_elem.inner_text(timeout=1000)
                        if info_text:
                            parts = info_text.split('·')
                            if len(parts) > 1:
                                check = parts[1].replace("\n", "").lower()
                                if 'shop' in check:
                                    service_info['store_shopping'] = 'Yes'
                                if 'pickup' in check:
                                    service_info['in_store_pickup'] = 'Yes'
                                if 'delivery' in check:
                                    service_info['store_delivery'] = 'Yes'
                    except:
                        continue
                
                data.update(service_info)
            except:
                pass
            
            # Clean up data
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.strip()
            
            return data if data.get('name') else None
            
        except Exception as e:
            self.logger.debug(f"Error extracting from detail panel: {e}")
            return None
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("Browser closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
