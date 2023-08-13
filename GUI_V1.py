import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import threading
import pickle

class Slave:
    def __init__(self, name, ip, port, category):
        self.name = name
        self.ip = ip
        self.port = port
        self.category = category
        self.connection_status = False

class MasterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Master GUI")
        self.slaves = []
        self.create_widgets()

    def create_widgets(self):
        # Labels and Entry fields for Slave info
        tk.Label(self.master, text="Slave Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.master, text="IP Address:").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.master, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.master, text="Category:").grid(row=0, column=3, padx=5, pady=5)

        self.name_entry = tk.Entry(self.master)
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)

        self.ip_entry = tk.Entry(self.master)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5)

        self.port_entry = tk.Entry(self.master)
        self.port_entry.grid(row=1, column=2, padx=5, pady=5)

        self.category_entry = tk.Entry(self.master)
        self.category_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons for adding slaves, checking connection, and running scripts
        tk.Button(self.master, text="Add Slave", command=self.add_slave).grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        tk.Button(self.master, text="Check Connection", command=self.check_connection).grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        tk.Button(self.master, text="Import and Run Script", command=self.import_and_run_script).grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        # Listbox to display slaves
        self.listbox = tk.Listbox(self.master, width=40)
        self.listbox.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self.on_slave_select)

        # Set the Listbox to expand with window resizing
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Start a thread to listen for commands from slaves
        self.listener_thread = threading.Thread(target=self.listen_to_slaves)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def add_slave(self):
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        category = self.category_entry.get()
        new_slave = Slave(name, ip, port, category)
        self.slaves.append(new_slave)
        self.listbox.insert(tk.END, self.format_slave_info(new_slave))
        self.name_entry.delete(0, tk.END)
        self.ip_entry.delete(0, tk.END)
        self.port_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def format_slave_info(self, slave):
        return f"Name: {slave.name} | IP: {slave.ip} | Port: {slave.port} | Category: {slave.category}"

    def check_connection(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_slave = self.slaves[selected_index[0]]
            try:
                # Check connection to the slave using a simple ping
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)  # Timeout for connection attempt (2 seconds)
                s.connect((selected_slave.ip, selected_slave.port))
                s.close()
                selected_slave.connection_status = True
                self.listbox.itemconfig(selected_index, {'fg': 'green'})
                messagebox.showinfo("Connection Status", f"{selected_slave.name} is connected!")
            except Exception as e:
                selected_slave.connection_status = False
                self.listbox.itemconfig(selected_index, {'fg': 'red'})
                messagebox.showwarning("Connection Status", f"Failed to connect to {selected_slave.name}.\nError: {e}")

    def on_slave_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_slave = self.slaves[selected_index[0]]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, selected_slave.name)
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, selected_slave.ip)
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, selected_slave.port)
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, selected_slave.category)

    def import_and_run_script(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_slave = self.slaves[selected_index[0]]
            file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if file_path:
                with open(file_path, 'r') as file:
                    script_code = file.read()
                    try:
                        # Send the script code to the selected slave
                        self.send_script_to_slave(selected_slave, script_code)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to send script to {selected_slave.name}.\nError: {e}")

    def send_script_to_slave(self, slave, script_code):
        try:
            # Create a socket to send the script code to the slave
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((slave.ip, slave.port))
            s.sendall(pickle.dumps(script_code))
            s.close()
            messagebox.showinfo("Success", f"Script sent to {slave.name} successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to send script to {slave.name}. Error: {e}")

    def listen_to_slaves(self):
        try:
            # Create a socket to listen for commands from slaves
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', 12345))
            s.listen(5)

            while True:
                conn, addr = s.accept()
                data = conn.recv(4096)
                if data:
                    command = pickle.loads(data)
                    # Process the received command from the slave
                    # Add your command processing logic here
                    print(f"Received command from {addr}: {command}")
                conn.close()
        except Exception as e:
            print(f"Error occurred while listening to slaves: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.mainloop()
