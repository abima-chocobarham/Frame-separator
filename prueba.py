import cv2
import os
import customtkinter as ctk  # La magia moderna
from tkinter import filedialog, messagebox
from PIL import Image
import threading

# Configuración global de tema
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

class ExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Extractor Pro")
        self.geometry("600x650")
        self.resizable(False, False)
        
        # Estado
        self.ruta_video = None
        self.stop_event = threading.Event()

        # --- UI LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Marco Principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Título
        self.lbl_titulo = ctk.CTkLabel(self.main_frame, text="Video a Frames", 
                                     font=("Roboto Medium", 24))
        self.lbl_titulo.pack(pady=(20, 10))

        # Área de Miniatura (Placeholder)
        self.preview_frame = ctk.CTkFrame(self.main_frame, width=400, height=250, fg_color="gray20")
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False) # Evita que se encoja

        self.lbl_imagen = ctk.CTkLabel(self.preview_frame, text="Arrastra o selecciona un video", text_color="gray")
        self.lbl_imagen.place(relx=0.5, rely=0.5, anchor="center")

        # Info
        self.lbl_info = ctk.CTkLabel(self.main_frame, text="", font=("Roboto", 12), text_color="gray70")
        self.lbl_info.pack(pady=10)

        # Barra de Progreso
        self.barra = ctk.CTkProgressBar(self.main_frame, width=400)
        self.barra.set(0)
        self.barra.pack(pady=(10, 5))
        
        self.lbl_estado = ctk.CTkLabel(self.main_frame, text="Listo", font=("Roboto", 10))
        self.lbl_estado.pack(pady=(0, 20))

        # Botones
        self.btn_cargar = ctk.CTkButton(self.main_frame, text="Seleccionar Video", 
                                      command=self.seleccionar_video, height=40, width=180)
        self.btn_cargar.pack(pady=10)

        self.btn_iniciar = ctk.CTkButton(self.main_frame, text="Iniciar Extracción", 
                                       command=self.iniciar_thread, state="disabled", 
                                       fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                       height=40, width=180)
        self.btn_iniciar.pack(pady=5)

    def seleccionar_video(self):
        ruta = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov")])
        if not ruta: return

        self.ruta_video = ruta
        
        # Procesar miniatura
        video = cv2.VideoCapture(ruta)
        video.set(cv2.CAP_PROP_POS_FRAMES, 30)
        success, frame = video.read()
        
        # Datos
        fps = video.get(cv2.CAP_PROP_FPS)
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frames / fps if fps > 0 else 0
        video.release()

        if success:
            # Convertir imagen para CTk
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame)
            # CTkImage optimiza para pantallas HDPI
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(400, 225))
            
            self.lbl_imagen.configure(image=ctk_img, text="")
            self.lbl_info.configure(text=f"{os.path.basename(ruta)}\n⏱ {duration:.1f} seg  |  🎞 {int(frames)} frames")
            
            # Activar botón principal con estilo sólido (color primario)
            self.btn_iniciar.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
        
    def iniciar_thread(self):
        self.btn_iniciar.configure(state="disabled")
        self.btn_cargar.configure(state="disabled")
        threading.Thread(target=self.procesar).start()

    def procesar(self):
        try:
            ruta_base = "/home/abimael/Imágenes/Frames"
            nombre = os.path.basename(self.ruta_video).split('.')[0]
            destino = os.path.join(ruta_base, nombre)
            os.makedirs(destino, exist_ok=True)

            cap = cv2.VideoCapture(self.ruta_video)
            duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            
            segundo = 0
            guardados = 0

            while segundo < duration:
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if not ret: break

                cv2.imwrite(os.path.join(destino, f"sec_{guardados:04d}.jpg"), frame)
                
                # Actualizar UI desde hilo
                progreso = segundo / duration
                self.barra.set(progreso)
                self.lbl_estado.configure(text=f"Procesando: {int(progreso*100)}%")
                
                segundo += 1
                guardados += 1

            cap.release()
            self.lbl_estado.configure(text="¡Completado!")
            messagebox.showinfo("Éxito", f"Se guardaron {guardados} imágenes")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        finally:
            self.btn_iniciar.configure(state="normal")
            self.btn_cargar.configure(state="normal")

if __name__ == "__main__":
    app = ExtractorApp()
    app.mainloop()