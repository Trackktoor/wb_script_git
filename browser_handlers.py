from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import psutil
import win32gui
import traceback
import queue

class WB_BROWSER():

    def __init__(self, profile_name='', headless=False, quick_collection=False) -> None:
        self.profile_name = profile_name
        if profile_name: self.profile_id = self.get_profile_id_on_profile_name(profile_name=profile_name)
        else: self.profile_id = profile_name

        self.headless = headless
        self.quick_collection = quick_collection

        self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1'
        self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop'

        self.browser = ''

    def get_data_on_queue(queue:queue.Queue):
        res = queue.get(block=True)
        queue.put(res)
        queue.task_done()
        return res
    
    def find_work_proxy(self):

        all_proxys_id = [proxy['id'] for proxy in self.get_all_proxy()]
        for proxy_id in all_proxys_id:
            
            self.change_proxy_for_target_profile(proxy={'proxy[id]':proxy_id}, profile_id=self.profile_id)
            self.initial_selenium_browser(self.profile_name)
            try:
                self.browser.get('https://www.wildberries.ru')
                return proxy_id
            except:
                continue

    def change_data_on_work_proxy(self,data:queue.Queue):
        if not data.empty():
                
            data.put(self.find_work_proxy())
            data.task_done()
        else:
            res = data.get(block=True)
            data.put(res)
            data.task_done()

    def activate_dolphin_window(self):
        try:
            hwnd = win32gui.FindWindow(None,'Dolphin{anty}')  # Должно вернуть hwnd последнего активного окна
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
    # DOLPHI ENTY METHODS
    def start_doplhin_profile(self,profile_name='') -> dict:
        self.activate_dolphin_window()
        if profile_name:
            profile_id = self.get_profile_id_on_profile_name(profile_name)
            if type(profile_id) == {}:
                return profile_id
            self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop'
            self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'
            while True:
                if self.headless:
                    response = requests.get(self.req_url_start + '&headless=1')
                    if 'error' in response.json().keys():
                        self.start_doplhin_profile()
                        time.sleep(2)
                        if 'already running' in response['error']:
                            self.activate_dolphin_window()
                            self.start_doplhin_profile()
                            print('ERROR: DUBLICATE')
                            continue
        
                    return response.json()
                else:
                    response = requests.get(self.req_url_start)
                    if 'error' in response.json().keys():
                        if 'already running' in response.json()['error']:
                            self.activate_dolphin_window()
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
            self.activate_dolphin_window()
            response = requests.get(self.req_url_stop)
        except:
            print(traceback.format_exc())
            return False
        return response.json()
    
    # SELENIUM METHODS
    def initial_selenium_browser(self, profile_name='') -> webdriver.Chrome:
        
        try:
            service = Service('chromedriver-windows-x64.exe')
            response = self.start_doplhin_profile(profile_name)
            if type(response) == {}:
                print('NEW')
                return False
            port = response['automation']['port']
        except Exception as ex:
            try:
                response = requests.get(self.req_url_stop)
            except:
                print('ERROR: ANTY NOT FOUND')
                return False
            
            print('ERROR: BAD PROFIEL - RESTART')
            return False

        options = webdriver.ChromeOptions()
        options.debugger_address = f'127.0.0.1:{port}'
        options.add_argument('--blink-settings=imagesEnabled=false')
        if self.quick_collection:
            """ ВНИМАНИЕ! """
            """ Данная функция может привести к утере данных """
            options.page_load_strategy = 'eager'

        browser = webdriver.Chrome(service=service,options=options)
        browser.set_page_load_timeout(10)
        self.browser = browser
        # if self.headless:
        #     try:
        #         self.browser.set_window_size(1920, 1080)
        #     except:
        #         print('ERROR: SET WINDOW SIZE ')
        #         return False

        return browser
    
    # def check_proxy(self, profile:webdriver.Chrome):
    #     try:
    #         profile.get('https://www.wildberries.ru/')
    #         time.sleep(1)
    #         profile.find_elements(By.CLASS_NAME, 'product-card__link')[5]
    #         return True
    #     except Exception as ex:
    #         if str(ex) == 'STOP':
    #             raise Exception('STOP')
    #         print('')
    #         return False

    def get_profile_id_on_profile_name(self, profile_name):
        profile_name = str(profile_name)
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNGIyZTU5MGNhMjc1NmUzZjUzYzRjNTMyOGUzZjRkZjRiOWJmMDNiNmRjZWM1YTQ5MDUxNjJlMDc4OTNkYTkzMThhMDhmNzZjZDE3ODM0MTgiLCJpYXQiOjE2OTkwNDM3MzguMDkxMjI5LCJuYmYiOjE2OTkwNDM3MzguMDkxMjMsImV4cCI6MTczMDU3OTczOC4wODIyNCwic3ViIjoiMjg3MTQwNCIsInNjb3BlcyI6W119.SpVpJI9F9fI4ljRENdl0bL6EHm_6bI62TNGQ6Qijsc7HUGB2iec3DzsajT6wQWqk5GvOnHGA86O-rlVG-bFJYart79Ep9bPfgWZL5hj0UsazmOfXJW1cr1BWtWGubxRoKfQXFz_qMxoK0p193lpuA4E-DBxoaKFqj_TDk6wIh4dtJrmiDojGhwv6zpIJxim9wR9m1669rRvZm-6DfD8ndUx9Ml5MMW4ubAeabfR4opwa0nGyccbwKxESZbAwYBDuDkmVkbZVFxhRdFVUGXUHfAaS7MKJJN6bplUHkGKxbSZriL6xP8_mCDi-OvYhJITQntGCO0JbI3mpoC7QJWX9CQf9lLg5uYpFdUaMk4_OkMGvtyXln_qUH50peH_hNSPGymT6GQy0uD6GlRtoAQTjnBHmLz1xUlO19m7lkvYrqARXVXRZ-QCdhaStKI3Th60uvb4aSy8JhxZus090aC8QhqdAi4lnQyEG_dHFLSdLU--mYeXVKCYdpR7t9tkIwXwQ_C7AlIsUIq3EO_sxPzP6gspTCsJoe2Ig0ohilaaQx9zik7nQEdlrfyU-0aTN7khZYe0g6cxyU35C_cYnTIRFPFCxEOrBPGZksswgRWPVgZhY0YsaCnVyvsipeM8BA_lzRghZ8zyZILYaDei80XRn-YvBNG2nRv1Bw5zsRDKmlCM'
        }
        profile = requests.request("GET", f'https://dolphin-anty-api.com/browser_profiles?query={profile_name}', headers=headers)
        if profile.json()['data'][0]['name'] == profile_name:
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
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNGIyZTU5MGNhMjc1NmUzZjUzYzRjNTMyOGUzZjRkZjRiOWJmMDNiNmRjZWM1YTQ5MDUxNjJlMDc4OTNkYTkzMThhMDhmNzZjZDE3ODM0MTgiLCJpYXQiOjE2OTkwNDM3MzguMDkxMjI5LCJuYmYiOjE2OTkwNDM3MzguMDkxMjMsImV4cCI6MTczMDU3OTczOC4wODIyNCwic3ViIjoiMjg3MTQwNCIsInNjb3BlcyI6W119.SpVpJI9F9fI4ljRENdl0bL6EHm_6bI62TNGQ6Qijsc7HUGB2iec3DzsajT6wQWqk5GvOnHGA86O-rlVG-bFJYart79Ep9bPfgWZL5hj0UsazmOfXJW1cr1BWtWGubxRoKfQXFz_qMxoK0p193lpuA4E-DBxoaKFqj_TDk6wIh4dtJrmiDojGhwv6zpIJxim9wR9m1669rRvZm-6DfD8ndUx9Ml5MMW4ubAeabfR4opwa0nGyccbwKxESZbAwYBDuDkmVkbZVFxhRdFVUGXUHfAaS7MKJJN6bplUHkGKxbSZriL6xP8_mCDi-OvYhJITQntGCO0JbI3mpoC7QJWX9CQf9lLg5uYpFdUaMk4_OkMGvtyXln_qUH50peH_hNSPGymT6GQy0uD6GlRtoAQTjnBHmLz1xUlO19m7lkvYrqARXVXRZ-QCdhaStKI3Th60uvb4aSy8JhxZus090aC8QhqdAi4lnQyEG_dHFLSdLU--mYeXVKCYdpR7t9tkIwXwQ_C7AlIsUIq3EO_sxPzP6gspTCsJoe2Ig0ohilaaQx9zik7nQEdlrfyU-0aTN7khZYe0g6cxyU35C_cYnTIRFPFCxEOrBPGZksswgRWPVgZhY0YsaCnVyvsipeM8BA_lzRghZ8zyZILYaDei80XRn-YvBNG2nRv1Bw5zsRDKmlCM'
        }
        new_proxy = requests.request("PATCH", f'https://dolphin-anty-api.com/browser_profiles/{profile_id}', headers=headers,data=proxy)
    def get_all_proxy(self):
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNGIyZTU5MGNhMjc1NmUzZjUzYzRjNTMyOGUzZjRkZjRiOWJmMDNiNmRjZWM1YTQ5MDUxNjJlMDc4OTNkYTkzMThhMDhmNzZjZDE3ODM0MTgiLCJpYXQiOjE2OTkwNDM3MzguMDkxMjI5LCJuYmYiOjE2OTkwNDM3MzguMDkxMjMsImV4cCI6MTczMDU3OTczOC4wODIyNCwic3ViIjoiMjg3MTQwNCIsInNjb3BlcyI6W119.SpVpJI9F9fI4ljRENdl0bL6EHm_6bI62TNGQ6Qijsc7HUGB2iec3DzsajT6wQWqk5GvOnHGA86O-rlVG-bFJYart79Ep9bPfgWZL5hj0UsazmOfXJW1cr1BWtWGubxRoKfQXFz_qMxoK0p193lpuA4E-DBxoaKFqj_TDk6wIh4dtJrmiDojGhwv6zpIJxim9wR9m1669rRvZm-6DfD8ndUx9Ml5MMW4ubAeabfR4opwa0nGyccbwKxESZbAwYBDuDkmVkbZVFxhRdFVUGXUHfAaS7MKJJN6bplUHkGKxbSZriL6xP8_mCDi-OvYhJITQntGCO0JbI3mpoC7QJWX9CQf9lLg5uYpFdUaMk4_OkMGvtyXln_qUH50peH_hNSPGymT6GQy0uD6GlRtoAQTjnBHmLz1xUlO19m7lkvYrqARXVXRZ-QCdhaStKI3Th60uvb4aSy8JhxZus090aC8QhqdAi4lnQyEG_dHFLSdLU--mYeXVKCYdpR7t9tkIwXwQ_C7AlIsUIq3EO_sxPzP6gspTCsJoe2Ig0ohilaaQx9zik7nQEdlrfyU-0aTN7khZYe0g6cxyU35C_cYnTIRFPFCxEOrBPGZksswgRWPVgZhY0YsaCnVyvsipeM8BA_lzRghZ8zyZILYaDei80XRn-YvBNG2nRv1Bw5zsRDKmlCM',
            'Content-Type': 'application/json'
        }
        all_proxys = requests.request("GET", 'https://dolphin-anty-api.com/proxy/', headers=headers)
        return all_proxys.json()['data']

    def stop(self) -> None:
        self.stop_doplhin_profile()
        self.browser.quit()

# print(WB_BROWSER('182637111').get_all_proxy()[0]['id'])

if __name__ == '__main__':
    wb_browser = WB_BROWSER('12').initial_selenium_browser()
    count_scroll_px = 100
    while True:
        try:
            height_scroll = int(wb_browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            break
        except:
            print( wb_browser.execute_script("return document.readyState"))
            time.sleep(0.5)
            print(104)
    while count_scroll_px < height_scroll:
        if wb_browser.execute_script("return document.readyState") == 'complete':
            print('complate')
            wb_browser.execute_script(f"window.scrollTo(0, {count_scroll_px})")
            count_scroll_px += 250
            height_scroll = int(wb_browser.execute_script("return document.getElementsByClassName('catalog-page__main')[0].scrollHeight"))
            time.sleep(0.4)
        else:
            print('wait..')