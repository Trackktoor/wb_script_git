from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import traceback

class WB_BROWSER():

    def __init__(self, profile_id, headless=False, quick_collection=False) -> None:
        self.profile_id = profile_id
        self.headless = headless
        self.quick_collection = quick_collection

        self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1'
        self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop'

        self.browser = ''

    # DOLPHI ENTY METHODS
    def start_doplhin_profile(self) -> dict:
        if self.headless:
            response = requests.get(self.req_url_start + '&headless=1')
            return response.json()
        else:
            response = requests.get(self.req_url_start)
            return response.json()

        
    def stop_doplhin_profile(self) -> dict:
        response = requests.get(self.req_url_stop)
        return response.json()
    
    # SELENIUM METHODS
    def initial_selenium_browser(self) -> webdriver.Chrome:
        while True:
            try:
                service = Service('chromedriver-windows-x64.exe')
                response = self.start_doplhin_profile()
                print(response)
                port = response['automation']['port']
                break
            except Exception as ex:
                if str(ex) == 'STOP':
                    raise Exception('STOP')
                print('1')
                return False

        options = webdriver.ChromeOptions()
        options.debugger_address = f'127.0.0.1:{port}'

        if self.quick_collection:
            """ ВНИМАНИЕ! """
            """ Данная функция может привести к утере данных """
            options.page_load_strategy = 'eager'

        browser = webdriver.Chrome(service=service,options=options)
        browser.set_page_load_timeout(10)
        self.browser = browser

        return browser
    
    def check_proxy(self, profile:webdriver.Chrome):
        try:
            profile.get('https://www.wildberries.ru/')
            time.sleep(1)
            profile.find_elements(By.CLASS_NAME, 'product-card__link')[5]
            return True
        except Exception as ex:
            if str(ex) == 'STOP':
                raise Exception('STOP')
            print('2')
            return False

        

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
        print(all_proxys)
        return all_proxys.json()['data']

    def stop(self) -> None:
        self.stop_doplhin_profile()
        self.browser.quit()

# print(WB_BROWSER('182637111').get_all_proxy()[0]['id'])