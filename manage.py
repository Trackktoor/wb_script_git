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
from selenium.common.exceptions import TimeoutException
import traceback
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains 


# 101 - ошибка но которую не нужно исправлять
# 102 - ошибка добалвенив корзину

ERRORS_DICT = {
    100: 'OK',
    101: 'Нет нужного размера',
    102: 'Продукт не найден на страницах',
    103: 'Не добавлен в корзину',
    104: 'Плохой прокси',
    105: 'Аккаунт ещё не успел встать',
    106: 'Элемент не найден на странице'
} 


class MANAGE_SCRIPT():
    def __init__(self,data_queue,max_pages=25, target_profile='', headless=False) -> None:
        self.fail_profiles = []
        self.wb_browser = ''
        self.report = EXCEL_REPORT()
        self.error_count = 0
        self.max_pages = max_pages
        self.target_profile = target_profile
        self.headless = headless
        self.data_queue = data_queue

    def autobasket_for_one_product(self,info,all_info, headless=False ):
        try:
            profile_name:str = info[1]
            wb_browser:WB_BROWSER = WB_BROWSER(profile_name=profile_name, headless=self.headless)
            self.wb_browser = wb_browser
            self.wb_browser.initial_selenium_browser(profile_name=profile_name)

            if self.wb_browser.browser == False or self.wb_browser.browser == '':
                print('STATUS: 105')
                self.wb_browser.stop_doplhin_profile()

                return {'status': 105}
                
            time.sleep(1.5)
            try:
                self.wb_browser.browser.get('https://www.wildberries.ru')

                add_item_in_basket:ADD_ITEM_IN_BASKET = ADD_ITEM_IN_BASKET(wb_browser,info, self.max_pages)
                search = add_item_in_basket.search()
                if type(search) == {}:
                    return {'status': 104}
                if search == False:
                    if self.wb_browser.browser != '':
                        self.stop()
                    self.wb_browser.stop_doplhin_profile()
                    return {'status': 104}

                product = add_item_in_basket.find_current_product()
            except TimeoutException:
                print('ERROR: Ожидание страницы превышено, меняю прокси')
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                return {'status': 104}
            except Exception as ex:
                    if 'chrome not reachable' in str(ex):
                        print('ERROR: Chrome not reachable')
                    else:
                        print(traceback.format_exc())
                    self.wb_browser.stop_doplhin_profile()
                    if self.wb_browser.browser != '':
                        self.stop()
                    return {'status': 104}
                
            if product == None:
                if info[4] == None:
                    info[4] = ''
                result = [item for item in info if item != None]
                result.append('Продукт не найден на страницах')
                self.report.add_product(result)
                self.wb_browser.stop_doplhin_profile()
                print('stop_doplhin_profile')   
                return {'status':102}
            
            if product == {'status': 104}:
                return product
            
            product_added = add_item_in_basket.add_product_in_basket(product)

            if product_added == {'status': 104}:
                return {'status': 104}

            if not product_added:
                print('no size')
                result = [item for item in info if item != None]
                result.append('Ошибка: Нет нужного размера')
                self.report.add_product(result)
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                return {'status':101}
            
            if add_item_in_basket.product_in_basket():
                if info[4] == None: info[4]=''
                result = [item for item in info if item != None]
                
                result.append('OK')
                self.report.add_product(result)
                print('report - complate')
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                    print('stop - complate finish')
                    if len(all_info) == 1 or self.target_profile=='':
                        print('SystemExit')
                        raise SystemExit
         
                return {'status': 100}
            else:
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                return {'status': 105} 
        except Exception as ex:
            return 106

    def start__process(self,all_info):
        i = 0
        while i < len(all_info):
            info = all_info[i]
            autobasket = self.autobasket_for_one_product(info, all_info)
            if autobasket == 106:
                self.fail_profiles.append(info)
                i += 1
                print('STATUS: 106')
                self.wb_browser.stop_doplhin_profile()
                
                if self.wb_browser.browser != '':
                    self.stop()
                self.wb_browser.change_data_on_work_proxy(self.data_queue)
                continue
            if autobasket['status'] == 103:
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                    print('stop - complate 103 process')
                    i += 1
                    continue

            if autobasket['status'] == 104:
                self.fail_profiles.append(info)
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                    
                    print('stop - complate 104 process')
                #ЗДЕСЬ ЗАКОНЧИЛ
                print('STATUS: 104')
                i += 1
                continue

            if autobasket['status'] == 105:
                self.fail_profiles.append(info)
                self.wb_browser.stop_doplhin_profile()
                if self.wb_browser.browser != '':
                    self.stop()
                    self.wb_browser.change_data_on_work_proxy(self.data_queue)
                    print('stop - complate 105 process')

                print('STATUS: 105')
                i += 1
            print
            if autobasket['status'] == 102:
                self.wb_browser.stop_doplhin_profile()
                if len(all_info) == 1 or self.target_profile=='':
                    raise SystemExit
            else:
                self.wb_browser.stop_doplhin_profile()
                
                if self.wb_browser.browser != '':
                    self.stop()
                    print('stop - complate 100 process')
                    if len(all_info) == 1 or self.target_profile=='':
                        print('SystemExit')
                        raise SystemExit
                i += 1

    def start(self):
        if self.target_profile != '':

            all_info = [self.target_profile]
            # Проверяем не пустая ли информация
            count_none = 0
            for info in all_info[0]:
                if info == None:
                    count_none += 1
            if count_none == len(all_info[0]):
                return
            
        else:
            excel_parser:excel_parser = EXCEL_PARSER()
            all_info = excel_parser.get_values()
        
        # Основной цикл
        try:
            self.start__process(all_info)
        except SystemExit:
            return
        except:
            print('Неожиданная ошибка')
            print(traceback.format_exc())
        # Цикл на обработу ошибок
        if len(self.fail_profiles) != 0:
            wb_browser:WB_BROWSER = WB_BROWSER(profile_name='')
            self.wb_browser = wb_browser
            self.wb_browser.get_all_proxy()
            all_proxys_id = [proxy['id'] for proxy in self.wb_browser.get_all_proxy()]
            work_proxy = self.wb_browser.get_data_on_queue()
            i = 0
            status = 106
            while len(self.fail_profiles) > 0:
                profile = self.fail_profiles[0]
                if work_proxy == None:
                    
                    j = True
                    while j:
                        try:
                            self.wb_browser.change_proxy_for_target_profile({'proxy[id]':self.wb_browser.get_data_on_queue()}, wb_browser.get_profile_id_on_profile_name(profile[1]))
                            autobasket_for_one_product = self.autobasket_for_one_product(profile, all_info)
                            if autobasket_for_one_product == 106:
                                self.wb_browser.stop_doplhin_profile()
                                if self.wb_browser.browser != '':
                                    self.stop()
                                    print('stop - complate 106 two')
                                print('STATUS: 106')
                                self.wb_browser.change_data_on_work_proxy(self.data_queue)
                                continue
                            status = autobasket_for_one_product['status']
                            if status == 105:
                                self.wb_browser.stop_doplhin_profile()
                                if self.wb_browser.browser != '':
                                    self.stop()
                                    print('stop - complate 105 two')
                                j = False
                                continue

                            if status in [100,101,102]:
                                j = False
                                i += 1
                                self.fail_profiles.remove(profile)
                                self.wb_browser.stop_doplhin_profile()
                                if self.wb_browser.browser != '':
                                    self.stop()
                                    print('stop - complate 100 two')
                                    if len(all_info) == 1 or self.target_profile=='':
                                        print('SystemExit')
                                        raise SystemExit
                                break
                            self.wb_browser.stop_doplhin_profile() 
                            self.wb_browser.change_data_on_work_proxy(self.data_queue) 
                            if self.wb_browser.browser != '':
                                self.stop()
                                print('stop - complate 106 last')

                            j = False
                            continue
                        except SystemExit:
                            raise SystemExit
                        except Exception as e:
                            continue
                else:
                    self.wb_browser.change_proxy_for_target_profile({'proxy[id]':work_proxy}, profile[1])
                    status = ''
                    j = True
                    while j:
                        try:
                            autobasket_for_one_product = self.autobasket_for_one_product(profile, all_info)
                            status = autobasket_for_one_product['status']
                            if status == 105:
                                print('STATUS: 105 ')
                                time.sleep(0.5)
                                print('Профиль недостпуен, пытаюсь подключиться...')
                                self.wb_browser.stop_doplhin_profile()
                                if self.wb_browser.browser != '':
                                    self.stop()
                                    print('stop - complate 105 three')
                                continue

                            if status == 104:
                                print('PT: 104')
                                work_proxy = None
                                j = False
                                self.wb_browser.stop_doplhin_profile()
                                if self.wb_browser.browser != '':
                                    self.stop()
                                    self.wb_browser.change_data_on_work_proxy(self.data_queue)
                                    print('stop - complate')
                        except Exception as ex:
                            self.wb_browser.stop_doplhin_profile()
                            
                            if self.wb_browser.browser != '':
                                self.stop()
                                print('stop - complate')
                    
                    if status == 102:
                        print('STATUS: 102')
                        i += 1
                        self.fail_profiles.remove(profile)
                        self.wb_browser.stop_doplhin_profile()
                        if self.wb_browser.browser != '':
                            self.stop()
                            print('stop - complate')
                        continue
                    
                    if status == 103:
                        print('STATUS: 103')
                        result = [item for item in profile if item != None]
                        result.append(f'Ошибка: не добавлен в корзину')
                        self.report.add_product(result)
                        i += 1
                        j = False
                        self.fail_profiles.remove(profile)
                        self.wb_browser.stop_doplhin_profile()
                        if self.wb_browser.browser != '':
                            self.stop()
                            print('stop - complate')
                    else:
                        print('PT: 101,103')
                        self.fail_profiles.remove(profile)
                        i += 1
                        self.wb_browser.stop_doplhin_profile()
                        if self.wb_browser.browser != '':
                            self.stop()
                            print('stop - complate')
                            if len(all_info) == 1 or self.target_profile=='':
                                print('SystemExit')
                                raise SystemExit
                        continue

    def stop(self):
        if self.wb_browser.browser != '':
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
        wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 20, poll_frequency=0.1)
        search_input = wait.until(EC.visibility_of_element_located(
            (By.ID, 'searchInput')
        ))
        # search_input = self.wb_browser.browser.find_element(By.ID, 'searchInput')

        stop = True
        i = 0
        while text_in_search and stop:
            search_input.clear()
            if ' ' in self.search_text:
                arr_words = self.search_text.split(' ')
                for word in arr_words:
                    search_input.send_keys(word + ' ')
                    time.sleep(randrange(2,3))
                search_input_text = self.wb_browser.browser.execute_script("return document.getElementById('searchInput').value")
                if search_input_text.strip() == self.search_text:
                    text_in_search = False
                    stop = False
                else:
                    i += 1
                    if i == 3:
                        return {'status': 104}
            else:
                search_input.send_keys(self.search_text)
                text_in_search = False
                stop = False
        search_input.send_keys(Keys.ENTER)
    
    def load_page(self):
        count_scroll_px = 100
        try:
            wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 20, poll_frequency=0.1)
            height_scroll = wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, 'catalog-page__main')
            ))
            height_scroll = int(self.wb_browser.browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
        except:
            return {'status': 104}
        while count_scroll_px < height_scroll:
            self.wb_browser.browser.execute_script(f"window.scrollTo(0, {count_scroll_px})")
            count_scroll_px += 250
            height_scroll = int(self.wb_browser.browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            time.sleep(0.4)
        self.wb_browser.browser.execute_script(f"window.scrollTo(0, 200)")

    def get_all_products(self):
        try:
            wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 30, poll_frequency=0.1)
            container = wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, 'product-card-list')
            ))

            # container = self.wb_browser.browser.find_element(By.CLASS_NAME, 'product-card-list')
        except:
            print('ERROR: not find product-card-list')
            self.wb_browser.start_doplhin_profile()
            self.wb_browser.stop()
            return {'status': 104}
        
        wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 20, poll_frequency=0.1)
        proucts = wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'product-card')
        ))
        # proucts = container.find_elements(By.CLASS_NAME, 'product-card')
        return proucts
    
    def product_is_valid(self, product):
        try:
            if int(self.product_number) == int(product.get_attribute('data-nm-id')):
                return True
        except:
            return False
        return False    
    
    def add_product_in_basket(self, product):
        product_clicked = True
        while product_clicked:
            product.click()
            time.sleep(1)
            if '#' in self.wb_browser.browser.current_url:
                product.click()
            else:
                product_clicked = False
        self.wb_browser.browser.execute_script('window.scrollTo(0,0)')
        time.sleep(3)

        # self.check_characteristics()
        # self.check_reviews()
        # self.check_reviews_text()
        self.check_product_photos()

        if self.size != None:
            size_list = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'sizes-list')[0]
            sizes = size_list.find_elements(By.TAG_NAME, 'li')

        if self.size != None:
            for size in sizes:
                label = size.find_element(By.TAG_NAME, 'label')
                if label.find_element(By.CLASS_NAME, 'sizes-list__size').text == str(self.size):
                    label_classes = label.get_attribute('class')
                    if  (len(label_classes.split(' ')) == 2 or label_classes == 'j-size sizes-list__button active') and label_classes != 'j-size sizes-list__button disabled':
                        label.click()

                        self.wb_browser.browser.find_elements(By.CLASS_NAME, 'btn-main')[4].click()
                        time.sleep(2)
                        return True
                    else:
                        continue
        else:
            self.wb_browser.browser.find_elements(By.CLASS_NAME, 'btn-main')[4].click()
            time.sleep(2)
            return True
        
        return False
    
    def find_current_product(self):
        conunt_page = 1
        while conunt_page <= self.max_pages:
            load = self.load_page()
            if type(load) == {}:
                return {'status': 104}

            products = self.get_all_products()
            if products == {'status': 104}:
                return {'status': 104}
            
            for product in products:
                if self.product_is_valid(product):
                    return product
            print(conunt_page)
            next = self.next_page()

            if next == 'max':
                return None
            
            conunt_page += 1
        return None

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
            return 'max'
    
    def product_in_basket(self):
        try:
            self.wb_browser.browser.get('https://www.wildberries.ru/lk/basket')
            wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 60, poll_frequency=0.3)
            products_links_in_basket = wait.until(EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'good-info__title')
            ))
            # products_links_in_basket = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'good-info__title')
            
            for product_link in products_links_in_basket:
                link_articul = product_link.get_attribute('href').split('/')[4]
                if link_articul == str(self.product_number):
                    return True
            return False
        except:
            return False

    def check_characteristics(self):
        self.wb_browser.browser.execute_script('window.scrollTo(0, 600)')
        action = ActionChains(self.wb_browser.browser)
        buttons_characteristics = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'collapsible__toggle-wrap')
        print('check_characteristics')
        time.sleep(4)
        for button in  buttons_characteristics:
            action.move_to_element(button)
            button.find_element(By.TAG_NAME, 'button').click()
            time.sleep(randrange(1,3))

    def check_reviews(self):
        try:
            self.wb_browser.browser.execute_script('window.scrollTo(0, 1350)')
            # wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 10, poll_frequency=0.1)
            # comment_card = wait.until(EC.visibility_of_all_elements_located(
            #     (By.CLASS_NAME, 'swiper-wrapper')
            # ))
            comment_card = self.wb_browser.browser.find_elements(By.CLASS_NAME, 'swiper-wrapper')[2]
            print('check_reviews')
            review = comment_card[2].find_element(By.TAG_NAME, 'div')
            action = ActionChains(self.wb_browser.browser)
            action.move_to_element(review)
            time.sleep(5)
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
            return {'status': 104}
            

    def check_reviews_text(self):
        scroll_y = 1500

        self.wb_browser.browser.execute_script(f'window.scrollTo(0, {scroll_y})')
        # wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 10, poll_frequency=0.1)
        # comment_card = wait.until(EC.visibility_of_element_located(
        #     (By.CLASS_NAME, 'comment-card')
        # ))
        time.sleep(4)
        comment_card = self.wb_browser.browser.find_element(By.CLASS_NAME, 'comment-card').find_element(By.CLASS_NAME, 'comment-card__content')
        print('check_reviews_text')
        action = ActionChains(self.wb_browser.browser)
        action.move_to_element(comment_card).perform()
        # self.wb_browser.browser.execute_script('arguments[0].scrollIntoView();', comment_card)
        time.sleep(2)
        comment_card.click()
        time.sleep(2)

        for i in range(2):
            self.wb_browser.browser.execute_script(f'window.scrollTo(0, {scroll_y})')
            scroll_y += 200
            time.sleep(0.4)
        # wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 10, poll_frequency=0.1)
        # element = wait.until(EC.visibility_of_element_located(
        #     (By.CLASS_NAME, 'product-feedbacks__back')
        # ))
        time.sleep(2)
        back_button = self.wb_browser.browser.find_element(By.CLASS_NAME, 'product-feedbacks__back')
        action.move_to_element(back_button)
        time.sleep(4)
        back_button.click()
        self.wb_browser.browser.execute_script(f'window.scrollTo(0, 0)')
        time.sleep(2)


    def check_product_photos(self):
        wait: WebDriverWait = WebDriverWait(self.wb_browser.browser, 30, poll_frequency=0.1)
        photos_wrapper = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'swiper-wrapper')
        ))
        # photos_wrapper = self.wb_browser.browser.find_element(By.CLASS_NAME, 'swiper-wrapper')
        # time.sleep(4)
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

        print('START MANAGE SCRIPT')
        manage_script = MANAGE_SCRIPT(max_pages=5)
        manage_script.start()
