#author: Honna Gowri Manjuanth honna.manjunath@colorado.edu
#name:Web Proxy
#purpose:
#date
#version
from bs4 import BeautifulSoup
import requests
import socket
import sys
import threading
import os
import hashlib
import time

class proxy():
    def __init__(self,max_time):
        self.threads=[]
        self.i=1
        self.address=''
        self.port=0
        self.max_time = max_time
        try:
            if len(sys.argv)<2:
                self.port=int(sys.argv[1])
        except:
                print("The port number is missing.")
                sys.exit()
        try:
            if len(sys.argv)<=3:
                self.port=int(sys.argv[1])
                self.max_time=int(sys.argv[2])
        except:
                print("Either the port number or the Max time entry is missing.")
                self.max_time=120
        print(self.port)
        if (int(self.port)<1025 or int(self.port)>65535):
            print("Port number is not valid")
            sys.exit()
        self.soc()
        
    def soc(self): 
        
        '''
        Creating a socket.
        '''
            
        try:
            bros=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bros.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bros.bind((self.address,self.port))
            bros.listen(5)
            print("The Webproxy is listening on port: ",self.port)
            while(1):
                (self.connbro,self.addbro)=bros.accept()
                #print("The address of the browser is : ", self.addbro)
                if self.connbro:
                    thr_multiple=multiplethread(self.connbro,self.addbro,self.i,max_time) #Calling the thread class.
                    self.threads.append(thr_multiple)
                    thr_multiple.start()
                    self.i=self.i+1
                    print("Thread number running"+str(self.i))
                   
        except (KeyboardInterrupt or  socket.error):
            print("Either a keyboard interrupt was raised else the socket wasn't created")
            sys.exit()
            

