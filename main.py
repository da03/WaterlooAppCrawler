from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from selenium.webdriver.support.ui import Select
import csv
from selenium.common.exceptions import NoSuchElementException


def get_page_content(url):
    firefox_options = webdriver.FirefoxOptions()
    # firefox_options.add_argument('-headless')  # Uncomment for headless mode
    # Initialize Firefox WebDriver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
    try:
        driver.get(url)
        time.sleep(1)
        content = driver.page_source

        username = os.getenv('WATERLOOEMAIL')
        password = os.getenv('WATERLOOPASSWORD')

        # Wait for the username input to be visible and enter the username
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "userNameInput"))).send_keys(username)

        time.sleep(1)
        # Click the 'Next' button
        driver.find_element(By.ID, "nextButton").click()

        # Wait for the password input to be visible and enter the password
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "passwordInput"))).send_keys(password)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "submitButton"))).click()

        wait = WebDriverWait(driver, 30)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "p.loader-text"), "Waiting for approval..."))
        yes_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "trust-browser-button"))
        )
        # Click the "Yes, this is my device" button
        time.sleep(1)
        yes_button.click()
        
        # Wait for the cookie consent popup "Accept all" button within the 'popup-buttons' div
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#popup-buttons .agree-button"))
        )
        time.sleep(1)
        accept_cookies_button.click()
        ### Click the "List Applications" link
        list_applications_link = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "List Applications"))
        )
        time.sleep(1)
        list_applications_link.click()

        #dropdown = WebDriverWait(driver, 10).until(
        #    EC.visibility_of_element_located((By.NAME, "plans"))
        #)


        # Function to process applications for a given plan
        def process_applications(plan):
            dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "plans"))
            )
            # Select the plan (CSD or CSM)
            select = Select(dropdown)
            select.select_by_value(plan)
        
            # Click the search button
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-input[type='submit']"))
            )
            time.sleep(1)
            search_button.click()
        
            # Wait for results to load
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
            time.sleep(20)
        
            # Collect all application links
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
            application_links = driver.find_elements(By.XPATH, "//tbody//a[contains(@href, '../view/')]")
            link_urls = [link.get_attribute('href') for link in application_links]
        
            # Process each application
            for href in link_urls:
                time.sleep(1)
                driver.get(href)
                #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Subplans:')]")))
                WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{plan}')]"))
                )
                h1_text, subplans, supervisor = extract_details()
                writer.writerow([href, plan, subplans, supervisor, h1_text])
        ###select = Select(dropdown)
        
        #### Select the option by its value
        ###select.select_by_value("CSD")
        ###
        #### Wait for the "Search" button to be clickable and then click it
        ###search_button = WebDriverWait(driver, 10).until(
        ###    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-input[type='submit']"))
        ###)
        ###time.sleep(1)
        ###search_button.click()
        ###time.sleep(10)
        ####wait = WebDriverWait(driver, 10)
        ####wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        ###WebDriverWait(driver, 10).until(
        ###    EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        ###)
        ###
        #### Find all anchor tags within the table
        ###application_links = driver.find_elements(By.XPATH, "//tbody//a[contains(@href, '../view/')]")
        ###
        #### Extract the href attribute from each link
        ###link_urls = [link.get_attribute('href') for link in application_links]
        ###
        #### Now you have all the application links
        ###print(link_urls)

        # Function to extract Subplans and Requested Supervisor
        def extract_details():
            try:
                h1_text = driver.find_element(By.CSS_SELECTOR, ".uw-site--title h1").text
            except NoSuchElementException:
                h1_text = ""  # Set to empty string if not found
            try:
                # Extracting Subplans
                subplans = driver.find_element(By.XPATH, "//th[contains(text(), 'Subplans:')]/following-sibling::td").text
            except NoSuchElementException:
                # If Subplans is not found, set to empty
                subplans = ""
        
            try:
                # Extracting Requested Supervisor
                supervisor = driver.find_element(By.XPATH, "//th[contains(text(), 'Requested Supervisor:')]/following-sibling::td").text
            except NoSuchElementException:
                # If Requested Supervisor is not found, set to empty
                supervisor = ""
        
            return h1_text, subplans, supervisor
        with open('applications_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Link', 'Plan', 'Subplans', 'Supervisor', 'Name'])

            # Process CSD applications
            process_applications("CSD")
            # Navigate back to the search page to process CSM applications
            driver.get("https://odyssey.uwaterloo.ca/grad/list/")
            process_applications("CSM") 
        #### Open a CSV file to write the data
        ###with open('applications_data.csv', 'w', newline='', encoding='utf-8') as file:
        ###    writer = csv.writer(file)
        ###    # Writing the header
        ###    writer.writerow(['Link', 'Subplans', 'Supervisor'])
        ###
        ###    # Find all application links and iterate through them
        ###    application_links = driver.find_elements(By.XPATH, "//tbody//a[contains(@href, '../view/')]")
        ###    link_urls = [link.get_attribute('href') for link in application_links]
        ###    for href in link_urls:
        ###        #href = link.get_attribute('href')
        ###        # Open each link
        ###        driver.get(href)
        ###
        ###        # Wait for the specific elements to be loaded
        ###        WebDriverWait(driver, 20).until(
        ###            EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Subplans:')]"))
        ###        )
        ###
        ###        # Extract the required details
        ###        subplans, supervisor = extract_details()
        ###
        ###        # Write the data to the CSV file
        ###        writer.writerow([href, subplans, supervisor])

        return content
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Closing the browser
        driver.quit()


def main():
    url = 'https://odyssey.uwaterloo.ca/grad/'
    page_content = get_page_content(url)

if __name__ == "__main__":
    main()
