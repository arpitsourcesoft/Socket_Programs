####### SERVER 2 ########
import socket
import cv2, numpy ,threading


ss = socket.socket(socket.AF_INET , socket.SOCK_STREAM)  #server socket for sending
cs = socket.socket(socket.AF_INET , socket.SOCK_STREAM)  #client socket for recieving


ss.bind(("localhost" , 3033))
ss.listen(5)


cs.connect(("localhost" , 2022))    # send request to server2 for connection


c_s ,addr = ss.accept()                      #accept connection request to server socket
print ("Connected to - " ,addr)        
cs.settimeout(1)  


# loading haarcascade model to detect face
model = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
flag = -1           
cap = cv2.VideoCapture(1)   # start capture video form external camera


def send():                  
    global flag , cap
    while(True):
        if ( flag == 0): 
            break
        try:
            ret,photo=cap.read()                              #read images
            b_img = cv2.imencode(".jpg" , photo)[1].tobytes() # first encode and then convert to bytes
            c_s.sendall(b_img)                                # send images
        except:
            continue
    cap.release()      #release camera after the function is done sending 
    ss.close()         # close the server (sending ) socket 
 


def receive():
    global flag , cap , model
    count=0
    while(True):
        if (count>10): break
        try:
            mess = cs.recv(100000)                        #recieve 1 lack bytes of data
            if (mess):
                nparr = numpy.frombuffer(mess, numpy.uint8)  # retreive the array form bytes
                img1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # create image from array
                if (not (img1 is None) ):     
                    try:
                        face =model.detectMultiScale(img1)  # detect face in img1
                        if (len(face)==0):
                            pass
                        else:
                            x1=face[0][0]
                            y1=face[0][1]
                            x2=face[0][2]
                            y2=face[0][3]
                        img1 = cv2.rectangle(img1,(x1,y1),(x1+x2,y1+y2),[255,255,255],3)                     
                
                    except:
                        pass
                    # adding the image image being sent in top left corner
                    ret,photo1=cap.read()
                    resized = cv2.resize(photo1, (150,150), interpolation = cv2.INTER_AREA)
                    img1[ 10:160 , 10:160  ] = resized
                    img1 = cv2.rectangle(img1, (0,0), (170,170), (0,0,250), 3)
                    
                    # showing the final images     
                    cv2.imshow("From server1.ipynb",img1)
                    if cv2.waitKey(10) == 13:       # if user press enter break the loop
                        break
        except:
            count+=1
            continue
            
    flag = 0
    cv2.destroyAllWindows()  # destroy the image window
    cs.close()               # close client (reciever) socket
    
# Putting the send and recieve functions in different thread so they can run in parallel
t1 = threading.Thread(target = receive)   
t2 = threading.Thread(target = send)
t1.start()       
t2.start()#