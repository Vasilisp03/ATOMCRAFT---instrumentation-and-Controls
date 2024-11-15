import socket
import threading

HOST = '192.168.0.28'  # Listen on all network interfaces
PORT = 2000       # Port to listen on

def temp_rec():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Server listening on port {PORT}...")
        counter = 0

        while True:
            msg, addr = s.recvfrom(1024)  # recvfrom for UDP
            print(f"Received Temperature from {addr}: {msg.decode()}")
            counter += 1
            print(counter)
            send = "ACK"
            s.sendto(send.encode(), ("192.168.0.29", 2390))

P_PORT = 2020       # Port to listen on

def pressure_rec():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, P_PORT))
        print(f"Server listening on port {P_PORT}...")
        counter = 0
        
        while True:
            msg, addr = s.recvfrom(1024)  # recvfrom for UDP
            print(f"Received Pressure from {addr}: {msg.decode()}")
            counter += 1
            print(counter)
            send = "ACK"
            s.sendto(send.encode(), ("192.168.0.29", 2390))

if __name__ == "__main__":
    # set up all threads that we want to exist
    temperature_data_thread = threading.Thread(target = temp_rec)
    pressure_data_thread = threading.Thread(target = pressure_rec)

    # start threads running
    temperature_data_thread.start()
    pressure_data_thread.start()
    
