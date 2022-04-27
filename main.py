import json
import socket
import ssl
import numpy as np
import traceback

# Connection Details
SERVER_HOST = '192.168.1.150'
#SERVER_HOST = '127.0.0.1'
SERVER_PORT = 6160
server_cert = "certificates/ca_cert.pem"
client_cert = "certificates/NetworkPlugin.pem"
client_key = "certificates/NetworkPlugin_key.pem"
plugin_data = "certificates/NetworkPlugin.zip"

def create_client():
    """
    :return:
    """
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketConnection = ssl.wrap_socket(socketConnection, keyfile=client_key, certfile=client_cert)    
    socketConnection.connect((SERVER_HOST, SERVER_PORT))


    # Read zip file from the folder and send the data
    data = np.fromfile(plugin_data, dtype=np.byte)
    data = np.array(data)
    length = len(data)
    #print(length)
    header = length.to_bytes(4, 'little')
    header = bytearray(header)
    msg = bytearray(data)
    # print(data)
    msg = header + msg
    socketConnection.send(msg)

    #connected SSL Socket
    return socketConnection

def close_SSLsocket(socketConnection):
    """
    :return:
    """
    socketConnection.close()

def send_msg(socketConnection, msg):

    print("\nsocket sending: " + str(msg)+"\n")
    msg = json.dumps(msg)
    msg = msg.encode()
    length = len(msg)
    header = length.to_bytes(4, 'little')
    msg = bytearray(msg)
    msg = header + msg
    #print(msg)
    socketConnection.send(msg)


def readSock(socketConnection):
    while True:
        try:
            data = socketConnection.recv(8)
            #  4 bytes msg header + 4 bytes length integer
            msg_type = data[0]
            length = int.from_bytes(data[4:8], "little")

            if msg_type == 1:
                data = socketConnection.recv(length)                    
                jsonMessage = json.loads(data.decode('utf-8'))
                print("json response: " + str(jsonMessage)+"\n")
                
        except Exception as e:
            print("error in reading the socket\n")
            print(e.__str__())
            traceback.print_exc()
            break


if __name__=="__main__":

    #create connection
    socket_connection = create_client()
    
    #message format for subscription to gain
    message = {"MessageId": 0,"NetworkSyncId": -1 ,"CommandId": "Subscribe","CommandPayload": {"StateId": "Scanner.Grayscale.Gain","SyncId": 0}}

    #send
    send_msg(socket_connection, message)

    #start recieiving from client
    while(True):
        readSock(socket_connection)

    