class multiplethread(threading.Thread):
    def __init__(self,connbro,addbro,i,max_time):
        threading.Thread.__init__(self)
        self.connbro = connbro
        self.addbro = addbro
        self.i=i
        self.max_time = max_time
        
    def run(self):
        #try:
            #while(1):
                #bdata=''
                bdata=self.connbro.recv(65535)
                bdata=bdata.decode()
                print("Decoded info")
                print(bdata)
                print("Details:"+ str(self.connbro.getsockname()))
                if bdata:
                    data=bdata.split("\n")
                    methodline=data[0]
                    method=methodline.split()[0] #Fetching the method
                    print("The method is "+ str(method))
                    hostline=bdata.split("\r")
                    host=hostline[1]
                    host=host.split(' ')[1]          #Fetching the host name
                    print("Printing host name:"+ str(host))
                    '''
                     CONTENT FILTERING
                    '''
                    present=os.path.isfile("blocked.txt")

                    if(present==True):
                        file=open("blocked.txt",'r')
                        a=file.readlines()
                        #print(a)
                        check=list(map(lambda s:s.strip(),a))
                        print("modified"+str(check))
                        w=host
                        for i in check:
                            print(i)
                            if str(i) in w:
                                print("I "+str(i))
                                print("The link contains blacklisted word")
                                message=("HTTP/1.0"+" 403 Forbidden\n"+"Content-Type: text/html \r\n")
                                self.connbro.send(message.encode())
                                self.connbro.send("\r\n".encode())
                                self.connbro.send("<html><head><title>403 Forbidden</title></head><body>This URL is blocked.</h1></body></html>".encode())
                                self.connbro.close()
                            else:   
                                print("The URL is clean.") 
                    else:
                        print("The blacklisting file is not present")
                    
                    '''
                    Content filtering check done.
                    '''
                else:
                    print("No data from the browser")
                    return
                '''
                CHECK IF WE ARE GETTING GET METHOD AND EXECUTE.
                '''
                if (method=="GET"):
                        print("Method is GET hence the page must be fetched from the Web server.")
                        try:
                            ip=socket.gethostbyname(host)
                            print("IP is " + str(ip))
                        except:
                            message=("HTTP/1.0"+" 400 Bad Request\n"+"Content-Type: text/html \r\n")
                            self.connbro.send(message.encode())
                            self.connbro.send("\r\n".encode())
                            self.connbro.send("<html><head><title>400 Bad Request</title></head><body>Invalid URL.</h1></body></html>".encode())
                            self.connbro.close()
                        filename=methodline.split()[1]
                        '''
                        Check if the directory exists
                        '''
                        check=os.path.isdir(host)
                        print("results of check: ",check)
                        if(check==False):
                            os.mkdir(host)
                        else:  
                            pass
                        '''
                        Preparing the hashed file name
                        '''
                        #print("The hashing filename is :",filename)
                        filename_hash= hashlib.sha224(filename.encode()).hexdigest()
                        #print("The hashed string: ",filename_hash)
                        existcheck=os.path.isfile(host+"\\"+filename_hash)
                        '''
                        CACHEING
                        '''
                        if(existcheck==True):
                            print("Pulling data from cache.")
                            request_time=time.time()
                            handler=open(host+"\\"+filename_hash,'rb')
                            save_time=os.path.getmtime(host+"\\"+filename_hash)
                            difference_time=request_time-save_time
                            print(save_time)
                            print(request_time)
                            print(difference_time)
                            if (int(difference_time)<int(self.max_time)):
                                for i in handler:
                                    self.connbro.send(i)
                                self.connbro.close()
                            else:
                                webport=80
                                websrv= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                websrv.connect((ip,webport))
                                print("Connected to Web-server")
                                websrv.send(bdata.encode())
                                self.websrvdata=websrv.recv(65535)
                                #print("The hashing filename from server is :",filename_hash)
                                pre=os.path.join(host,filename_hash)
                                print("The joined path: "+str(pre))
                                with open(pre,'wb') as handler2:
                                    handler2.write(bytes(self.websrvdata))
                                    handler2.close()
                                try:
                                    self.connbro.send(self.websrvdata)
                                except:
                                    pass
                                self.connbro.close()
                                
                                '''
                                PREFETCHING
                                '''
                                try:
                                    webserver="http://"+host+"/"
                                    r=requests.get(webserver)
                                    soup=BeautifulSoup(r.text,'html.parser')
                                    data=[]
                                    list1=[]
                                    list2=[]
                                    list3=[]
                                    check=os.path.isdir(host)
                                    if check==False:
                                        os.mkdir(host)
                                    else:
                                        pass
                                    
                                    for link in soup.find_all('a'):
                                        l=link.get('href')
                                        data.append(l)
                                    
                                    for i in data:
                                        if not 'http://' in i:
                                            list1.append(i)
                                        else:
                                            list2.append(i)
                                            
                                    for elements in list1:
                                        elements=webserver+elements
                                        list3.append(elements)
                        
                                    endresult=list3+list2
                                    
                                    for link in endresult:
                                        r1=requests.get(link)
                                        #print("The hashing filename is :",i)
                                        filename_hash= hashlib.sha224(r1.content).hexdigest()
                                        #print("The hashed string: ",filename_hash)
                                        file=open(host+"\\"+filename_hash,'wb')
                                        file.write(r1.content)
                                        file.close()
                                except:
                                    pass
        
                        else:
                            webport=80
                            websrv= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            websrv.connect((ip,webport))
                            print("Connected to Web-server")
                            websrv.send(bdata.encode())
                            self.websrvdata=websrv.recv(65535)
                            #print("The hashing filename from server is :",filename_hash)
                            pre=os.path.join(host,filename_hash)
                            print("The joined path: "+str(pre))
                            with open(pre,'wb') as handler2:
                                handler2.write(bytes(self.websrvdata))
                                handler2.close()
                            try:
                                self.connbro.send(self.websrvdata)
                            except:
                                pass
                            self.connbro.close()
                            
                            '''
                            PREFETCHING
                            '''
                            try:
                                webserver="http://"+host+"/"
                                r=requests.get(webserver)
                                soup=BeautifulSoup(r.text,'html.parser')
                                data=[]
                                list1=[]
                                list2=[]
                                list3=[]
                                check=os.path.isdir(host)
                                if check==False:
                                    os.mkdir(host)
                                else:
                                    pass
                                
                                for link in soup.find_all('a'):
                                    l=link.get('href')
                                    data.append(l)
                                
                                for i in data:
                                    if not 'http://' in i:
                                        list1.append(i)
                                    else:
                                        list2.append(i)
                                        
                                for elements in list1:
                                    elements=webserver+elements
                                    list3.append(elements)
                    
                                endresult=list3+list2
                                
                                for link in endresult:
                                    r1=requests.get(link)
                                    #print("The hashing filename is :",i)
                                    filename_hash= hashlib.sha224(r1.content).hexdigest()
                                    #print("The hashed string: ",filename_hash)
                                    file=open(host+"\\"+filename_hash,'wb')
                                    file.write(r1.content)
                                    file.close()
                            except:
                                pass
                                                        
                elif (method in("HEAD","POST")):
                    message=('HTTP/1.0 501 Not Implemented\n'+'Content-Type: text/html \r\n')
                    self.connbro.send(message.encode())
                    self.connbro.send("\r\n".encode())
                    self.connbro.send("<html><head><title>501 Not Implemented</title></head><body><h1>Only GET method is handled.</h1></body></html>".encode())
                    self.connbro.close()
                    
                else:
                    message=("HTTP/1.0"+" 400 Bad Request\n"+"Content-Type: text/html \r\n")
                    self.connbro.send(message.encode())
                    self.connbro.send("\r\n".encode())
                    self.connbro.send("<html><head><title>400 Bad Request</title></head><body>Only GET method is handled along with a valid URL.</h1></body></html>".encode())
                    self.connbro.close()

if __name__=='__main__':
    max_time=0
    proxy=proxy(max_time)     
       
