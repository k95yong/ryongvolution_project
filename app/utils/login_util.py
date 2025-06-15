import json
import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils.path_util import get_root_dir
from app.utils.log_util import logger

YOUTUBE_ID = "ykim7928@gmail.com"
YOUTUBE_PW = "dydehfdl1!!"
COOKIES_FILE_PATH = os.path.join(get_root_dir(), 'config', 'cookies.txt')


def get_youtube_cookies():
    options = uc.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, use_subprocess=True)

    try:
        driver.get("https://accounts.google.com/signin/v2/identifier?service=youtube")
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        id_input.send_keys(YOUTUBE_ID)
        driver.find_element(By.CSS_SELECTOR, "#identifierNext").click()
        logger.info(f"아이디 [{YOUTUBE_ID}]를 입력했습니다.")

        pw_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
        )
        pw_input.send_keys(YOUTUBE_PW)
        logger.info(f"PW를 입력했습니다.")

        driver.find_element(By.CSS_SELECTOR, "#passwordNext").click()

        logger.info("로그인 성공을 기다리는 중입니다...")
        WebDriverWait(driver, 15).until(
            EC.url_contains("myaccount.google.com")
        )

        logger.info("로그인 성공! 쿠키를 추출합니다.")
        driver.get("https://www.youtube.com")
        cookies = driver.get_cookies()

        with open(COOKIES_FILE_PATH, 'w') as file:
            json.dump(cookies, file)

        logger.info(f"쿠키를 성공적으로 '{COOKIES_FILE_PATH}' 파일에 저장했습니다.")
        return True

    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        driver.save_screenshot("login_error.png")
        return False
    finally:
        driver.quit()


if __name__ == "__main__":
    get_youtube_cookies()
