from typing import List
import time
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException

from build_assets.selenium_runner.SeleniumRunner import SeleniumRunner

class BuildSeleniumRunner(SeleniumRunner):
    def build_icons(self, icomoon_json_path: str,
        zip_path: Path, svgs: List[str], screenshot_folder: str):
        self.upload_icomoon(icomoon_json_path)
        self.upload_svgs(svgs, screenshot_folder)
        self.download_icomoon_fonts(zip_path)

    def upload_icomoon(self, icomoon_json_path: str):
        """
        Upload the icomoon.json to icomoon.io.
        :param icomoon_json_path: a path to the iconmoon.json.
        :raises TimeoutException: happens when elements are not found.
        """
        print("Uploading icomoon.json file...")
        
        # find the file input and enter the file path
        import_btn = self.driver.find_element_by_css_selector(
            SeleniumRunner.GENERAL_IMPORT_BUTTON_CSS
        )
        import_btn.send_keys(icomoon_json_path)

        try:
            confirm_btn = WebDriverWait(self.driver, SeleniumRunner.MED_WAIT_IN_SEC).until(
                ec.element_to_be_clickable((By.XPATH, "//div[@class='overlay']//button[text()='Yes']"))
            )
            confirm_btn.click()
        except SeleniumTimeoutException as e:
            raise Exception("Cannot find the confirm button when uploading the icomoon.json" \
                  "Ensure that the icomoon.json is in the correct format for Icomoon.io")

        print("JSON file uploaded.")

    def upload_svgs(self, svgs: List[str], screenshot_folder: str):
        """
        Upload the SVGs provided in svgs. This will upload the 
        :param svgs: a list of svg Paths that we'll upload to icomoon.
        :param screenshot_folder: the name of the screenshot_folder. 
        """
        print("Uploading SVGs...")

        import_btn = self.driver.find_element_by_css_selector(
            SeleniumRunner.SET_IMPORT_BUTTON_CSS
        )

        for i in range(len(svgs)):
            import_btn.send_keys(svgs[i])
            print(f"Uploaded {svgs[i]}")
            self.test_for_possible_alert(self.SHORT_WAIT_IN_SEC, "Dismiss")
            self.edit_svg()

        # take a screenshot of the icons that were just added
        new_icons_path = str(Path(screenshot_folder, "new_svgs.png").resolve())
        self.driver.save_screenshot(new_icons_path);

        print("Finished uploading the svgs...")

    def download_icomoon_fonts(self, zip_path: Path, screenshot_folder: str):
        """
        Download the icomoon.zip from icomoon.io.
        :param zip_path: the path to the zip file after it's downloaded.
        :param screenshot_folder: the name of the screenshot_folder. 
        """
        print("Downloading Font files...")
        self.select_all_icons_in_top_set()
        self.go_to_font_tab()

        # take an overall screenshot of the icons that were just added
        # also include the glyph count
        new_icons_path = str(Path(screenshot_folder, "new_icons.png").resolve())
        main_content_xpath = "/html/body/div[4]/div[2]/div/div[1]"
        main_content = self.driver.find_element_by_xpath(main_content_xpath)
        main_content.screenshot(new_icons_path);

        download_btn = WebDriverWait(self.driver, SeleniumRunner.LONG_WAIT_IN_SEC).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "button.btn4 span"))
        )
        download_btn.click()
        if self.wait_for_zip(zip_path):
            print("Font files downloaded.")
        else:
            raise TimeoutError(f"Couldn't find {zip_path} after download button was clicked.")

    def wait_for_zip(self, zip_path: Path) -> bool:
        """
        Wait for the zip file to be downloaded by checking for its existence
        in the download path. Wait time is self.LONG_WAIT_IN_SEC and check time
        is 1 sec.
        :param zip_path: the path to the zip file after it's
        downloaded.
        :return: True if the file is found within the allotted time, else
        False.
        """
        end_time = time.time() + self.LONG_WAIT_IN_SEC
        while time.time() <= end_time:
            if zip_path.exists():
                return True
            time.sleep(1)  # wait so we don't waste sys resources
        return False
