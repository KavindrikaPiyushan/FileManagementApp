import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil

class FileManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Management System")
        self.geometry("800x600")

        self.create_widgets()
        self.file_paths = {}  # Dictionary to store full file paths
        self.current_folder = os.getcwd()  # Keep track of the currently displayed folder

        # Display initial folder contents
        self.display_folder_contents(self.current_folder)

    def create_widgets(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Create Folder", command=self.create_folder)
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Duplicate", command=self.duplicate_file)
        edit_menu.add_command(label="Delete", command=self.delete_file)
        edit_menu.add_command(label="Add File", command=self.add_file)
        edit_menu.add_command(label="Remove File", command=self.remove_file)
        edit_menu.add_command(label="Edit File", command=self.edit_file)
        edit_menu.add_command(label="Create Subfolder", command=self.create_subfolder)

        # Add a label to show current folder path
        self.path_var = tk.StringVar()
        self.path_label = tk.Label(self, textvariable=self.path_var, anchor="w")
        self.path_label.pack(fill=tk.X, padx=5, pady=5)

        self.tree = ttk.Treeview(self)
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

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=5)
        search_entry.bind("<KeyRelease>", self.search_files)

    def display_folder_contents(self, folder_path):
        self.current_folder = folder_path
        self.path_var.set(f"Current folder: {self.current_folder}")

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add ".." for parent directory, except for root
        if self.current_folder != os.path.abspath(os.sep):
            parent_path = os.path.dirname(self.current_folder)
            self.tree.insert("", "end", iid=parent_path, text="..", values=("..", "", ""))

        # Populate with current contents
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

    def on_item_double_click(self, event):
        selected_item = self.tree.focus()
        item_path = selected_item

        if os.path.isdir(item_path):
            self.display_folder_contents(item_path)
        elif os.path.isfile(item_path):
            self.edit_file()

    def open_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.current_folder)
        if file_path:
            self.add_file_to_current_view(file_path)

    def add_file_to_current_view(self, file_path):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_name)[1]
        self.tree.insert("", "end", iid=file_path, text=file_name, 
                         values=(file_name, f"{file_size} bytes", file_type))
        self.file_paths[file_name] = file_path

    def create_folder(self):
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            new_folder_path = os.path.join(self.current_folder, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                self.display_folder_contents(self.current_folder)  # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")

    def delete_file(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        item_name = self.tree.item(selected_item, "text")
        if messagebox.askyesno("Delete Item", f"Are you sure you want to delete {item_name}?"):
            try:
                if os.path.isdir(selected_item):
                    shutil.rmtree(selected_item)
                else:
                    os.remove(selected_item)
                self.display_folder_contents(self.current_folder)  # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete item: {str(e)}")

    def duplicate_file(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to duplicate.")
            return

        item_path = selected_item
        item_name = self.tree.item(selected_item, "text")
        new_name = f"copy_of_{item_name}"
        new_path = os.path.join(self.current_folder, new_name)

        try:
            if os.path.isdir(item_path):
                shutil.copytree(item_path, new_path)
            else:
                shutil.copy2(item_path, new_path)
            self.display_folder_contents(self.current_folder)  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Could not duplicate item: {str(e)}")

    def add_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.current_folder)
        if file_path:
            try:
                shutil.copy2(file_path, self.current_folder)
                self.display_folder_contents(self.current_folder)  # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Could not add file: {str(e)}")

    def remove_file(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file to remove.")
            return

        if os.path.isdir(selected_item):
            messagebox.showerror("Error", "Please select a file, not a folder.")
            return

        if messagebox.askyesno("Remove File", f"Are you sure you want to remove {os.path.basename(selected_item)}?"):
            try:
                os.remove(selected_item)
                self.display_folder_contents(self.current_folder)  # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Could not remove file: {str(e)}")

    def edit_file(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file to edit.")
            return

        if os.path.isdir(selected_item):
            messagebox.showerror("Error", "Please select a file, not a folder.")
            return

        try:
            os.startfile(selected_item)  # This will open the file with the default application
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def create_subfolder(self):
        folder_name = simpledialog.askstring("Create Subfolder", "Enter subfolder name:")
        if folder_name:
            new_folder_path = os.path.join(self.current_folder, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                self.display_folder_contents(self.current_folder)  # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Could not create subfolder: {str(e)}")

    def search_files(self, event):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            item_name = self.tree.item(item, "text").lower()
            if query in item_name:
                self.tree.item(item, tags=("match",))
            else:
                self.tree.item(item, tags=("",))

        self.tree.tag_configure("match", background="yellow")

if __name__ == "__main__":
    app = FileManagementApp()
    app.mainloop()