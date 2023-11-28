import tkinter
from tkinter import *
from tkinter import ttk
from multiprocessing import Pool, Process
from typing import Any
import psutil
from threading import Thread
from excel_handlers import *
from tkinter import filedialog
import tkinter.messagebox as mb
import sys
import os
import shutil

from manage import MANAGE_SCRIPT
from browser_handlers import WB_BROWSER


def start_autobasket(max_pages_entry='', target_profile='', headless=False):
    
    if max_pages_entry: max_pages_entry = int(max_pages_entry)
    manage_script = MANAGE_SCRIPT(max_pages=int(max_pages_entry), target_profile=target_profile, headless=headless)
    manage_script.start()

class CheckbuttonVar(ttk.Checkbutton):
    def __init__(self, *args, **kwargs):
        self._var = tkinter.BooleanVar()
        self.is_checked = False
        super().__init__(*args, variable=self._var, **kwargs)

    def invoke(self) -> Any:
        self.is_checked = not self.is_checked
        return super().invoke()

    @property
    def is_checked(self):
        return self._var.get()

    @is_checked.setter
    def is_checked(self, value):
        self._var.set(value)

class HackThread(Thread):
    def __init__(self, *args, **keywords):
        Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run 
        Thread.start(self)
    
    def __run(self):
        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
            return self.localtrace

    def kill(self):
        self.killed = True

class WB_PROMOTER(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.process = []
        self.threads = []

        self.max_pages = 25
        self.master = master

        master.title('WB PROMOTER')
        master.geometry('800x300')
        master.resizable(False, False)
        master.iconbitmap(default='logo.ico')
        master.resizable(False, False)

        master.window_title = ttk.Label(font=18,text='WB PROMOTER')
        master.window_title.pack(pady=20)

        master.btn_load1 = ttk.Button(text='Загрузить ТЗ Excel', command=self.load_tz)
        master.btn_load1.place(x=50, y=100, height=50)

        master.excel_template_link = Button(text='Шаблон для ТЗ', bg=self.cget('background'),fg='blue',borderwidth=0, command=self.open_this_directory)
        master.excel_template_link.place(x=50, y=158)

        """  
            Чтобы открыть папку:
            def foo():
                os.system("start explorer ./")
        """

        master.btn_load2 = ttk.Button(text='Старт', command=self.start_loading,)
        master.btn_load2.place(x=300, y=100, height=50)

        master.btn_load3 = ttk.Button(text='Отчет', command=self.open_this_directory)
        master.btn_load3.place(x=50, y=200, height=50)

        master.btn_load4 = ttk.Button(text='Стоп', command=self.stop_thread)
        master.btn_load4.place(x=300, y=200, height=50)
        
        # Настройки

        self.settings_initial(450, 100)

    def open_this_directory(self):
        os.system(f"start explorer {os.getcwd()}")

    
    def terminate_thread(self):
        if not self.process.is_alive(): 
            return

        self.process.close()

    def load_tz(self):
        filepath = filedialog.askopenfilename()
        if filepath == '':
            mb.showerror('Ошибка', 'Вы не выбрали файл!')
        try:
            shutil.copy2(filepath, 'info.xlsx')
        except:
            os.remove('info.xlsx')
            shutil.copy2(filepath, 'info.xlsx') 

    def settings_initial(self,x,y):
        self.label_setting_accounts = ttk.Label(text='Количество аккаунтов:')
        self.label_setting_accounts.place(x=x, y=y)

        self.entry_setting_accounts = ttk.Entry(width=10)
        self.entry_setting_accounts.place(x=x+140, y=y)

        self.label_setting_browser_hidden= ttk.Label(text='Показать браузер:')
        self.label_setting_browser_hidden.place(x=x, y=y+50)

        self.entry_setting_browser_hidden = CheckbuttonVar(width=10)
        self.entry_setting_browser_hidden.place(x=x+140, y=y+50)

        self.label_setting_pages = ttk.Label(text='Мониторинг страниц товара (макс):')
        self.label_setting_pages.place(x=x, y=y+100)

        self.entry_setting_pages = ttk.Entry(width=10)
        self.entry_setting_pages.place(x=x+210, y=y+100)

        self.entry_setting_pages.insert(index=0,string='25')

    def threads_of_multiprocessing(self,number_of_accounts):
            WB_BROWSER().auhorization_dolphin_anty()
            while len(self.infos) != 0:
                i = 0
                if len(self.infos) - number_of_accounts < 0:
                    number_of_accounts = len(self.infos)
                while i < number_of_accounts:
                        if len(self.infos) == 0:
                            self.master.btn_load2.config(text='Старт')
                            self.master.btn_load2.config(state=tkinter.NORMAL)                        
                            return
                        
                        thread = HackThread(self.loading_body(list(self.infos[0])))
                        thread.start()
                        print('\n__START_THREAD__\n')
                        self.threads.append(thread)
                        self.infos.remove(self.infos[0])
                        i += 1
                
                for thread in self.threads:
                    thread.join()
                print('\n__FINISH__\n')
                if len(self.infos) == 0:
                    self.master.btn_load2.config(text='Старт')
                    self.master.btn_load2.config(state=tkinter.NORMAL)                    
                    return
                

    def start_loading(self):

        self.master.btn_load2['text'] = 'Работаю...'
        self.master.btn_load2['state'] = 'disabled'

        self.infos = EXCEL_PARSER().get_values()
        EXCEL_REPORT().create_book()
        threads = []
        if self.entry_setting_accounts.get() != '':
            # i = 0
            # while i < int(self.entry_setting_accounts.get()):
            #     threads.append(Thread(self.loading_body(list(self.infos[0]))))
            #     threads[i].start()
            #     self.infos.remove(self.infos[0])
            
            # while len(self.infos):
                # if len(list(filter(lambda thread: thread.is_live(),self.threads))) == 0:
                # hack_thread = ''
                # while (hack_thread == '' or not hack_thread.is_alive()) and len(self.infos) != 0:
                #     if hack_thread != '': print( hack_thread.is_alive())
                    hack_thread = HackThread(target=self.threads_of_multiprocessing,
                        kwargs={
                            'number_of_accounts':int(self.entry_setting_accounts.get())}
                        )
                    hack_thread.start()
                
                
        else:
            self.loading_body()

    def stop_thread(self):
        self.infos = []

        for thread in self.threads:
            thread.kill()

        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'anty.exe' in proc.info['name']:
                proc.terminate()
        
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'chromedriver-windows-x64.exe' in proc.info['name']:
                proc.terminate()

        print('stop_process')
        self.master.btn_load2.config(text='Старт')
        self.master.btn_load2.config(state=tkinter.NORMAL)

    def loading_body(self, info=''):
            headless = self.entry_setting_browser_hidden.is_checked
            if info:
                thread = HackThread(name='loading_body',kwargs={'max_pages_entry': self.entry_setting_pages.get(), 'target_profile': info, 'headless':headless}, target=start_autobasket)
                self.threads.append(thread)
                thread.start()
            else:
                thread = HackThread(name='loading_body',kwargs={'max_pages_entry': self.entry_setting_pages.get(), 'headless':headless}, target=start_autobasket)
                self.process.append(thread)
                thread.start()


if __name__ == '__main__':
    root = tkinter.Tk()
    
    WB_PROMOTER(root).mainloop()