import socket

UDP_IP = "192.168.0.29"  # Replace with your Arduino's IP address
UDP_PORT = 2390

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)  # Set timeout for response

def send_command(command):
    sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
    try:
        data, addr = sock.recvfrom(1024)
        print(f"Received response: {data.decode()}")
    except socket.timeout:
        print("No response from Arduino")

while True:
    cmd = input("Enter 'o' to open solenoid or 'q' to quit: ").strip()
    if cmd == "q":
        break
    send_command(cmd)