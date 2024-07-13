import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
from datetime import datetime
import subprocess
import platform
import json

CONFIG_FILE = 'editor_config.json'

class FileManagementApp(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.title("File Management System")
        self.geometry("800x600")

        self.create_widgets()
        self.file_paths = {}  # Dictionary to store full file paths
        self.folder_history = []  # List to keep track of folder navigation history
        self.root_folder = os.path.join(os.path.expanduser("~"), "Pettrolium Files")  # Use this folder as the root
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

    def get_folder_size(self, folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

if __name__ == "__main__":
    app = FileManagementApp()
    app.mainloop() 
