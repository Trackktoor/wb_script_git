import tkinter
from tkinter import *
from tkinter import ttk
from multiprocessing import Pool, Process
import psutil
from threading import Thread
from excel_handlers import *
import time

from manage import MANAGE_SCRIPT


def start_autobasket(max_pages_entry='', target_profile=''):
    
    if max_pages_entry: max_pages_entry = int(max_pages_entry)

    manage_script = MANAGE_SCRIPT(max_pages=int(max_pages_entry), target_profile=target_profile )
    manage_script.start()

class WB_PROMOTER(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.process = []

        self.max_pages = 25
        self.master = master

        master.title('WB PROMOTER')
        master.geometry('800x300')
        master.resizable(False, False)
        master.iconbitmap(default='logo.ico')
        master.resizable(False, False)

        master.window_title = ttk.Label(font=18,text='WB PROMOTER')
        master.window_title.pack(pady=20)

        master.btn_load1 = ttk.Button(text='Загрузить ТЗ Excel')
        master.btn_load1.place(x=50, y=100, height=50)

        master.excel_template_link = Button(text='Шаблон для ТЗ', bg=self.cget('background'),fg='blue',borderwidth=0)
        master.excel_template_link.place(x=50, y=158)

        """  
            Чтобы открыть папку:
            def foo():
                os.system("start explorer C:/Users/evamo/Documents/")
        """

        master.btn_load2 = ttk.Button(text='Старт', command=self.start_loading,)
        master.btn_load2.place(x=300, y=100, height=50)

        master.btn_load3 = ttk.Button(text='Отчет')
        master.btn_load3.place(x=50, y=200, height=50)

        master.btn_load4 = ttk.Button(text='Стоп', command=self.stop_thread)
        master.btn_load4.place(x=300, y=200, height=50)
        
        # Настройки

        self.settings_initial(450, 100)

    def terminate_thread(self):
        if not self.process.is_alive():
            return

        self.process.close()

    def settings_initial(self,x,y):
        self.label_setting_accounts = ttk.Label(text='Количество аккаунтов:')
        self.label_setting_accounts.place(x=x, y=y)

        self.entry_setting_accounts = ttk.Entry(width=10)
        self.entry_setting_accounts.place(x=x+140, y=y)

        self.label_setting_browser_hidden= ttk.Label(text='Показать браузер:')
        self.label_setting_browser_hidden.place(x=x, y=y+50)

        self.entry_setting_browser_hidden = ttk.Checkbutton(width=10)
        self.entry_setting_browser_hidden.place(x=x+140, y=y+50)

        self.label_setting_pages = ttk.Label(text='Мониторинг страниц товара (макс):')
        self.label_setting_pages.place(x=x, y=y+100)

        self.entry_setting_pages = ttk.Entry(width=10)
        self.entry_setting_pages.place(x=x+210, y=y+100)

        self.entry_setting_pages.insert(index=0,string='25')

    def threads_of_multiprocessing(self,number_of_accounts):
        while len(self.infos) != 0:
            while len(list(filter(lambda proces: proces.is_alive() == True,self.process))) != 0:
                if len(self.infos) == 0:
                    self.master.btn_load2.config(text='Старт')
                    self.master.btn_load2.config(state=tkinter.NORMAL)
                    return

            for i in range(0, number_of_accounts):
                    if len(self.infos) == 0:
                        self.master.btn_load2.config(text='Старт')
                        self.master.btn_load2.config(state=tkinter.NORMAL)                        
                        return
                    Thread(self.loading_body(list(self.infos[0]))).start()
                    self.infos.remove(self.infos[0])

            while len(list(filter(lambda proces: proces.is_alive(),self.process))) != 0:
                if len(self.infos) == 0:
                    self.master.btn_load2.config(text='Старт')
                    self.master.btn_load2.config(state=tkinter.NORMAL)                    
                    return
        self.master.btn_load2.config(text='Старт')
        self.master.btn_load2.config(state=tkinter.NORMAL)

    def start_loading(self):

        self.master.btn_load2['text'] = 'Работаю...'
        self.master.btn_load2['state'] = 'disabled'

        self.infos = EXCEL_PARSER().get_values()
        EXCEL_REPORT().create_book()
        threads = []
        if self.entry_setting_accounts.get() != '':
            for i in range(0, int(self.entry_setting_accounts.get())):
                threads.append(Thread(self.loading_body(list(self.infos[0]))))
                threads[i].start()
                self.infos.remove(self.infos[0])
                
            Thread(target=self.threads_of_multiprocessing,
                kwargs={
                    'number_of_accounts':int(self.entry_setting_accounts.get())}
                ).start()
        else:
            self.loading_body()

    def stop_thread(self):
        self.infos = []
        for proces in self.process:
            proces.terminate()

        print('stop_process')
        self.master.btn_load2.config(text='Старт')
        self.master.btn_load2.config(state=tkinter.NORMAL)

        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'anty.exe' in proc.info['name']:
                proc.terminate()
        
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'chromedriver-windows-x64.exe' in proc.info['name']:
                proc.terminate()


    def loading_body(self, info=''):
            if info:
                proces = Process(kwargs={'max_pages_entry': self.entry_setting_pages.get(), 'target_profile': info}, target=start_autobasket, daemon=True)
                self.process.append(proces)
                proces.start()
                print('async')
            else:
                proces = Process(kwargs={'max_pages_entry': self.entry_setting_pages.get()}, target=start_autobasket, daemon=True)
                self.process.append(proces)
                proces.start()


if __name__ == '__main__':
    root = tkinter.Tk()
    
    WB_PROMOTER(root).mainloop()