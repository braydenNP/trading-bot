import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

def getAuth(username, password, pin):
    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    options = Options()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=options)

    # Go to the login page
    driver.get("https://ic.cgsi.com")  # Open the site you want to monitor

    # Fetch performance logs from Chrome DevTools Protocol
    logs = driver.get_log("performance")

    # Optional: wait for page and JS to load fully
    time.sleep(2)

    # Locate and fill the username and password fields
    driver.find_element(By.NAME, "cic_username").send_keys(username)
    driver.find_element(By.NAME, "cic_password").send_keys(password)

    # Submit the form (adjust this depending on how the site handles login)
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    driver.execute_script("arguments[0].style.display = 'block';", submit_button)
    submit_button.click()


    # Wait for login to complete (adjust timing or use WebDriverWait for better control)
    time.sleep(3)

    pinInputField = driver.find_element(By.ID, 'pinInputField')
    pinInputField.send_keys(pin)

    time.sleep(2)

    print(driver.current_url)

    logs = driver.get_log("performance")

    auth = ''
    accountid = ''
    for entry in logs:
        message = json.loads(entry["message"])["message"]
        
        if message["method"] == "Network.requestWillBeSent":
            request = message["params"]["request"]
            url = request.get("url", "")
            if "ic.cgsi.com/api/v1/" in url:
                headers = request.get("headers", {})
                for k, v in headers.items():
                    print(f"  {k}: {v}")
                    if 'Bearer' in v:
                        auth = v
                    if 'CGSI_' in v:
                        accountid = v

    driver.quit()
    if auth != '':
        return auth
    else:
        return ''