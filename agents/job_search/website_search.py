from playwright.sync_api import sync_playwright


''' : ========== Open chrome and go to Well Found website ===================== :'''

with sync_playwright() as p :

    browser = p.chromium.launch(headless = False ) # headless --> Faster and not shown in the screen 

    page = browser.new_page()

    page.goto("https://wellfound.com/jobs")

    input("Press enter to close...")

    print(page.title())

    print(page.content()[:5000])

    input("Press Enter")

    browser.close()