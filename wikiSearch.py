from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from elementLocator import Locator
from selenium.webdriver.common.by import By

import base64operations
from summarizer import Summarizer
from mongodbOperations import MongoDBOperations
import concurrent.futures


class WikiSearch:
    def __init__(self, executable_path, chrome_options, db_name):
        try:
            self.db_name = db_name
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
            self.summarizer_obj = Summarizer()
            self.mongo_client = MongoDBOperations()
        except Exception as e:
            raise Exception("Error\n" + str(e))

    def openurl(self, url):
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            raise Exception("Webpage cannot be loaded\n" + str(e))

    def find_element_by_id(self, id_):
        try:
            element = self.driver.find_element(By.ID, id_)
            return element
        except Exception as e:
            raise Exception("Unable to locate id provided\n" + str(e))

    def find_element_by_xpath(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element
        except Exception as e:
            raise Exception("Unable to locate xpath element\n" + str(e))

    def find_elements_by_css_selector(self, css_element):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_element)
            return elements
        except Exception as e:
            raise Exception("Unable to locate css element\n" + str(e))

    def find_elements_by_class_name(self, class_name):
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            return elements
        except Exception as e:
            raise Exception("Unable to locate elements by class name\n" + str(e))

    def wait(self):
        self.driver.implicitly_wait(1)

    def quit(self):
        self.driver.quit()

    def search_wiki(self, search_string, locator):
        try:
            search_area = self.find_element_by_xpath(locator.search_input_area())
            search_area.send_keys(search_string)
            search_button = self.find_element_by_xpath(locator.search_button())
            search_button.click()
        except StaleElementReferenceException:
            search_button = self.find_element_by_xpath(locator.search_button())
            search_button.click()
        except Exception as e:
            raise Exception("Wikipedia search encountered some error\n" + str(e))

        title = self.find_element_by_id(locator.firstHeadingLocator()).text
        coll_name = title.strip().replace(" ", "")
        print(f"found wiki page: {title}")

        return title, coll_name

    def wiki_text_scrapper(self, locator):

        p_list = self.find_elements_by_css_selector(locator.p_element_locator())
        if len(p_list) < 1:
            return "Wikipedia Confused! Try again"
        body = ""
        for t in p_list:
            body += t.text + " "

        body_summary = self.summarizer_obj.summarize(body)

        return body_summary

    def wiki_pic_scrapper(self, locator):
        img_array = []
        info_image = ""
        try:
            images = self.find_elements_by_css_selector(locator.img_element_locator())
            for image in images:
                if int(image.get_attribute("height")) > 40:
                    img_url = image.get_attribute("src")
                    img_array.append(img_url)
            try:
                infobox = self.driver.find_element(By.CLASS_NAME, "infobox-image")
                info_image = infobox.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            except NoSuchElementException:
                print("No infobox image")

            info_image_encoded = base64operations.b64encoder_single_image(info_image)
            images_encoded = base64operations.b64_encoder(img_array)

            return images_encoded, info_image_encoded
        except Exception as e:
            raise Exception("Error: \t\t\t" + str(e))

    def wiki_references_scrapper(self, locator):
        references = []
        try:
            references_list = self.find_elements_by_class_name(locator.references_locator())
            for reference in references_list:
                references.append(reference.text)
            return references
        except Exception as e:
            raise Exception("Error: \t\t\t" + str(e))

    def wiki_scrapper(self, search_string):
        try:
            self.openurl("https://en.wikipedia.org")
            self.wait()
            locator = Locator()
            title, coll_name = self.search_wiki(search_string, locator)
            # mongo search
            if coll_name in self.mongo_client.list_coll_names(self.db_name):
                print("found in database")
                self.quit()
                return self.mongo_client.fetch_one_record(self.db_name, coll_name)
            else:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    f1 = executor.submit(self.wiki_text_scrapper, locator)
                    f2 = executor.submit(self.wiki_pic_scrapper, locator)
                    f3 = executor.submit(self.wiki_references_scrapper, locator)

                    body_summary = f1.result()
                    print("Summarized")
                    images_encoded, info_image_encoded = f2.result()
                    print("Images Encoded")
                    references = f3.result()
                    print("References scrapped")

                self.quit()

                record = {"title": title, "summary": body_summary, "info_image": info_image_encoded,
                          "images": images_encoded, "references": references}
                try:
                    self.mongo_client.insert_one(self.db_name, coll_name, record)
                    print("Inserted in database")
                except Exception as e:
                    print(str(e))

                return record

        except Exception as e:
            self.quit()
            raise Exception("Error: \t\t" + str(e))
