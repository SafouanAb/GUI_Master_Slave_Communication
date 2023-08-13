import socket
import pickle

def execute_script(script_code):
    try:
        # Execute the received script forcefully using 'exec'
        exec(script_code, globals(), locals())
    except Exception as e:
        print(f"Failed to execute the script. Error: {e}")

def listen_to_master():
    try:
        # Create a socket to listen for commands from the master
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 50000))  # Bind to any available network interface on port 50000
        s.listen(5)

        print("Waiting for commands from the master...")

        while True:
            conn, addr = s.accept()
            data = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            if data:
                script_code = pickle.loads(data)
                # Execute the received script
                execute_script(script_code)
            conn.close()
    except Exception as e:
        print(f"Error occurred while listening to the master: {e}")

if __name__ == "__main__":
    listen_to_master()