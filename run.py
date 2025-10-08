#!/usr/bin/env python3
"""
Script multiplataforma para configurar y ejecutar User Gaze Track
Uso: python run.py [--venv]
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path


class GazeTrackRunner:
    def __init__(self):
        self.env_name = "user-gaze-track"
        self.venv_dir = ".venv"
        self.use_conda = False
        self.is_windows = platform.system() == "Windows"
        
    def print_step(self, message, emoji="🔧"):
        """Imprime un mensaje con formato"""
        print(f"{emoji} {message}")
        
    def run_command(self, command, shell=True, check=True, capture_output=False):
        """Ejecuta un comando del sistema"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=shell, check=check, 
                                      capture_output=True, text=True)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=shell, check=check)
                return True
        except subprocess.CalledProcessError as e:
            if capture_output:
                return None
            print(f"❌ Error ejecutando comando: {command}")
            print(f"   {e}")
            return False
            
    def command_exists(self, command):
        """Verifica si un comando está disponible"""
        return shutil.which(command) is not None
        
    def detect_environment_manager(self, force_venv=False):
        """Detecta qué gestor de entornos usar"""
        if force_venv:
            self.print_step("Forzando el uso de Python venv...")
            self.use_conda = False
        elif self.command_exists("conda"):
            self.print_step("Conda detectado. Usando conda para gestión de entornos...", "🐍")
            self.use_conda = True
        else:
            self.print_step("Conda no disponible. Usando Python venv como fallback...", "⚠️")
            self.use_conda = False
            
    def conda_env_exists(self):
        """Verifica si el entorno conda existe"""
        try:
            output = self.run_command("conda env list", capture_output=True)
            if output:
                for line in output.split('\n'):
                    if line.strip().startswith(self.env_name):
                        return True
            return False
        except:
            return False
            
    def setup_conda_environment(self):
        """Configura el entorno con conda"""
        if self.conda_env_exists():
            self.print_step(f"El entorno conda '{self.env_name}' ya existe.", "✅")
        else:
            self.print_step(f"Creando el entorno conda '{self.env_name}' desde environment.yml...", "⚙️")
            if not self.run_command(f"conda env create -n {self.env_name} -f environment.yml"):
                return False
            self.print_step(f"Entorno conda '{self.env_name}' creado.", "✅")
        return True
        
    def get_conda_python(self):
        """Obtiene la ruta del Python del entorno conda"""
        try:
            # Obtener la ruta base de conda
            conda_info = self.run_command("conda info --base", capture_output=True)
            if conda_info:
                if self.is_windows:
                    python_path = f"{conda_info}\\envs\\{self.env_name}\\python.exe"
                else:
                    python_path = f"{conda_info}/envs/{self.env_name}/bin/python"
                return python_path
            return None
        except:
            return None
            
    def setup_venv_environment(self):
        """Configura el entorno con venv"""
        venv_path = Path(self.venv_dir)
        venv_exists = venv_path.exists()
        
        if venv_exists:
            self.print_step(f"El entorno virtual '{self.venv_dir}' ya existe.", "✅")
        else:
            self.print_step(f"Creando entorno virtual Python '{self.venv_dir}'...", "⚙️")
            if not self.run_command(f"python -m venv {self.venv_dir}"):
                return False
            self.print_step(f"Entorno virtual '{self.venv_dir}' creado.", "✅")
            
        return True, not venv_exists
        
    def get_venv_python(self):
        """Obtiene la ruta del Python del entorno virtual"""
        if self.is_windows:
            return str(Path(self.venv_dir) / "Scripts" / "python.exe")
        else:
            return str(Path(self.venv_dir) / "bin" / "python")
            
    def check_flask_installed(self, python_path):
        """Verifica si Flask está instalado"""
        try:
            result = self.run_command(f'"{python_path}" -c "import flask"', capture_output=True)
            return result is not None
        except:
            return False
            
    def install_dependencies(self, python_path):
        """Instala las dependencias del proyecto"""
        self.print_step("Instalando dependencias...", "📦")
        
        requirements_file = Path("requirements.txt")
        if requirements_file.exists() and requirements_file.stat().st_size > 0:
            self.print_step("   Desde requirements.txt...")
            if not self.run_command(f'"{python_path}" -m pip install -r requirements.txt'):
                return False
        else:
            self.print_step("   Dependencias básicas...")
            deps = [
                "flask==3.1.0",
                "flask-sqlalchemy==3.1.1", 
                "flasgger==0.9.7.1",
                "numpy==1.26.4",
                "ttkbootstrap==1.10.1"
            ]
            for dep in deps:
                if not self.run_command(f'"{python_path}" -m pip install {dep}'):
                    return False
                    
        self.print_step("Dependencias instaladas.", "✅")
        return True
        
    def ask_for_configuration(self, python_path):
        """Pregunta si el usuario quiere configurar la aplicación"""
        print()
        try:
            choice = input("¿Desea modificar las configuraciones antes de ejecutar la aplicación? (s/n): ")
            if choice.lower() in ['s', 'sí', 'si', 'y', 'yes']:
                self.print_step("Abriendo configurador...", "⚙️")
                if self.run_command(f'"{python_path}" src/config.py'):
                    self.print_step("Configuración completada.", "✅")
                else:
                    print("❌ Error al abrir el configurador")
                    return False
        except KeyboardInterrupt:
            print("\n❌ Cancelado por el usuario")
            return False
        return True
        
    def run_application(self, python_path):
        """Ejecuta la aplicación principal"""
        self.print_step("Ejecutando la aplicación...", "🚀")
        return self.run_command(f'"{python_path}" src/app.py')
        
    def run(self):
        """Método principal que ejecuta todo el flujo"""
        # Detectar argumentos
        force_venv = "--venv" in sys.argv
        
        # Detectar gestor de entornos
        self.detect_environment_manager(force_venv)
        
        if self.use_conda:
            # Flujo conda
            if not self.setup_conda_environment():
                sys.exit(1)
                
            python_path = self.get_conda_python()
            if not python_path:
                print("❌ No se pudo obtener la ruta del Python de conda")
                sys.exit(1)
                
        else:
            # Flujo venv
            success, is_new_env = self.setup_venv_environment()
            if not success:
                sys.exit(1)
                
            python_path = self.get_venv_python()
            
            # Instalar dependencias si es necesario
            if is_new_env or not self.check_flask_installed(python_path):
                if not self.install_dependencies(python_path):
                    sys.exit(1)
            else:
                self.print_step("Dependencias ya instaladas, omitiendo instalación.", "✅")
                
        # Configuración opcional
        if not self.ask_for_configuration(python_path):
            sys.exit(1)
            
        # Ejecutar aplicación
        if not self.run_application(python_path):
            sys.exit(1)


if __name__ == "__main__":
    try:
        runner = GazeTrackRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n❌ Ejecución cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)