import time
import logging
import pyperclip
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt

URL: str = "https://duck.ai/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[type="submit"][aria-label="Send"]'
ANSWER_XPATH: str = "//div[@heading]"


def check_if_chat_loaded(driver) -> bool:
    driver.implicitly_wait(5)
    try:
        button = driver.find_element(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    except Exception as e:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


def initialize_driver(config: Config):
    logging.info("Initializing browser for DeepSeek...")
    driver = create_driver(config)
    driver.get(URL)

    while not check_if_chat_loaded(driver):
        logging.info("Waiting for chat interface to load...")
        time.sleep(5)
    logging.info("Browser initialized")
    return driver


def send_request_and_get_response(driver, message):
    logging.debug("Send request to chatbot interface")
    driver.implicitly_wait(10)
    textarea = driver.find_element(By.TAG_NAME, "textarea")
    transfer_prompt(message, textarea)
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)))
    time.sleep(1)
    submit_buttons = driver.find_elements(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    submit_button = submit_buttons[-1]
    logging.debug("Push submit button")
    submit_button.click()

    # Wait a little time to avoid early fail.
    time.sleep(1)

    # Wait for submit button to be available. It means answer is finished.
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)))
    scroll_down(driver)
    message = ""
    remaining_attemps = 5
    while not message and remaining_attemps > 0:
        time.sleep(1)
        message = get_answer_from_copy_button(driver)
        remaining_attemps -= 1

    if not message:
        logging.warning("No message found.")
        return ""
    clean_message = clean_chat_answer(message)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


def scroll_down(driver):
    form_element = driver.find_element(By.XPATH, "//form[@autocomplete='off']")
    div_element = form_element.find_element(By.XPATH, "./ancestor::div[1]")
    if scrollable_div := div_element.find_element(By.TAG_NAME, "div"):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    else:
        logging.warning("No scrollable div found.")


def get_answer_from_copy_button(driver) -> str:
    message_bubbles = driver.find_elements(By.XPATH, ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    copy_button = last_message_bubble.find_element(By.XPATH, "//*[@data-copyairesponse='true']")
    try:
        copy_button.click()
    except Exception as e:
        logging.warning("Error clicking copy button:", e)
        return ""
    return pyperclip.paste()


def clean_chat_answer(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def main():
    driver = initialize_driver(Config())
    try:
        while True:
            user_request = input("Ask something (or 'quit'): ")
            if user_request.lower() == "quit":
                break
            response = send_request_and_get_response(driver, user_request)
            print("Answer:", response)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
