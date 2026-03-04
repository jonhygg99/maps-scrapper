"""
Stealth Techniques for Browser Automation
Anti-detection measures to avoid being blocked
"""
from playwright.async_api import Page
import random


async def apply_stealth_techniques(page: Page):
    """
    Apply various stealth techniques to avoid detection
    
    Args:
        page: Playwright page object
    """
    
    # Override navigator.webdriver
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    # Override permissions
    await page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    # Override plugins
    await page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                    description: "",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                },
                {
                    0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin},
                    1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin},
                    description: "",
                    filename: "internal-nacl-plugin",
                    length: 2,
                    name: "Native Client"
                }
            ],
        });
    """)
    
    # Override languages
    await page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)
    
    # Override platform
    await page.add_init_script("""
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
    """)
    
    # Override chrome property
    await page.add_init_script("""
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    """)
    
    # Override notification permissions
    await page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    # Add realistic mouse movements (can be called when needed)
    await page.add_init_script("""
        // Make automation harder to detect
        delete navigator.__proto__.webdriver;
    """)
    
    # Randomize canvas fingerprint
    await page.add_init_script("""
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.apply(this, [parameter]);
        };
    """)
    
    # Override screen properties to look more realistic
    await page.add_init_script("""
        Object.defineProperty(screen, 'colorDepth', {
            get: () => 24
        });
        Object.defineProperty(screen, 'pixelDepth', {
            get: () => 24
        });
    """)


async def random_mouse_movement(page: Page, x: int, y: int):
    """
    Simulate human-like mouse movement
    
    Args:
        page: Playwright page object
        x: Target x coordinate
        y: Target y coordinate
    """
    # Get current position (assuming center of screen as start)
    steps = random.randint(10, 30)
    
    for i in range(steps):
        # Add some randomness to the path
        current_x = x * (i / steps) + random.randint(-5, 5)
        current_y = y * (i / steps) + random.randint(-5, 5)
        
        await page.mouse.move(current_x, current_y)
        await page.wait_for_timeout(random.randint(5, 15))


async def random_scroll(page: Page, direction: str = "down", distance: int = 100):
    """
    Simulate human-like scrolling
    
    Args:
        page: Playwright page object
        direction: 'up' or 'down'
        distance: Distance to scroll in pixels
    """
    scroll_amount = distance if direction == "down" else -distance
    steps = random.randint(5, 15)
    
    for i in range(steps):
        await page.mouse.wheel(0, scroll_amount // steps)
        await page.wait_for_timeout(random.randint(10, 50))
