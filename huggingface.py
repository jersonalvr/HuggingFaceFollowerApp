import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sv_ttk
import os
import sys
import json
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from PIL import Image, ImageTk

class HuggingFaceCredentialManager:
    CREDENTIALS_FILE = "hf_credentials.json"

    @classmethod
    def save_credentials(cls, username, password):
        """Guardar credenciales de manera segura"""
        credentials = {
            "username": username,
            "password": cls.simple_encrypt(password)
        }
        
        with open(cls.CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)

    @classmethod
    def load_credentials(cls):
        """Cargar credenciales guardadas"""
        try:
            with open(cls.CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
                return {
                    "username": credentials["username"],
                    "password": cls.simple_decrypt(credentials["password"])
                }
        except FileNotFoundError:
            return {"username": "", "password": ""}

    @staticmethod
    def simple_encrypt(text):
        """Método simple de encriptación (para propósitos básicos)"""
        return ''.join([chr(ord(c) + 1) for c in text])

    @staticmethod
    def simple_decrypt(encrypted_text):
        """Método simple de desencriptación"""
        return ''.join([chr(ord(c) - 1) for c in encrypted_text])

class HuggingFaceFollowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HuggingFace Mass Follower")
        self.root.geometry("500x700")
        
        sv_ttk.set_theme("light")
        self.set_icon()
        self.create_widgets()
        self.load_saved_credentials()

    def set_icon(self):
        """Set application icon"""
        try:
            # Determine base path
            base_path = (sys._MEIPASS if getattr(sys, 'frozen', False) 
                        else os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "hf-logo.ico")
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título con logo
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 20), fill=tk.X)
        
        # Cargar y redimensionar logo
        try:
            base_path = (sys._MEIPASS if getattr(sys, 'frozen', False) 
                        else os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(base_path, "hf-logo.png")
            
            # Intentar cargar la imagen
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((50, 50), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # Añadir logo
                logo_label = ttk.Label(title_frame, image=self.logo_photo)
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Título
        title_label = ttk.Label(
            title_frame, 
            text="HuggingFace Mass Follower", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Username
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
        
        # Password
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, show="*", width=40)
        self.password_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
        
        # Checkbox para guardar credenciales
        self.save_credentials_var = tk.BooleanVar(value=True)
        save_credentials_check = ttk.Checkbutton(
            main_frame, 
            text="Guardar credenciales", 
            variable=self.save_credentials_var
        )
        save_credentials_check.pack(pady=10)
        
        # Organization URL
        org_frame = ttk.Frame(main_frame)
        org_frame.pack(fill=tk.X, pady=5)
        ttk.Label(org_frame, text="Org URL:").pack(side=tk.LEFT)
        self.org_url_entry = ttk.Entry(org_frame, width=40)
        self.org_url_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
        
        # Start Button
        self.start_button = ttk.Button(
            main_frame, 
            text="Seguir Usuarios", 
            command=self.start_following
        )
        self.start_button.pack(pady=20, fill=tk.X)
        
        # Log Area
        log_label = ttk.Label(main_frame, text="Log:", font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame, 
            height=10, 
            width=60, 
            wrap=tk.WORD
        )
        self.log_text.pack(expand=True, fill=tk.BOTH, pady=10)

        # Theme Switch
        self.theme_switch = ttk.Checkbutton(
            main_frame, 
            text="Dark Theme", 
            style="Switch.TCheckbutton", 
            command=self.toggle_theme
        )
        self.theme_switch.pack(pady=10)

    def load_saved_credentials(self):
        """Cargar credenciales guardadas al iniciar"""
        saved_creds = HuggingFaceCredentialManager.load_credentials()
        self.username_entry.insert(0, saved_creds["username"])
        self.password_entry.insert(0, saved_creds["password"])

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_theme = sv_ttk.get_theme()
        if current_theme == "dark":
            sv_ttk.set_theme("light")
            self.theme_switch.config(text="Dark Theme")
        else:
            sv_ttk.set_theme("dark")
            self.theme_switch.config(text="Light Theme")

    def log(self, message):
        """Registrar mensajes en área de log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_following(self):
        """Iniciar proceso de seguimiento"""
        # Validar entradas
        username = self.username_entry.get()
        password = self.password_entry.get()
        org_url = self.org_url_entry.get()
        
        if not all([username, password, org_url]):
            messagebox.showerror("Error", "Por favor llene todos los campos")
            return
        
        # Guardar credenciales si está marcado
        if self.save_credentials_var.get():
            HuggingFaceCredentialManager.save_credentials(username, password)
        
        # Deshabilitar botón de inicio
        self.start_button.config(state=tk.DISABLED)
        
        # Limpiar logs anteriores
        self.log_text.delete(1.0, tk.END)
        
        # Iniciar seguimiento en hilo separado
        threading.Thread(
            target=self.follow_users, 
            args=(username, password, org_url), 
            daemon=True
        ).start()

    def follow_users(self, username, password, org_url):
        """Automatización Selenium para seguir usuarios"""
        driver = None
        try:
            # Configuración de Chrome
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Inicializar WebDriver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=chrome_options
            )
            
            wait = WebDriverWait(driver, 10)
            
            # Iniciar sesión
            self.log("Iniciando sesión...")
            driver.get("https://huggingface.co/login")
            
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(1)
            
            # Navegar a organización
            self.log(f"Navegando a organización: {org_url}")
            driver.get(org_url)
            time.sleep(1)
            
            # Abrir miembros del equipo
            team_members_button = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(text(), 'Team members')]"
                ))
            )
            team_members_button.click()
            
            time.sleep(1)
            
            # Usando la coincidencia exacta del texto 'Follow'
            follow_buttons = driver.find_elements(
                By.XPATH, "//button[.//div[text() = 'Follow']]"
            )

            self.log(f"Encontrados {len(follow_buttons)} usuarios para seguir")
            
            # Seguir usuarios
            followed_count = 0
            for index, button in enumerate(follow_buttons, 1):
                try:
                    # Scroll y esperar visibilidad
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    wait.until(EC.element_to_be_clickable(button))
                    
                    # Hacer clic con JavaScript para mayor confiabilidad
                    driver.execute_script("arguments[0].click();", button)
                    
                    # Esperar cambio de estado
                    time.sleep(0.5)

                    # Verificar si cambió a "Following"
                    following_text = button.text
                    if following_text.lower() == "Following":
                        followed_count += 1
                        self.log(f"Seguido: Usuario {index}")

                except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                    self.log(f"No se pudo seguir usuario {index}: {e}")
            
            self.log(f"Seguimiento completado. Total seguidos: {followed_count}")
        
        except Exception as e:
            self.log(f"Error durante el proceso: {e}")
        
        finally:
            # Cerrar navegador si está abierto
            if driver:
                driver.quit()
            
            # Rehabilitar botón de inicio
            self.root.after(0, self.start_button.config, {"state": tk.NORMAL})

def main():
    root = tk.Tk()
    app = HuggingFaceFollowerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()