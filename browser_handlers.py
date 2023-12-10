from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
import time
import win32gui
import traceback


class WB_BROWSER():

    def __init__(self, profile_name='', headless=False, quick_collection=False) -> None:    
        self.token = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNDc2OWYzMDljNzgxNDBhOTNhZTU3YzMyN2NmMDJkY2JmZjAzY2YyNGM5N2RiMDQ3MmMxNDZmZDcyNDk1MGU1NmQwYjdlNDY5Y2FjOWJmZjAiLCJpYXQiOjE3MDIyMjY0NTYuODkyMTUyLCJuYmYiOjE3MDIyMjY0NTYuODkyMTU1LCJleHAiOjE3MDQ4MTg0NTYuODc4NzU4LCJzdWIiOiIyMTI2NjUyIiwic2NvcGVzIjpbXX0.tI9ag1LFtAQgZL8M1PCNVpZFP6Mg7epVofhDIZs2PdfBZjE4zLR6eor69RhRvnhsT0OeMcWUwlfJEu2LZ1k2bLoOwRKjVbPOZu5ORm7henNIY4cQUi8kA7Vig12XEPSgdyGgTKEnzzOB_GmVoud-oxxcY7JY0zvqWVoy_IXQB7W-GkhARD_kXmr8ODY_DcPEvGCtfNQagGqkhXcGzFbbFCPrkzGIJ6Q1hX8N5RZR2dp52m7RmibbtnipxB3MjADzrNgpqTFNozLD8ia32G8OfA5OQSYogRYDBMUtgDJBnRw-IWQumvqNjpkDIwp4um932RBP03X2fBALoExqFcaHoh6oVAEQhoaRvRWnXvwCwrkgoSxm5D_fsMoBcoGeTNe3yurwljK7NNf47aRyGVUuke6vsWutsnfLChOc7giHLXE2K6_QUvGHkP7_4vuq6cOXGfI-pM5gBagvgxOedTBj4O08HfucnwZzvlekXYzb0M56dTuH1xWz8lgs8oC-uMJkp5GqUJ63JMcWcUcQhpNzsjUn34ZDrIA2CKdiCnG7R7soGbgnB6crEmGOEew6CdCz4XakMcW1tA3mk-0Kbb3Th8ydHFMausBaW6Na5gyt2fMi8VG9txRaITwlHP2Oorj1ebH1L2raOA3qoCJ9yUicgDwF8KKE589qCoCK6fKbZUQ'
        # print('pofile_name: '+str(bool(profile_name)))
        if profile_name: self.profile_id = self.get_profile_id_on_profile_name(profile_name=profile_name)
        else: self.profile_id = profile_name
        self.profile_name = profile_name
        self.headless = headless
        self.quick_collection = quick_collection
        self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1'
        self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop'

        self.browser = ''

    def activate_dolphin_window(self):
        try:
            hwnd = win32gui.FindWindow(None,'Dolphin{anty}')  # Должно вернуть hwnd последнего активного окна
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
    def auhorization_dolphin_anty(self):
        try:
            response = requests.post('http://localhost:3001/v1.0/auth/login-with-token', data={'token':self.token.split(' ')[1]})
        except:
            print(traceback.format_exc())
            return False
        return response.json()
    # DOLPHI ENTY METHODS
    def start_doplhin_profile(self,profile_name='') -> dict:
        if not self.profile_id:
            profile_id = self.get_profile_id_on_profile_name(profile_name)
            if type(profile_id) == {}:
                return profile_id
            self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop'
            self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'
            while True:
                if self.headless:
                    response = requests.get(self.req_url_start + '&headless=1')
                    if 'error' in response.json().keys():
                        if 'already running' in response.json()['error']:
                            time.sleep(1)
                            self.stop_doplhin_profile()
                            print('ERROR: DUBLICATE')
                            continue
                    print(response.json())
        
                    return response.json()
                else:
                    response = requests.get(self.req_url_start)
                    if 'error' in response.json().keys():
                        if 'already running' in response.json()['error']:
                            self.stop_doplhin_profile()
                            print('ERROR: DUBLICATE')
                            time.sleep(1)
                            continue

                    return response.json()
        else:
            if self.headless:
                response = requests.get(self.req_url_start + '&headless=1')
                return response.json()
            else:
                response = requests.get(self.req_url_start)
                return response.json()
        
    def stop_doplhin_profile(self) -> dict:
        try:
            response = requests.get(self.req_url_stop)
            # len_line = len('PROFILE ' + str(self.profile_name) +  ' STOP: ' + str(response.json()))
            # print(
            #     f"\n{ '-' * len_line }\n" +
            #     'PROFILE ' + str(self.profile_name) +  ' STOP: ' + str(response.json()) +
            #     f"\n{ '-' * len_line }\n"
            #     )
        except:
            # print(traceback.format_exc())
            return False
        return response.json()
    
    def close_tabs_browser(self, browser:webdriver.Chrome):
        windows = browser.window_handles[1:]
        # Переключиться на каждую вкладку и закрыть ее
        for window in windows:
            try:
                browser.switch_to.window(window)
                browser.close()
            except:
                continue

        # Вернуться к исходной вкладке

        # browser.switch_to.window(browser.window_handles[0])

    # SELENIUM METHODS
    def initial_selenium_browser(self, profile_name='') -> webdriver.Chrome:
        no_unauthorized = True
        port = ''
        while no_unauthorized:
            try:
                service = Service('chromedriver-windows-x64.exe')
                response = self.start_doplhin_profile(profile_name)
                # len_line = len('PROFILE ' + str(self.profile_name) +  ' START: ' + str(response))
                # print(
                #     f"\n{ '-' * len_line }\n" +
                #     'PROFILE ' + str(self.profile_name) +  ' START: ' + str(response) +
                #     f"\n{ '-' * len_line }\n"
                # )
                if 'error' in response.keys():
                    if response['error'] == 'Error: Ошибка проверки соединения с прокси':
                        return {'status': 104}
                    if response['error'] == 'unauthorized':
                        time.sleep(5)
                        continue
                    if 'ggr:' in response['error']:
                        time.sleep(5)
                        continue
                    if 'EPERM' in response['error']:
                        print(f'"EPEM" in {response["message"]} == {"EPERM" in response["message"]}')
                        return {'status':108}
                print(response)

                port = response['automation']['port']
                break
            except Exception as ex:
                try:
                    response = requests.get(self.req_url_stop)
                except:
                    print('ERROR: ANTY NOT FOUND')
                    return False
                print('TRACEBACK')
                print(traceback.format_exc())

        options = webdriver.ChromeOptions()
        options.debugger_address = f'127.0.0.1:{port}'
        if self.headless:
            options.add_argument("start-maximized")
        options.add_argument('--blink-settings=imagesEnabled=false')
        if self.quick_collection:
            """ ВНИМАНИЕ! """
            """ Данная функция может привести к утере данных """
            options.page_load_strategy = 'eager'

        browser = webdriver.Chrome(service=service,options=options)
        browser.set_page_load_timeout(10)
        self.browser = browser
        if len(browser.window_handles) > 1:
            self.close_tabs_browser(browser=browser)

        return browser

    def get_profile_id_on_profile_name(self, profile_name):
        headers = {
            'Authorization': self.token
        }
        profile = requests.request("GET", 'https://dolphin-anty-api.com/browser_profiles?query=' + str(profile_name), headers=headers)
       
        profiles_str = list(map(lambda profile: profile['name'], profile.json()['data']))

        if len(profiles_str) == 0:
            profiles_str = ['error: not found..']
        else:
            profiles_str = str(profiles_str)

        # print(
        #     "\n---------------------------------------------------------------------\n"
        #     +
        #     'RESPONSE FOR GET PROFILE BY NAME ' + profiles_str
        #     +
        #     "\n---------------------------------------------------------------------\n"
        # )
        if profile.json()['data'][0]['name'] == str(profile_name):
            return profile.json()['data'][0]['id']
        else:
            for profile_res in profile.json()['data']:
                if profile_res['name'] == profile_name:
                        return profile_res['id']
                
    def change_proxy_for_target_profile(self, proxy, profile_id):
        #proxy: {
            #'type': 'http',
            #'host': '185.39.148.213',
            #'port': '8000',
            #'login': '1scbDn',
            #'password': '2AQ8zX',
        #}
        #or
        #proxy: {
            #'id': 'id прокси',
        #}
        headers = {
            'Authorization': self.token
        }
        new_proxy = requests.request("PATCH", f'https://dolphin-anty-api.com/browser_profiles/{profile_id}', headers=headers,data=proxy)
    def get_all_proxy(self):
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
        all_proxys = requests.request("GET", 'https://dolphin-anty-api.com/proxy/', headers=headers)
        return all_proxys.json()['data']

    def stop(self) -> None:
        self.browser.quit()
        self.stop_doplhin_profile()

# print(WB_BROWSER('182637111').get_all_proxy()[0]['id'])

if __name__ == '__main__':
    wb_browser = WB_BROWSER('12').initial_selenium_browser()
    count_scroll_px = 100
    while True:
        try:
            height_scroll = int(wb_browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            break
        except:
            # print( wb_browser.execute_script("return document.readyState"))
            time.sleep(0.5)
            # print(104)
    while count_scroll_px < height_scroll:
        if wb_browser.execute_script("return document.readyState") == 'complete':
            # print('complete')
            wb_browser.execute_script(f"window.scrollTo(0, {count_scroll_px})")
            count_scroll_px += 250
            height_scroll = int(wb_browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            time.sleep(0.4)
        else:
            # print('wait..')
            pass