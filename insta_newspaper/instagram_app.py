import os
import pickle
import yaml

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


class InstagramApp:
    """Class managing the entire Instagram process.
    Creates a Selenium instance to log in and post images.

    Attributes:
        driver (webdriver.Firefox): Selenium gecko driver
        config (dict): Config parameters parsed during init
        language (str): Instagram language detected during upload process
    """

    def __init__(
        self, config: dict, headless: bool = False, save_cookies: bool = False
    ):
        """Constructor for InstagramApp

        Args:
            config (dict): Config parameters parsed during init
            headless (bool, optional): If true driver will be headless,
                no graphical window will be invoked.
            save_cookies (bool, optional): If true, driver will not be headless
                and will not log in automatically to let the user enter his
                credentials. Defaults to False.
        """

        self.driver = None
        self.config = config
        self.language = None

        with open(
            os.path.join(os.path.dirname(__file__), "instagram_strings.yaml")
        ) as f:
            self.string_dict = yaml.load(f, Loader=yaml.FullLoader)

        if save_cookies:
            self.save_cookies()
            return

        self.start_driver(headless=headless)

    def start_driver(self, auto_login=True, headless=False):
        """Manages the creation of the gecko driver instance.

        Args:
            auto_login (bool, optional): If true, will try to log in with
                saved cookies. If no cookies have been saved yet or if log
                in fails, will try to use raw credentials. Defaults to True.
            headless (bool, optional): If true driver will be headless,
                no graphical window will be invoked. auto_login has to be False.
        """

        # Replace original browser user agent by an Android one to be able to
        # post, which is only possible on smartphones.
        android_useragent = "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", android_useragent)

        options = webdriver.FirefoxOptions()
        if auto_login and headless:
            options.add_argument("--headless")

        self.driver = webdriver.Firefox(firefox_profile=profile, options=options)

        self.driver.get("https://www.instagram.com")
        self.driver.maximize_window()

        if not auto_login:
            return

        cookie_location = self.config["cookie_save_path"] + "cookies.pkl"

        print("Loading cookies:", cookie_location)

        if os.path.isfile(cookie_location):
            self.cookie_login(cookie_location)

            try:
                WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable(
                        (By.XPATH, "//div[@data-testid='new-post-button']")
                    )
                )
                print("Connected with cookies.")
                return
            except:
                print("Login failed with cookies. Trying classic login.")

        else:
            print("No cookies found for log in.")

        # Log in with credentials entered in config.yaml if no cookies
        # were saved previously or if cookie log in fails.
        self.classic_login()

        try:
            WebDriverWait(self.driver, 10).until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//div[@data-testid='new-post-button']")
                )
            )
            print("Connected with credentials.")

        except:
            print("Classic login. Exiting.")
            exit()

    def stop_driver(self):
        """Stops the driver properly."""

        self.driver.quit()

    def save_cookies(self):
        """Starts the driver and connect to Instagram.
        User have to manually enter his credentials, then press a key in terminal.
        Cookies will be stored in path given in config.yaml
        """

        self.start_driver(auto_login=False)

        input("Press a key when connected.")

        pickle.dump(
            self.driver.get_cookies(),
            open(self.config["cookie_save_path"] + "cookies.pkl", "wb"),
        )

        self.driver.quit()

    def cookie_login(self, cookie_location):
        """Manages the deletion of default cookies and injection
        of previously stored valid cookies.

        Args:
            cookie_location (str): Cookie location, set in config.yaml
        """

        try:
            cookies = pickle.load(open(cookie_location, "rb"))
        except:
            print("Error while opening cookies.")
            exit()

        self.driver.delete_all_cookies()
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get("https://www.instagram.com")

    def classic_login(self):
        """Uses credentials set in config.yaml to log in"""

        wait = WebDriverWait(self.driver, 10)

        accept_cookies_button = wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Accept')]")
            )
        )
        accept_cookies_button.click()

        log_in_button = wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Log In')]")
            )
        )
        log_in_button.click()

        username_input = wait.until(
            ec.element_to_be_clickable((By.XPATH, "//input[@name='username']"))
        )
        username_input.send_keys(self.config["username"])

        password_input = wait.until(
            ec.element_to_be_clickable((By.XPATH, "//input[@name='password']"))
        )
        password_input.send_keys(self.config["password"])
        password_input.send_keys(Keys.ENTER)

        not_now_button = wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Not Now')]")
            )
        )
        not_now_button.click()

    def detect_language(self):
        """Detect Instagram language to adapt searched strings later on."""

        source = self.driver.page_source

        if "Nouvelle publication photo" in source:
            self.language = "fr"
        else:
            self.language = "en"

    def upload_image(self, name, simple_name, chosen_date):
        """Upload previously saved image with caption."""

        wait = WebDriverWait(self.driver, 10)

        print("Uploading...")

        new_post_button = wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "//div[@data-testid='new-post-button']")
            )
        )
        new_post_button.click()

        file_location = "{save_path}{simple_name}-{chosen_date}.jpeg".format(
            save_path=self.config["image_local_save_path"],
            simple_name=simple_name,
            chosen_date=chosen_date,
        )

        hidden_input = self.driver.find_element_by_xpath(
            "//input[@accept='image/jpeg']"
        )
        hidden_input.send_keys(file_location)

        # Wait until image is loaded
        wait.until(
            ec.visibility_of_element_located(
                (By.XPATH, "//div[contains(@style, 'background-image')]")
            )
        )

        self.detect_language()

        expand_button = wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(), '{expand}')]".format(
                        expand=self.string_dict[self.language]["expand"]
                    ),
                )
            )
        )
        expand_button.click()

        next_button = wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(text(), '{next}')]".format(
                        next=self.string_dict[self.language]["next"]
                    ),
                )
            )
        )
        next_button.click()

        formated_date = "{day}/{month}/{year}".format(
            year=chosen_date[:4], month=chosen_date[4:6], day=chosen_date[6:8]
        )

        hashtags = [
            simple_name,
            "presse",
            "journal",
            "france",
            "patrimoine",
            "histoire",
            "culture",
            "heritage",
            "newspaper",
            "history",
            "throwback",
            "historia",
            "historical",
            "old",
            "ancient",
            "vintage",
            "oldies",
            "tbt",
            "throwback",
            "photooftheday",
            "picoftheday",
            "instagood",
            "instadaily",
            "instalike",
            "likeforlike",
            "follow",
            "followme",
            "like",
            "tagforlikes",
            "followforfollow",
        ]

        if len(hashtags) > 30:
            print(
                "Too much hashtags, Instagram only allows 30 in your caption. Exiting."
            )
            exit()

        caption = " 📰 {name}\n 📅 {date}\n\nSource : Bibliothèque Nationale de France\n\n\n\n#{hashtags}".format(
            name=name,
            date=formated_date,
            hashtags="# ".join(hashtags),
        )

        caption_area = wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//textarea[@aria-label='{caption_label}']".format(
                        caption_label=self.string_dict[self.language]["caption_label"]
                    ),
                )
            )
        )
        caption_area.send_keys(caption)

        share_button = wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(text(), '{share}')]".format(
                        share=self.string_dict[self.language]["share"]
                    ),
                )
            )
        )
        share_button.click()

        # Wait to make sure upload is completed
        try:
            WebDriverWait(self.driver, 20).until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//div[@data-testid='new-post-button']")
                )
            )
        except:
            print("Failed to upload image on Instagram. Exiting.")
            exit()

        print("Image uploaded on Instagram !")