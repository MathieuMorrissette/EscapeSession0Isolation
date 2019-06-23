# This will open an nt authority system on your computer
# python rip_system.py install
# python rip_system.py start

import base64
import os
import socket
import subprocess
import time

import psutil
import pyscreenshot
import servicemanager
import win32api
import win32con
import win32event
import win32file
import win32pipe
import win32process
import win32profile
import win32security
import win32service
import win32serviceutil
import win32ts


def get_pid(proc_name):
    for proc in psutil.process_iter():
        if proc.name() == proc_name:
            return proc.pid
    return 0

def getusertoken():
    print("Getting winlogon pid...")
    winlogon_pid = get_pid('winlogon.exe')
    print("PID:" + str(winlogon_pid))

    p = win32api.OpenProcess(1024, 0, get_pid('winlogon.exe'))
    t = win32security.OpenProcessToken(p, win32security.TOKEN_DUPLICATE)
    
    primaryToken = win32security.DuplicateTokenEx(t,
                                win32security.SecurityImpersonation,
                                win32security.TOKEN_ALL_ACCESS,
                                win32security.TokenPrimary)
    return primaryToken

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "SystemRIP"
    _svc_display_name_ = "SystemRIP"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(20)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        #my_app_path = 'C:\\Windows\\System32\\cmd.exe'
        my_app_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        startup = win32process.STARTUPINFO()
        priority = win32con.NORMAL_PRIORITY_CLASS
        console_user_token = getusertoken()
        environment = win32profile.CreateEnvironmentBlock(console_user_token, False)
        handle, thread_id ,pid, tid = win32process.CreateProcessAsUser(console_user_token, my_app_path, None, None, None, True, priority, environment, None, startup)


if __name__ == '__main__': 
        win32serviceutil.HandleCommandLine(AppServerSvc)
