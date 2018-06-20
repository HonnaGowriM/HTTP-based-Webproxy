
                                                                          WEBPROXY

  Overview
  ---------

 A webproxy is going to act as an intermediate device between the browser and the webserver. It cache information and acts as a load balancer to the web-server.

  Python Version
  ---------------

  The python version used for the assignment is Python 3.6


  Method of Execution
  --------------------

  1. Run the webproxy.py first, by entering the port number between 1024-65535 and a number to set max-time.

  2. Open the web-browser Firefox and make sure you set the proxy port same as the one given in the program.  

  3. Use Ctl+Shift+Q to open the Developer tool to see the requests that are being generated.

  Web Proxy
  ------------
  1. Libraries used are BeautifulSoup and requests for Pre-fetching. Socket, Sys , Threading, os, hashlib, time for the rest of the implementation.
 
  2.There are two classes. One class if to create the socket and the other class is for threading.

  3.In the init function of the proxy class where in the socket is created, the port number is validated and the max-time is set.
  
  4.Once the proxy is binded on the address and port number if a connection is established a thread is invoked.

  5.In the run function of the thread, we do content filtering at the initial state to see if any blacklisted url is being accessed. If it is being access a 403 error is sent across.

  6.Next the program checks for method GET, if any other method other than GET is request appropriate error is sent across.Such as 501 not implemented if POST or HEAD is requested. 
    Anything apart from these two a 400 Bad request is sent across.

  7.Once the program verifies a GET request is being requested the program checks if a directory with the host name is present, if yes then that states the data has been cached and hence the 
    data is sent across from the cache.

  8.If not, the proxy makes a connection with the web-server with another socket and then retrives the required information.

  9. While retriving the information the request is cached for futher use and then the information is passed on to the browser. 

  10. Additionally, the potentional links to while the user might visit is prefetched and kept. 
  
  11. A file blocked.txt contains terms that is used to block a page from loading.
