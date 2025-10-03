import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

TASKS_FILE = os.path.join(os.path.dirname(__file__), "config/tasks.json")

class TaskEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Editor de Tareas")
        self.root.geometry("600x400")
        self.root.minsize(500, 300)
        
        self.tasks = self.load_tasks()
        self.setup_ui()
        
    def load_tasks(self):
        """Cargar tareas existentes"""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tasks", [])
        return []
    
    def save_tasks(self):
        """Guardar tareas al archivo JSON"""
        data = {
            "task_types": {
                "bool": "True/False task",
                "numeric": "Number input task",
                "text": "Text input task"
            },
            "tasks": self.tasks
        }
        
        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        messagebox.showinfo("Guardado", f"Tareas guardadas correctamente")
    
    def setup_ui(self):
        """Configurar interfaz simple"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title = ttk.Label(main_frame, text="Editor de Tareas", font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, pady=(0, 10))
        
        # Lista de tareas existentes
        list_frame = ttk.LabelFrame(main_frame, text="Tareas Existentes", padding="5")
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para tareas
        self.task_tree = ttk.Treeview(list_frame, columns=("Type",), show="tree headings", height=6)
        self.task_tree.heading("#0", text="Tarea")
        self.task_tree.heading("Type", text="Tipo")
        self.task_tree.column("#0", width=400)
        self.task_tree.column("Type", width=100)
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Botones para lista
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_task).pack(side="left", padx=(0, 5))
        
        # Formulario nueva tarea
        form_frame = ttk.LabelFrame(main_frame, text="Nueva Tarea", padding="5")
        form_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Descripción
        ttk.Label(form_frame, text="Tarea:").grid(row=0, column=0, sticky="nw", padx=(0, 5), pady=(0, 5))
        self.task_text = scrolledtext.ScrolledText(form_frame, height=3, width=50)
        self.task_text.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        
        # Tipo
        ttk.Label(form_frame, text="Tipo:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.type_var = tk.StringVar(value="bool")
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, 
                                 values=["bool", "numeric", "text"], state="readonly", width=15)
        type_combo.grid(row=1, column=1, sticky="w")
        
        # Botones principales
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Agregar Tarea", command=self.add_task).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Guardar Todo", command=self.save_tasks).pack(side="left")
        
        self.refresh_task_list()
    
    def refresh_task_list(self):
        """Actualizar lista de tareas"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for task in self.tasks:
            self.task_tree.insert("", "end", text=task["task"], values=(task["type"],))
    
    def add_task(self):
        """Agregar nueva tarea"""
        task_text = self.task_text.get("1.0", "end-1c").strip()
        if not task_text:
            messagebox.showerror("Error", "La descripción de la tarea es obligatoria")
            return
        
        new_task = {
            "task": task_text,
            "type": self.type_var.get()
        }
        
        self.tasks.append(new_task)
        self.refresh_task_list()
        
        # Limpiar formulario
        self.task_text.delete("1.0", "end")
        
        messagebox.showinfo("Éxito", "Tarea agregada correctamente")
    
    def delete_task(self):
        """Eliminar tarea seleccionada"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta tarea?"):
            index = self.task_tree.index(selection[0])
            del self.tasks[index]
            self.refresh_task_list()
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    editor = TaskEditor()
    editor.run()