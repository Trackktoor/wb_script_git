from browser_handlers import WB_BROWSER
from excel_handlers import EXCEL_PARSER
from excel_handlers import EXCEL_REPORT
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC
from random import randrange
import traceback


# 101 - ошибка но которую не нужно исправлять
# 102 - ошибка добалвенив корзину

ERRORS_DICT = {
    100: 'OK',
    101: 'Нет нужного размера',
    102: 'Продукт не найден на страницах ',
    103: 'Не добавлен в корзину',
    104: 'Плохой прокси',
    105: 'Аккаунт ещё не успел встать',
    106: 'Элемент не найден на странице'
} 


class MANAGE_SCRIPT():
    def __init__(self, max_pages=25, target_profile='', headless=False) -> None:
        self.fail_profiles = []
        self.wb_browser = ''
        self.report = EXCEL_REPORT()
        self.error_count = 0
        self.max_pages = max_pages
        self.target_profile = target_profile
        self.headless = headless

    def autobasket_for_one_product(self, info, headless=False):
        try:
            profile_id:int = info[1]
            wb_browser:WB_BROWSER = WB_BROWSER(profile_id=profile_id, headless=self.headless)
            self.wb_browser = wb_browser
            self.wb_browser.initial_selenium_browser()

            if self.wb_browser.browser == False or self.wb_browser.browser == '':
                print('Вернул 105 статус')
                return {'status': 105}
                
            time.sleep(1.5)
            try:
                self.wb_browser.browser.get('https://www.wildberries.ru')

                add_item_in_basket:ADD_ITEM_IN_BASKET = ADD_ITEM_IN_BASKET(wb_browser,info, self.max_pages)

                if add_item_in_basket.search() == False:
                    self.stop()
                    return {'status': 104}

                product = add_item_in_basket.find_current_product()
            except Exception as ex:
                    if str(ex) == 'STOP':
                        raise Exception('STOP')
                    print(traceback.format_exc())
                    self.stop()
                    return {'status': 104}
                
            if not product:
                result = [item for item in info if item != None]
                result.append('Продукт не найден на страницах')
                self.report.add_product(result)
                self.stop()
                return {'status':102}
            
            product_added = add_item_in_basket.add_product_in_basket(product)

            if not product_added:
                result = [item for item in info if item != None]
                result.append('Ошибка: Нет нужного размера')
                self.report.add_product(result)
                self.stop()
                return {'status':101}
            
            if add_item_in_basket.product_in_basket():
                self.stop()
                print('stop - complate')
                result = [item for item in info if item != None]
                
                result.append('OK')
                self.report.add_product(result)
                print('report - complate')

                return {'status': 100}
            else:
                self.stop()
                return {'status': 103} 
        except Exception as ex:
            print(traceback.format_exc())
            return 106

    def start__process(self,all_info):
        i = 0
        while i < len(all_info):
            info = all_info[i]
            autobasket = self.autobasket_for_one_product(info)
            if autobasket != 106:
                print('В перовм цикле получил: ' + str(autobasket['status']))
            else:
                print('В перовм цикле получил: ' + str(autobasket))
            print('autobasket - complate')

            if autobasket == 106:
                self.fail_profiles.append(info)
                i += 1
                print(106)
                continue
            if autobasket['status'] == 103:
                if self.error_count == 0:
                    self.error_count += 1
                if type(self.wb_browser.browser) == webdriver:
                    self.wb_browser.browser.quit()
                    print('quit - complate')

                    print(103)
                    continue
                else:
                    result = [item for item in info if item != None]
                    result.append(f'Ошибка: не добавлен в корзину')
                    self.report.add_product(result)
                if type(self.wb_browser.browser) == webdriver:
                    self.wb_browser.browser.quit()
                    print('quit - complate')
                    i += 1

            if autobasket['status'] == 104:
                self.fail_profiles.append(info)
                print(info[4])
                if type(self.wb_browser.browser) == webdriver:
                    self.wb_browser.browser.quit()
                    print('quit - complate')
                print(104)
                i += 1
                continue

            if autobasket['status'] == 105:
                print('Обрабатываю 105 статус в первом цикле')
                self.fail_profiles.append(info)

                if type(self.wb_browser.browser) == webdriver:
                    self.wb_browser.browser.quit()
                    print('quit - complate')

                print(105)
                i += 1
            else:
                if type(self.wb_browser.browser) == webdriver:
                    self.wb_browser.browser.quit()
                    print('quit - complate')
                i += 1

    def start(self):


        if self.target_profile != '':
            all_info = [self.target_profile]
        else:
            excel_parser:excel_parser = EXCEL_PARSER()
            all_info = excel_parser.get_values()
        
        # Основной цикл
        self.start__process(all_info)
        '''result = [item for item in info if item != None]
                result.append(f'Ошибка: плохой прокси')
                self.report.add_product(result)'''
        
        # Цикл на обработу ошибок
        if len(self.fail_profiles) != 0:
            wb_browser:WB_BROWSER = WB_BROWSER(profile_id='')
            self.wb_browser = wb_browser
            self.wb_browser.get_all_proxy()
            all_proxys_id = [proxy['id'] for proxy in self.wb_browser.get_all_proxy()]
            work_proxy = None
            i = 0
            status = 106
            while len(self.fail_profiles) > 0:
                profile = self.fail_profiles[0]
                print(f'profile {i}')
                if work_proxy == None:
                    for proxy_id in all_proxys_id:
                        j = True
                        while j:
                            self.wb_browser.change_proxy_for_target_profile({'proxy[id]':proxy_id}, profile[1])

                            autobasket_for_one_product = self.autobasket_for_one_product(profile)
                            print('PN')
                            if autobasket_for_one_product == 106:
                                if type(self.wb_browser.browser) == webdriver:
                                    self.wb_browser.browser.quit()
                                    print('quit - complate')
                                print('106 во втором')
                                continue
                            status = autobasket_for_one_product['status']
                            if status == 105:
                                print('PN:105')
                                if type(self.wb_browser.browser) == webdriver:
                                    self.wb_browser.browser.quit()
                                    print('quit - complate')
                                break

                            if status in [100,101,102]:
                                print('PN:OK')
                                work_proxy = proxy_id
                                j = False
                                i += 1
                                self.fail_profiles.remove(profile)
                                break

                            if type(self.wb_browser.browser) == webdriver:
                                    self.wb_browser.browser.quit()
                                    print('quit - complate')
                            j = False
                            continue
                        if status in [100,101,102]:
                            break
                else:

                    self.wb_browser.change_proxy_for_target_profile({'proxy[id]':work_proxy}, profile[1])
                    status = ''
                    j = True
                    while j:
                        print('PT')
                        try:
                            autobasket_for_one_product = self.autobasket_for_one_product(profile)
                            status = autobasket_for_one_product['status']
                            if status == 105:
                                print('PT: 105')
                                time.sleep(0.5)
                                print('Профиль недостпуен, пытаюсь подключиться...')
                                continue

                            if status == 104:
                                print('PT: 104')
                                work_proxy = None
                                j = False
                                continue

                        except Exception as ex:
                            continue
                    
                    if status == 102:
                        print('PT: 102')
                        i += 1
                        self.fail_profiles.remove(profile)
                        continue
                    
                    if status == 103:
                        print('PT: 103')
                        result = [item for item in profile if item != None]
                        result.append(f'Ошибка: не добавлен в корзину')
                        self.report.add_product(result)
                        i += 1
                        j = False
                        self.fail_profiles.remove(profile)
                    else:
                        # if len(self.fail_profiles) == 1:
                        #     print('CLOSE - complate 100 or 101')
                        #     self.wb_browser.browser.quit()
                        #     break
                        print('PT: 101,103')
                        self.fail_profiles.remove(profile)
                        i += 1
                        continue

    def stop(self):
        self.wb_browser.stop()


