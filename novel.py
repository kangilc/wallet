'''
이 스크립트를 실행하려면 다음 라이브러리를 설치해야 합니다:
pip install selenium beautifulsoup4

또한 사용 중인 브라우저에 맞는 웹 드라이버를 다운로드해야 합니다.
Chrome의 경우 여기에서 다운로드할 수 있습니다: https://chromedriver.chromium.org/downloads
'''

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import urllib

# 목록 URL
list_url = "https://booktoki468.com/novel/14323569?stx=%EB%AC%B4%ED%95%9C&book=%EC%9D%BC%EB%B0%98%EC%86%8C%EC%84%A4"

# 웹 드라이버 경로 (chromedriver.exe 파일의 경로로 변경)
# DRIVER_PATH = 'path/to/your/chromedriver.exe'
# service = Service(executable_path=DRIVER_PATH)
# driver = webdriver.Chrome(service=service)
# 이 예제에서는 chromedriver가 PATH에 있다고 가정합니다.

def get_novel_content(driver, url):
    """
    주어진 URL에서 소설 본문 내용을 가져옵니다.
    """
    try:
        driver.get(url)
        # 소설 내용이 로드될 때까지 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "novel_content"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        content_div = soup.find('div', {'id': 'novel_content'})

        if content_div:
            return content_div.get_text(separator='\n', strip=True)
        else:
            return "본문 내용을 찾을 수 없습니다."

    except Exception as e:
        return f"오류 발생: {e}"

def save_to_file(content, filename_prefix="novel_chapter", chapter_index=1):
    """
    내용을 파일에 저장합니다.
    """
    filename = f"temp/{filename_prefix}_{chapter_index}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def get_all_iframes(driver, timeout=7):
    """
    모든 iframe을 가져옵니다.
    WebDriverWait를 사용하여 iframe이 DOM에 나타날 때까지 기다립니다.
    """
    driver.switch_to.default_content() # 항상 기본 콘텐츠에서 시작
    print("기본 콘텐츠로 전환했습니다. iframe을 찾는 중...")
    try:
        # 모든 iframe 요소가 DOM에 나타날 때까지 기다립니다.
        iframes = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
        )
        return iframes
    except TimeoutException:
        print(f"지정된 시간({timeout}초) 내에 iframe을 찾지 못했습니다.")
        return []

if __name__ == "__main__":
    driver = None
    try:
        # 웹 드라이버를 사용하여 페이지를 엽니다.
        # 이 부분은 시스템에 따라 구성해야 할 수 있습니다.
        # driver = webdriver.Chrome()
        driver = uc.Chrome()
        driver.get(list_url)
        time.sleep(15) # Cloudflare 챌린지가 해결될 시간을 줍니다.

        # 디버깅을 위해 스크린샷과 페이지 소스를 저장합니다.
        screenshot_path = "temp/debug_screenshot.png"
        page_source_path = "temp/debug_page_source.html"
        driver.save_screenshot(screenshot_path)
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"디버깅 스크린샷이 {screenshot_path}에 저장되었습니다.")
        print(f"디버깅 페이지 소스가 {page_source_path}에 저장되었습니다.")

        print("\nCloudflare 챌린지 페이지가 열렸습니다.")
        print("브라우저 창에서 Cloudflare 챌린지를 수동으로 해결해 주세요.")
        input("챌린지를 해결한 후 Enter 키를 누르면 스크립트가 계속됩니다...")

        # 챌린지 해결 후 페이지가 로드될 때까지 기다립니다.
        time.sleep(5) # 페이지 로드를 위한 추가 대기 시간 (필요에 따라 조정)

        list_soup = BeautifulSoup(driver.page_source, 'html.parser')

        chapter_links = list_soup.select(".list-item a")

        if chapter_links:
            print(f"총 {len(chapter_links)}개의 챕터 링크를 찾았습니다.")
            for i, link_tag in enumerate(chapter_links):
                if link_tag.has_attr('href'):
                    chapter_url = urllib.parse.urljoin(list_url, link_tag['href'])
                    chapter_title = link_tag.get_text(strip=True) # Get chapter title for filename
                    print(f"챕터 {i+1} ({chapter_title}) 링크: {chapter_url}")

                    novel_text = get_novel_content(driver, chapter_url)

                    # Save to a unique file for each chapter
                    save_to_file(novel_text, filename_prefix=chapter_title.replace(' ', '_').replace('/', '_'), chapter_index=i+1)
                else:
                    print(f"챕터 {i+1}의 링크를 찾을 수 없습니다.")
        else:
            print("소설 챕터 링크를 찾을 수 없습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        if driver:
            driver.quit()
