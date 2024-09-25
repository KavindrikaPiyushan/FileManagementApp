import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
from datetime import datetime
import subprocess
import platform
from cryptography.fernet import Fernet
import json
import smtplib
import random
from email.mime.text import MIMEText
from tkinter import simpledialog







CONFIG_FILE = 'editor_config.json'
CREDENTIALS_FILE = 'credentials.json'

class CreateAccountDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.iconbitmap("D:\sf using python\pettrolium File Management System\FileManagementApp\icon.ico")

        self.username = None
        self.password = None
        self.email = None

        self.title("Create Account")
        self.geometry("300x250")

        tk.Label(self, text="Username:").pack(padx=20, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(padx=20, pady=5)

        tk.Label(self, text="Password:").pack(padx=20, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(padx=20, pady=5)

        tk.Label(self, text="Gmail:").pack(padx=20, pady=5)
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(padx=20, pady=5)

        tk.Button(self, text="Create Account", command=self.on_create).pack(padx=20, pady=20)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.center_window(parent)
        self.wait_window(self)

    def center_window(self, parent):
        window_width = 300
        window_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
     
    def validate_email(self, email):
        import re
        pattern = r'^[\w\.-]+@gmail\.com$'
        return re.match(pattern, email) is not None

    def on_create(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.email = self.email_entry.get()

        if not self.username or not self.password or not self.email:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not self.validate_email(self.email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        # If all validations pass, close the dialog
        self.destroy()

    def on_cancel(self):
        self.username = None
        self.password = None
        self.email = None
        self.destroy()



class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Login")
        self.iconbitmap("D:\sf using python\pettrolium File Management System\FileManagementApp\icon.ico")
        tk.Label(master, text="Username:").grid(row=0)
        tk.Label(master, text="Password:").grid(row=1)

        self.username_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        self.forgot_button = tk.Button(master, text="Forgot Password?", command=self.on_forgot_password)
        self.forgot_button.grid(row=2, columnspan=2, pady=5)

        return self.username_entry

    def apply(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
    def show(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
        self.deiconify()
        self.wait_window(self)

    def on_forgot_password(self):
        username = self.username_entry.get()
        if username in self.parent.credentials:
            email = self.parent.credentials[username]["email"]
            ResetPasswordDialog(self, email,username,self.parent.credentials)
        else:
            messagebox.showerror("Error", "Username not found.")    

class ResetPasswordDialog(tk.Toplevel):
    def __init__(self, parent, email,username,credentials):
        super().__init__(parent)
        self.iconbitmap("D:\sf using python\pettrolium File Management System\FileManagementApp\icon.ico")
        self.transient(parent)
        self.grab_set()
        self.email = email
        self.username=username
        self.credentials = credentials
        self.code = str(random.randint(100000, 999999))
        self.sent = self.send_verification_code()
        
        self.title("Reset Password")
        self.geometry("300x250")

        tk.Label(self, text="Verification Code:").pack(padx=20, pady=5)
        self.code_entry = tk.Entry(self)
        self.code_entry.pack(padx=20, pady=5)

        tk.Label(self, text="New Password:").pack(padx=20, pady=5)
        self.new_password_entry = tk.Entry(self, show="*")
        self.new_password_entry.pack(padx=20, pady=5)

        tk.Button(self, text="Reset Password", command=self.on_reset).pack(padx=20, pady=20)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.center_window(parent)
        self.wait_window(self)

    def center_window(self, parent):
        window_width = 300
        window_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    def send_verification_code(self):
        sender_email = "kavintest2000@gmail.com"
        app_password = "cksq qooc kzua viyk"  # Replace with your app password

        msg = MIMEText(f"Your verification code is: {self.code}")
        msg['Subject'] = 'Password Reset Verification Code'
        msg['From'] = sender_email
        msg['To'] = self.email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, self.email, msg.as_string())
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send verification code: {e}")
            return False
        
    def save_credentials(self,credentials):
        self.credentials = credentials
        try:
        # Load the key
            with open("secret.key", "rb") as key_file:
                 key = key_file.read()
            cipher = Fernet(key)
        
        # Encrypt and save the credentials
            credentials_bytes = json.dumps(self.credentials).encode("utf-8")
            encrypted_credentials = cipher.encrypt(credentials_bytes)
            with open("credentials.enc", "wb") as enc_file:
                enc_file.write(encrypted_credentials)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}")

    def on_reset(self):
        if not self.sent:
            return

        entered_code = self.code_entry.get()
        new_password = self.new_password_entry.get()

        if entered_code != self.code:
            messagebox.showerror("Error", "Incorrect verification code.")
            return

        if not new_password:
            messagebox.showerror("Error", "New password cannot be empty.")
            return
        
        self.credentials[self.username]["password"] = new_password
        
        
        # FileManagementApp.credentials[self.username]["password"] = new_password
        self.save_credentials(self.credentials)
        messagebox.showinfo("Success", "Password reset successfully.")
        self.destroy()

    def on_cancel(self):
        self.destroy()

class FileManagementApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.iconbitmap("D:\sf using python\pettrolium File Management System\FileManagementApp\icon.ico")
        self.title("File Management System")
        self.geometry("800x600")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1000
        window_height = 800
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
       
        self.credentials_file = "credentials.enc"
        self.is_credentials_empty = None  # This will hold the boolean value
        self.load_and_check_credentials()

        
        self.credentials = self.load_credentials()
        self.logged_in = False 
        self.login()

        if not self.logged_in:
            self.destroy()
            return

        

        self.create_widgets()
        self.file_paths = {}  # Dictionary to store full file paths
        self.folder_history = []  # List to keep track of folder navigation history
        self.root_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pettrolium Files")
        os.makedirs(self.root_folder, exist_ok=True)  # Create the folder if it doesn't exist
        self.current_folder = self.root_folder  # Set the initial folder to the root folder

        # Display initial folder contents
        self.display_parent_folder_contents(self.root_folder)
        self.display_folder_contents(self.root_folder)

    


    def create_widgets(self):
        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.bind("<Button-1>", self.deselect_all_items)  # Bind left mouse click to deselect items

        # Create left frame for parent tree
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create right frame for main tree and back button
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Duplicate", command=self.duplicate_file)
        edit_menu.add_command(label="Delete", command=self.delete_file)
        edit_menu.add_command(label="Add File", command=self.add_file)
        # edit_menu.add_command(label="Remove File", command=self.remove_file)
        edit_menu.add_command(label="Edit File", command=self.edit_file)
        edit_menu.add_command(label="Create Folder", command=self.create_folder)
        # edit_menu.add_command(label="Create Subfolder", command=self.create_subfolder)
        edit_menu.add_command(label="Set Custom Editor", command=self.set_custom_editor)

        # Add a label to show current folder path
        self.path_var = tk.StringVar()
        self.path_label = tk.Label(self, textvariable=self.path_var, anchor="w")
        self.path_label.pack(fill=tk.X, padx=5, pady=5)

        # Add a label to show selected item path
        self.selected_path_var = tk.StringVar()
        self.selected_path_label = tk.Label(self, textvariable=self.selected_path_var, anchor="w", fg="blue")
        self.selected_path_label.pack(fill=tk.X, padx=5, pady=5)

        # Create the parent folder treeview
        self.parent_tree = ttk.Treeview(self.left_frame, columns=("name", "type"), show="headings")
        self.parent_tree.heading("name", text="Most Parent Files/Folders")
        self.parent_tree.heading("type", text="Type")
        self.parent_tree.column("name", width=200)
        self.parent_tree.column("type", width=100)
        self.parent_tree.pack(side=tk.LEFT, fill=tk.Y)
        self.parent_tree.bind("<Double-1>", self.on_parent_double_click)
        self.parent_tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # Create frame for back button, sort button and treeview
        self.back_frame = ttk.Frame(self.right_frame)
        self.back_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.back_button = tk.Button(self.back_frame, text="Go Back", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.sort_button = tk.Button(self.back_frame, text="Sort", command=self.sort_files)
        self.sort_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.sort_options = ttk.Combobox(self.back_frame, values=["Alphabetically", "Newest", "Oldest", "Modified", "Ascending", "Descending"])
        self.sort_options.current(0)  # Set the default value
        self.sort_options.pack(side=tk.LEFT, padx=5, pady=5)

        self.tree = ttk.Treeview(self.right_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree["columns"] = ("name", "size", "type")
        self.tree.heading("name", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("type", text="Type")

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("name", anchor=tk.W, width=300)
        self.tree.column("size", anchor=tk.W, width=100)
        self.tree.column("type", anchor=tk.W, width=100)

        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # Create a frame for search
        self.search_frame = ttk.Frame(self)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Add a label for search
        search_label = ttk.Label(self.search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        # Move the search entry to the new frame
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<KeyRelease>", self.search_current_folder)

        # Add a "Search Everywhere" button
        self.search_button = ttk.Button(self.search_frame, text="Search Everywhere", command=self.search_everywhere)
        self.search_button.pack(side=tk.LEFT)

        # Add button to view properties
        self.properties_button = tk.Button(self.back_frame, text="View Properties", command=self.view_properties)
        self.properties_button.pack(side=tk.RIGHT, padx=5, pady=5)
     
    def load_and_check_credentials(self):
        """Check if the credentials file is empty and update the boolean value."""
        self.is_credentials_empty = self.is_file_empty(self.credentials_file)
        if not self.is_credentials_empty:
            self.load_credentials()

    def is_file_empty(self, file_path):
        """Check if the file is empty."""
        return not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    def display_parent_folder_contents(self, folder_path):
    # Check if folder_path is the root directory
        if folder_path == self.root_folder:
        # Clear existing items in parent treeview
            for item in self.parent_tree.get_children():
                self.parent_tree.delete(item)

        # Populate parent folder treeview with only immediate subfolders and subfiles
            try:
                 for item_name in os.listdir(folder_path):
                     item_path = os.path.join(folder_path, item_name)
                     if os.path.isdir(item_path) or os.path.isfile(item_path):
                         self.parent_tree.insert("", "end", iid=item_path, values=(item_name, "Folder" if os.path.isdir(item_path) else "File"))
            except PermissionError:
                messagebox.showerror("Error", f"Permission denied to access folder: {folder_path}")
    def create_account(self):
        create_account_dialog = CreateAccountDialog(self)
        if create_account_dialog.username and create_account_dialog.password and create_account_dialog.email:
            # Check if the username already exists
            if create_account_dialog.username in self.credentials:
                messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            else:
                # Add the new account to the credentials
                self.credentials[create_account_dialog.username] = {
                    "password": create_account_dialog.password,
                    "email": create_account_dialog.email
                }
                self.save_credentials()
                messagebox.showinfo("Success", "Account created successfully. You can now log in.\n\nPlease relaunch the application.")


    def save_credentials(self):
        try:
        # Load the key
            with open("secret.key", "rb") as key_file:
                 key = key_file.read()
            cipher = Fernet(key)
        
        # Encrypt and save the credentials
            credentials_bytes = json.dumps(self.credentials).encode("utf-8")
            encrypted_credentials = cipher.encrypt(credentials_bytes)
            with open("credentials.enc", "wb") as enc_file:
                enc_file.write(encrypted_credentials)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}")

    def display_folder_contents(self, folder_path):
        self.current_folder = folder_path
        self.path_var.set(f"Current folder: {self.current_folder}")

        # Clear existing items in the main treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate the main treeview with the contents of the current folder
        try:
            for item_name in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item_name)
                if os.path.isdir(item_path):
                    self.tree.insert("", "end", iid=item_path, text=item_name, values=(item_name, "", "Folder"))
                else:
                    file_size = os.path.getsize(item_path)
                    file_type = os.path.splitext(item_name)[1]
                    self.tree.insert("", "end", iid=item_path, text=item_name, 
                                     values=(item_name, f"{file_size} bytes", file_type))
                    self.file_paths[item_name] = item_path
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied to access folder: {folder_path}")

    def sort_files(self):
        sort_option = self.sort_options.get()
        items = [(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], item, self.tree.item(item, "values")[2]) for item in self.tree.get_children()]

        if sort_option == "Alphabetically":
            items.sort(key=lambda x: x[0].lower())
        elif sort_option == "Newest":
            items.sort(key=lambda x: os.path.getctime(self.file_paths.get(x[0], x[2])), reverse=True)
        elif sort_option == "Oldest":
            items.sort(key=lambda x: os.path.getctime(self.file_paths.get(x[0], x[2])))
        elif sort_option == "Modified":
            items.sort(key=lambda x: os.path.getmtime(self.file_paths.get(x[0], x[2])), reverse=True)
        elif sort_option == "Ascending":
            items.sort(key=lambda x: x[0].lower())
        elif sort_option == "Descending":
            items.sort(key=lambda x: x[0].lower(), reverse=True)

        for index, (name, size, iid, type_) in enumerate(items):
            self.tree.move(iid, '', index)

    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            if os.path.isdir(selected_path):
                self.folder_history.append(self.current_folder)  # Add current folder to history
                self.display_folder_contents(selected_path)
            elif os.path.isfile(selected_path):
                self.open_file()

    def on_parent_double_click(self, event):
        selected_item = self.parent_tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            if os.path.isdir(selected_path):
                self.folder_history.append(self.current_folder)  # Add current folder to history
                self.display_folder_contents(selected_path)

    def go_back(self):
        if self.folder_history:
           previous_folder = self.folder_history.pop()  # Get the last folder from history
        #    self.display_parent_folder_contents(previous_folder)  # Update parent tree
           self.display_folder_contents(previous_folder)  # Update main tree with previous folder contents
           self.current_folder = previous_folder  # Update current folder to the previous folder
        else:
        # If no history is available, go back to the root folder
        #    self.display_parent_folder_contents(self.root_folder)
           self.display_folder_contents(self.root_folder)
           self.current_folder = self.root_folder


    def open_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            if os.path.isfile(selected_path):
                try:
                    if platform.system() == "Windows":
                        os.startfile(selected_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", selected_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", selected_path])
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")

    def delete_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            try:
                if os.path.isfile(selected_path):
                    os.remove(selected_path)
                elif os.path.isdir(selected_path):
                    shutil.rmtree(selected_path)
                self.display_parent_folder_contents(self.current_folder)
                self.display_folder_contents(self.current_folder)
                 
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

    def duplicate_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            try:
                if os.path.isfile(selected_path):
                    base, extension = os.path.splitext(selected_path)
                    new_path = base + "_copy" + extension
                    shutil.copyfile(selected_path, new_path)
                elif os.path.isdir(selected_path):
                    new_path = selected_path + "_copy"
                    shutil.copytree(selected_path, new_path)
                self.display_parent_folder_contents(self.current_folder)
                self.display_folder_contents(self.current_folder)
                   
            except Exception as e:
                messagebox.showerror("Error", f"Failed to duplicate: {e}")

    def add_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                shutil.copy(file_path, self.current_folder)
                self.display_folder_contents(self.current_folder)
                self.display_parent_folder_contents(self.current_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add file: {e}")

    # def remove_file(self):
    #     selected_item = self.tree.selection()
    #     if selected_item:
    #         selected_path = selected_item[0]
    #         if os.path.isfile(selected_path):
    #             os.remove(selected_path)
    #             self.display_folder_contents(self.current_folder)
    #         else:
    #             messagebox.showerror("Error", "Selected item is not a file.")

    def edit_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            if os.path.isfile(selected_path):
                try:
                    editor = self.get_custom_editor()
                    if editor:
                        subprocess.run([editor, selected_path])
                    else:
                        messagebox.showerror("Error", "No custom editor set.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to edit file: {e}")

    def create_folder(self):
        folder_name = simpledialog.askstring("Input", "Enter folder name:")
        if folder_name:
            new_folder_path = os.path.join(self.current_folder, folder_name)
            try:
                os.makedirs(new_folder_path)
                self.display_folder_contents(self.current_folder)
                self.display_parent_folder_contents(self.current_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

    # def create_subfolder(self):
    #     selected_item = self.tree.selection()
    #     if selected_item:
    #         parent_folder_path = selected_item[0]
    #         if os.path.isdir(parent_folder_path):
    #             subfolder_name = simpledialog.askstring("Input", "Enter subfolder name:")
    #             if subfolder_name:
    #                 new_subfolder_path = os.path.join(parent_folder_path, subfolder_name)
    #                 try:
    #                     os.makedirs(new_subfolder_path)
    #                     self.display_folder_contents(self.current_folder)
    #                 except Exception as e:
    #                     messagebox.showerror("Error", f"Failed to create subfolder: {e}")

    def set_custom_editor(self):
        editor_path = filedialog.askopenfilename(title="Select Custom Editor")
        if editor_path:
            config = {"editor_path": editor_path}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            messagebox.showinfo("Info", "Custom editor set successfully.")

    def get_custom_editor(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("editor_path")
        return None

    def on_item_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            self.selected_path_var.set(f"Selected item: {selected_path}")

    def search_current_folder(self, event=None):
        query = self.search_var.get().lower()
        self.tree.selection_remove(self.tree.selection())  # Deselect all items
        for item in self.tree.get_children():
            item_text = self.tree.item(item, "values")[0].lower()
            if query in item_text:
                self.tree.selection_add(item)  # Select item if query matches
                self.tree.see(item)  # Scroll to the item

    def search_everywhere(self):
        query = self.search_var.get().lower()
        matching_items = []
        for root, dirs, files in os.walk(self.root_folder):
            for name in files + dirs:
                if query in name.lower():
                    matching_items.append(os.path.join(root, name))

        if matching_items:
            self.display_search_results(matching_items)
        else:
            messagebox.showinfo("Info", "No matching items found.")

    def display_search_results(self, results):
        self.current_folder = "Search Results"
        self.path_var.set("Search Results")
        
        # Clear existing items in the main treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item_path in results:
            item_name = os.path.basename(item_path)
            if os.path.isdir(item_path):
                self.tree.insert("", "end", iid=item_path, text=item_name, values=(item_name, "", "Folder"))
            else:
                file_size = os.path.getsize(item_path)
                file_type = os.path.splitext(item_name)[1]
                self.tree.insert("", "end", iid=item_path, text=item_name, 
                                 values=(item_name, f"{file_size} bytes", file_type))

    def deselect_all_items(self, event):
        self.tree.selection_remove(self.tree.selection())  # Deselect all items in the main tree
        self.parent_tree.selection_remove(self.parent_tree.selection())  # Deselect all items in the parent tree

    def view_properties(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_path = selected_item[0]
            properties = self.get_file_properties(selected_path)
            messagebox.showinfo("File Properties", properties)

    def get_file_properties(self, path):
        try:
            properties = f"Path: {path}\n"
            if os.path.isdir(path):
                total_size = self.get_folder_size(path)
                properties += f"Size: {total_size / (1024 * 1024):.2f} MB\n"
            else:
                properties += f"Size: {os.path.getsize(path) / (1024 * 1024):.2f} MB\n"
            properties += f"Created: {datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')}\n"
            properties += f"Modified: {datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')}\n"
            properties += f"Accessed: {datetime.fromtimestamp(os.path.getatime(path)).strftime('%Y-%m-%d %H:%M:%S')}\n"
            return properties
        except Exception as e:
            return f"Error retrieving properties: {e}"
    def load_credentials(self):
        try:
        # Load the key
            with open("secret.key", "rb") as key_file:
                 key = key_file.read()
            cipher = Fernet(key)
        
        # Load and decrypt the credentials
            with open("credentials.enc", "rb") as enc_file:
                 encrypted_credentials = enc_file.read()
            decrypted_credentials = cipher.decrypt(encrypted_credentials)
            return json.loads(decrypted_credentials.decode("utf-8"))
        except FileNotFoundError:
            return {}  # Return empty dict if files not found
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {}
    def login(self):
        
        
        while not self.logged_in:
            login_dialog = LoginDialog(self)
            username = login_dialog.username
            password = login_dialog.password
    
            if username is None and password is None:
                # User closed the dialog without logging in or creating an account
                self.quit()
                return
            self.credentials = self.load_credentials()
            if username in self.credentials and self.credentials[username]["password"] == password:
                self.logged_in = True
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
       
    
    def get_folder_size(self, folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

# class RestartMessage(tk.Toplevel):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.title("Account")
#         self.geometry("300x250")


class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.transient(parent)
        self.grab_set()
        self.iconbitmap("D:\sf using python\pettrolium File Management System\FileManagementApp\icon.ico")

        self.username = None
        self.password = None

        self.title("Login")
        self.geometry("300x250")  # Increased height to accommodate new button

        tk.Label(self, text="Username:").pack(padx=20, pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(padx=20, pady=5)

        tk.Label(self, text="Password:").pack(padx=20, pady=10)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(padx=20, pady=5)
        
        if self.parent.is_credentials_empty:
            tk.Label(self, text="No accounts found. Please create an account.").pack(padx=20, pady=10)
            tk.Button(self, text="Create Account", command=self.on_create_account).pack(padx=20, pady=10)
        else:
            tk.Button(self, text="Login", command=self.on_login).pack(padx=20, pady=10)
            tk.Button(self, text="Forgot Password", command=self.on_forgot_password).pack(padx=20, pady=10)
        
        
       
        
        

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.center_window(parent)
        self.wait_window(self)

    # def createbtn(self):
    #     self.on_create_account()
    #     self.destroy()

        
    
    @staticmethod
    def load_encryption_key():
        # Load the encryption key from the key.key file
        with open('secret.key', 'rb') as key_file:
            return key_file.read()

    @staticmethod
    def decrypt_credentials(encrypted_data, key):
        # Create a Fernet object with the encryption key
        fernet = Fernet(key)
        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data

    def on_forgot_password(self):
        # Retrieve the username from the entry widget
        username = self.username_entry.get()
    
        # Load the encryption key
        key = LoginDialog.load_encryption_key()
        print(f"data read from env file")
    
        # Read the encrypted credentials from the file
        with open('credentials.enc', 'rb') as enc_file:
            encrypted_data = enc_file.read()
    
        # Decrypt the credentials
        decrypted_data = LoginDialog.decrypt_credentials(encrypted_data, key)
        print(f"Decrypted data: {decrypted_data}")
        # Load the credentials from the decrypted JSON data
        credentials = json.loads(decrypted_data)
    
        # Check if the username exists in the credentials dictionary
        if username in credentials:
            # Debug print statement to check the value and type
            print(f"Credentials for {username}: {credentials[username]} (type: {type(credentials[username])})")
        
            # Retrieve the email associated with the username
            email = credentials[username]["email"]
        
            # Open the reset password dialog with the retrieved email
            ResetPasswordDialog(self, email,username,credentials)
            print(f"Reset password called..... Email: {email}")
        else:
            # Show an error message if the username is not found
            messagebox.showerror("Error", "Username not found.")

    def on_create_account(self):
         
        self.destroy()
        self.parent.create_account()
        self.parent.load_and_check_credentials()
        # LoginDialog(self.parent)
    
    def center_window(self, parent):
        window_width = 300
        window_height = 250
        parent.update_idletasks()
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        # window_width = self.winfo_reqwidth()
        # window_height = self.winfo_reqheight()
        position_top = int(parent.winfo_y() + parent.winfo_height() / 2 - window_height / 2)
        position_right = int(parent.winfo_x() + parent.winfo_width() / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')


    def on_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.destroy() 
        

    def on_cancel(self):
        self.username = None
        self.password = None
        self.destroy()

if __name__ == "__main__":
    app = FileManagementApp()
    app.mainloop() 