class ADD_ITEM_IN_BASKET():
    def __init__(self, wb_browser:WB_BROWSER, info:tuple, max_pages) -> None:
        self.wb_browser = wb_browser

        self.profile_number:str = info[1]
        self.product_number:str = info[2]
        self.brand:str = info[3]
        self.size:str = info[4]
        self.search_text:str = info[5]
        self.max_pages = max_pages

    def search(self):
        time.sleep(1)
        text_in_search = True
        try:
            search_input = self.wb_browser.browser.find_element(By.ID, 'searchInput')
        except Exception as ex:
            if str(ex) == 'STOP':
                raise Exception('STOP')
            return False
        
        while text_in_search:
            
            search_input.clear()
            if ' ' in self.search_text:
                arr_words = self.search_text.split(' ')
                for word in arr_words:
                    search_input.send_keys(word + ' ')
                    time.sleep(randrange(2,3))
                search_input_text = self.wb_browser.browser.execute_script("return document.getElementById('searchInput').value")
                if search_input_text == self.search_text + ' ':
                    text_in_search = False
            else:
                search_input.send_keys(self.search_text)


        search_input.send_keys(Keys.ENTER)
    
    def load_page(self):
        count_scroll_px = 100
        time.sleep(3)
        height_scroll = int(self.wb_browser.browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))

        while count_scroll_px < height_scroll:
            self.wb_browser.browser.execute_script(f"window.scrollTo(0, {count_scroll_px})")
            count_scroll_px += 250
            height_scroll = int(self.wb_browser.browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            time.sleep(0.2)
        self.wb_browser.browser.execute_script(f"window.scrollTo(0, 200)")

    def get_all_products(self):
        container = self.wb_browser.browser.find_element(By.CLASS_NAME, 'product-card-list')
        proucts = container.find_elements(By.CLASS_NAME, 'product-card')
        return proucts
    
    def product_is_valid(self, product):
        if int(self.product_number) == int(product.get_attribute('data-nm-id')):
            return True

        return False    
    
    def add_product_in_basket(self, product):
        time.sleep(1)
        product.click()
        time.sleep(3)
        while True:
            try:
                self.wb_browser.browser.execute_script('window.scrollTo(0,0)')
                time.sleep(1)

                self.check_characteristics()
                self.check_reviews()
                self.check_reviews_text()
                self.check_product_photos()
                size_list = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'sizes-list')[0]
                sizes = size_list.find_elements(By.TAG_NAME, 'li')
                break
            except:
                print(traceback.format_exc())
                self.wb_browser.browser.refresh()
                time.sleep(4)
                continue

        for size in sizes:
            label = size.find_element(By.TAG_NAME, 'label')
            if label.find_element(By.CLASS_NAME, 'sizes-list__size').text == str(self.size):
                label_classes = label.get_attribute('class')
                if  (len(label_classes.split(' ')) == 2 or label_classes == 'j-size sizes-list__button active') and label_classes != 'j-size sizes-list__button disabled':
                    label.click()

                    self.wb_browser.browser.find_elements(By.CLASS_NAME, 'btn-main')[4].click()
                    time.sleep(1)
                    return True
                else:
                    continue
        return False
    
    def find_current_product(self):
        conunt_page = 1
        while conunt_page <= self.max_pages:
            time.sleep(2)
            self.load_page()
            products = self.get_all_products()
            for product in products:
                if self.product_is_valid(product):
                    return product
                
            next = self.next_page()

            if next == 'max':
                return None
            
            conunt_page += 1

    def next_page(self):
        try:
            wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 10, poll_frequency=0.1)
            self.wb_browser.browser.execute_script(f"window.scrollTo(0, document.body.scrollHeight)")
            element = wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, 'pagination__next')
            ))
            next_link = self.wb_browser.browser.find_element(By.CLASS_NAME, 'pagination__next')
        
            next_link.click()
        except Exception as ex:
            if str(ex) == 'STOP':
                raise Exception('STOP')
            return 'max'
    
    def product_in_basket(self):
        self.wb_browser.browser.get('https://www.wildberries.ru/lk/basket')
        time.sleep(2)
        
        products_links_in_basket = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'good-info__title')
        
        for product_link in products_links_in_basket:
            link_articul = product_link.get_attribute('href').split('/')[4]
            if link_articul == str(self.product_number):
                return True
        return False

    def check_characteristics(self):
        self.wb_browser.browser.execute_script('window.scrollTo(0, 600)')
        buttons_characteristics = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'collapsible__toggle-wrap')
        for button in  buttons_characteristics:
            button.find_element(By.TAG_NAME, 'button').click()
            time.sleep(randrange(1,3))

    def check_reviews(self):
        try:
            self.wb_browser.browser.execute_script('window.scrollTo(0, 1350)')
            time.sleep(1)
            reviews_wraper = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'swiper-wrapper')[2]
            review = reviews_wraper.find_element(By.TAG_NAME, 'div')
            review.click()
            time.sleep(randrange(1,2))
            next_button = self.wb_browser.browser.find_element(By.CLASS_NAME, 'swiper-button-next')
            for i in range(2):
                next_button.click()
                time.sleep(randrange(1,2))
            
            self.wb_browser.browser.find_element(By.CLASS_NAME, 'popup__close').click()
            time.sleep(1)
            self.wb_browser.browser.execute_script('window.scrollTo(0, 200)')
        except:
            self.wb_browser.browser.execute_script('window.scrollTo(0, 200)')
            

    def check_reviews_text(self):
        scroll_y = 1500

        self.wb_browser.browser.execute_script(f'window.scrollTo(0, {scroll_y})')
        time.sleep(1)
        comment_card = self.wb_browser.browser.find_element(By.CLASS_NAME, 'comment-card')
        self.wb_browser.browser.execute_script('arguments[0].scrollIntoView();', comment_card)
        time.sleep(0.5)
        comment_card.click()
        time.sleep(1)

        for i in range(2):
            self.wb_browser.browser.execute_script(f'window.scrollTo(0, {scroll_y})')
            scroll_y += 200
            time.sleep(0.4)
        wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 10, poll_frequency=0.1)
        element = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'product-feedbacks__back')
        ))
        back_button = self.wb_browser.browser.find_element(By.CLASS_NAME, 'product-feedbacks__back')
        back_button.click()
        self.wb_browser.browser.execute_script(f'window.scrollTo(0, 0)')
        self.wb_browser.browser.refresh()
        time.sleep(2)

    def check_product_photos(self):
        photos_wrapper = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'swiper-wrapper')[0]
        for photo in photos_wrapper.find_elements(By.TAG_NAME, 'li'):
            try:
                photo.click()
                time.sleep(0.4)
            except Exception as ex:
                continue

if __name__ == '__main__':
        ERRORS_DICT = {
            100: 'OK',
            101: 'Нет нужного размера',
            102: 'Продукт не найден на страницах ',
            103: 'Не добавлен в корзину',
            104: 'Плохой прокси',
            105: 'Аккаунт ещё не успел встать'
        } 
        
        manage_script = MANAGE_SCRIPT(max_pages=5)
        manage_script.start()
