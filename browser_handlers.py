from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import traceback

class WB_BROWSER():

    def __init__(self, profile_name='', headless=False, quick_collection=False) -> None:
        if profile_name: self.profile_id = self.get_profile_id_on_profile_name(profile_name=profile_name)
        else: self.profile_id = profile_name

        self.headless = headless
        self.quick_collection = quick_collection

        self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1'
        self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop'

        self.browser = ''

    # DOLPHI ENTY METHODS
    def start_doplhin_profile(self,profile_name='') -> dict:
        if profile_name:
            profile_id = self.get_profile_id_on_profile_name(profile_name)
            self.req_url_stop = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop'
            self.req_url_start = f'http://127.0.0.1:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'

            if self.headless:
                response = requests.get(self.req_url_stop + '&headless=1')
                return response.json()
            else:
                response = requests.get(self.req_url_stop)
                return response.json()
        else:
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
    def initial_selenium_browser(self, profile_name='') -> webdriver.Chrome:
        try:
            service = Service('chromedriver-windows-x64.exe')
            response = self.start_doplhin_profile(profile_name)
            print(response)
            port = response['automation']['port']
        except Exception as ex:
            response = requests.get(self.req_url_stop)
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
        self.browser.set_window_size(1920, 1080)

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

    def get_profile_id_on_profile_name(self, profile_name):
        profile_name = str(profile_name)
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiODAwYTA0MzNhMWYwMDY3NzIzYmEyNjRlODBjY2Q1MzJjNWQ0NmYwYmQwZmVmNTY0MTAzMGRhMjFiNGIyMjc0ZGMwNGExYTc4ZTZkMjhmZGYiLCJpYXQiOjE3MDAyMDM2NDUuMDIxMjU1LCJuYmYiOjE3MDAyMDM2NDUuMDIxMjU3LCJleHAiOjE3MDA4MDg0NDUuMDEwNzA4LCJzdWIiOiIyMTI2NjUyIiwic2NvcGVzIjpbXX0.iYDF0_NXSPGVg10bCpj0Zn6l-0rM7nXxYSMAq2Hf7i5SLJbKnJi0rB0_UHT50CjNkeRQ3v6S9aNYRBDxR8ErFXhu02YSRC8ciJQNio7OT8rAn6Pm0l9QqukWZib53X1GtP21yToQmyoKTR9Fu-e7H_CjkxC-NnX09IWH69O3dP28y2KfFxKS5Mz6eu5G9L4ujpt0fl7_NYRhBBVUQWshyH2b6-DXjw5eHHPerCAv0nTy576A2OoWWZHAJg-QKHXnPNfUskEvJcod4Ve4AvYBF_XR70Coo35eprMNEL4k1zGyDFZXpyC3aF4Tqp4ONJHV7j7AkMSwBKs5OuX0o2A262E6z4rqfdYocOpltajIj6VmxFIYYlFb4BD6xrC_0OnrGX6MMI2wlk35grnGg6xbCrrrIaCKEoogTCKONns7HWvuQ_15MtnIX6PWwH6QdnprAVw4xMaxQ_owZE1ZHEWaozXQSfxXvjNLTHSaZA8BrTU0bZe_clh-befFoOxg4jChbutQ7FP1piLjtPKNpdGmuyjHC6h0eDOGPw3gRKejFHOyQULPhwumxtCzW2EaoebET3O9TZ23muziFhhts3HHKoR1575dJNXOWMiWSq_TqOj-PnWCieE1zYQ03bfleLcwfSSFAsf31xdj9KIXcKhdPtlW2fS7G4dtTuUxIjWL5PE'
        }
        profile = requests.request("GET", f'https://dolphin-anty-api.com/browser_profiles/', headers=headers,data={'query':profile_name})
        print('PROFILE NAME = ' + profile_name)
        return list(filter(lambda profile: profile['name']==profile_name, profile.json()['data']))[0]['id']

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
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiODAwYTA0MzNhMWYwMDY3NzIzYmEyNjRlODBjY2Q1MzJjNWQ0NmYwYmQwZmVmNTY0MTAzMGRhMjFiNGIyMjc0ZGMwNGExYTc4ZTZkMjhmZGYiLCJpYXQiOjE3MDAyMDM2NDUuMDIxMjU1LCJuYmYiOjE3MDAyMDM2NDUuMDIxMjU3LCJleHAiOjE3MDA4MDg0NDUuMDEwNzA4LCJzdWIiOiIyMTI2NjUyIiwic2NvcGVzIjpbXX0.iYDF0_NXSPGVg10bCpj0Zn6l-0rM7nXxYSMAq2Hf7i5SLJbKnJi0rB0_UHT50CjNkeRQ3v6S9aNYRBDxR8ErFXhu02YSRC8ciJQNio7OT8rAn6Pm0l9QqukWZib53X1GtP21yToQmyoKTR9Fu-e7H_CjkxC-NnX09IWH69O3dP28y2KfFxKS5Mz6eu5G9L4ujpt0fl7_NYRhBBVUQWshyH2b6-DXjw5eHHPerCAv0nTy576A2OoWWZHAJg-QKHXnPNfUskEvJcod4Ve4AvYBF_XR70Coo35eprMNEL4k1zGyDFZXpyC3aF4Tqp4ONJHV7j7AkMSwBKs5OuX0o2A262E6z4rqfdYocOpltajIj6VmxFIYYlFb4BD6xrC_0OnrGX6MMI2wlk35grnGg6xbCrrrIaCKEoogTCKONns7HWvuQ_15MtnIX6PWwH6QdnprAVw4xMaxQ_owZE1ZHEWaozXQSfxXvjNLTHSaZA8BrTU0bZe_clh-befFoOxg4jChbutQ7FP1piLjtPKNpdGmuyjHC6h0eDOGPw3gRKejFHOyQULPhwumxtCzW2EaoebET3O9TZ23muziFhhts3HHKoR1575dJNXOWMiWSq_TqOj-PnWCieE1zYQ03bfleLcwfSSFAsf31xdj9KIXcKhdPtlW2fS7G4dtTuUxIjWL5PE'
        }
        new_proxy = requests.request("PATCH", f'https://dolphin-anty-api.com/browser_profiles/{profile_id}', headers=headers,data=proxy)
    def get_all_proxy(self):
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiODAwYTA0MzNhMWYwMDY3NzIzYmEyNjRlODBjY2Q1MzJjNWQ0NmYwYmQwZmVmNTY0MTAzMGRhMjFiNGIyMjc0ZGMwNGExYTc4ZTZkMjhmZGYiLCJpYXQiOjE3MDAyMDM2NDUuMDIxMjU1LCJuYmYiOjE3MDAyMDM2NDUuMDIxMjU3LCJleHAiOjE3MDA4MDg0NDUuMDEwNzA4LCJzdWIiOiIyMTI2NjUyIiwic2NvcGVzIjpbXX0.iYDF0_NXSPGVg10bCpj0Zn6l-0rM7nXxYSMAq2Hf7i5SLJbKnJi0rB0_UHT50CjNkeRQ3v6S9aNYRBDxR8ErFXhu02YSRC8ciJQNio7OT8rAn6Pm0l9QqukWZib53X1GtP21yToQmyoKTR9Fu-e7H_CjkxC-NnX09IWH69O3dP28y2KfFxKS5Mz6eu5G9L4ujpt0fl7_NYRhBBVUQWshyH2b6-DXjw5eHHPerCAv0nTy576A2OoWWZHAJg-QKHXnPNfUskEvJcod4Ve4AvYBF_XR70Coo35eprMNEL4k1zGyDFZXpyC3aF4Tqp4ONJHV7j7AkMSwBKs5OuX0o2A262E6z4rqfdYocOpltajIj6VmxFIYYlFb4BD6xrC_0OnrGX6MMI2wlk35grnGg6xbCrrrIaCKEoogTCKONns7HWvuQ_15MtnIX6PWwH6QdnprAVw4xMaxQ_owZE1ZHEWaozXQSfxXvjNLTHSaZA8BrTU0bZe_clh-befFoOxg4jChbutQ7FP1piLjtPKNpdGmuyjHC6h0eDOGPw3gRKejFHOyQULPhwumxtCzW2EaoebET3O9TZ23muziFhhts3HHKoR1575dJNXOWMiWSq_TqOj-PnWCieE1zYQ03bfleLcwfSSFAsf31xdj9KIXcKhdPtlW2fS7G4dtTuUxIjWL5PE',
            'Content-Type': 'application/json'
        }
        all_proxys = requests.request("GET", 'https://dolphin-anty-api.com/proxy/', headers=headers)
        print(all_proxys)
        return all_proxys.json()['data']

    def stop(self) -> None:
        self.stop_doplhin_profile()
        self.browser.quit()

# print(WB_BROWSER('182637111').get_all_proxy()[0]['id'])