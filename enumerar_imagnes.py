
import os
import uuid
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

EXTENSIONES_IMAGENES = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp", ".tif", ".tiff"
}

class EnumeradorImagenes:

    def __init__(self, root):
        self.root = root
        self.root.title("Enumerador de imagenes")
        self.root.geometry("650x450")
        self.root.resizable(True, True)

        self.carpeta = None
        titulo = tk.Label(
            root,
            text="ENUMERADOR DE IMÁGENES",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=20)
        self.btn_carpeta = ttk.Button(
            root,
            text="Seleccionar carpeta",
            command=self.seleccionar_carpeta
        )
        self.btn_carpeta.pack(pady=5)
        self.lbl_carpeta = tk.Label(
            root,
            text="Ninguna carpeta seleccionada",
            wraplength=580
        )
        self.lbl_carpeta.pack(pady=10)
        self.btn_renombrar = ttk.Button(
            root,
            text="Enumerar imágenes",
            command=self.enumerar_imagenes,
            state="disabled"
        )
        self.btn_renombrar.pack(pady=10)
        self.estado = tk.StringVar(
            value="Seleccioná una carpeta para comenzar."
        )

        tk.Label(
            root,
            textvariable=self.estado,
            wraplength=580,
            justify="center"
        ).pack(pady=10)

        self.lista = tk.Listbox(
            root,
            width=75,
            height=12
        )
        self.lista.pack(
            padx=15,
            pady=10,
            fill="both",
            expand=True
        )

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory(
            title="Seleccioná la carpeta con imágenes"
        )

        if not ruta:
            return

        self.carpeta = Path(ruta)
        self.lbl_carpeta.config(text=str(self.carpeta))

        self.lista.delete(0, tk.END)

        imagenes = self.obtener_imagenes()

        for imagen in imagenes:
            self.lista.insert(tk.END, imagen.name)

        self.estado.set(
            f"Se encontraron {len(imagenes)} imágenes."
        )

        self.btn_renombrar.config(
            state="normal" if imagenes else "disabled"
        )

    def obtener_imagenes(self):
        """Obtiene imágenes de la carpeta seleccionada."""
        if not self.carpeta:
            return []

        return sorted(
            [
                archivo
                for archivo in self.carpeta.iterdir()
                if archivo.is_file()
                and archivo.suffix.lower() in EXTENSIONES_IMAGENES
            ],
            key=lambda archivo: archivo.name.casefold()
        )

    def enumerar_imagenes(self):
        imagenes = self.obtener_imagenes()

        if not imagenes:
            messagebox.showinfo(
                "Información",
                "No se encontraron imágenes."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar operación",
            f"Se renombrarán {len(imagenes)} imágenes.\n\n"
            "Los nombres originales cambiarán.\n"
            "¿Querés continuar?"
        )

        if not confirmar:
            return

        temporales = []
        renombradas = []

        try:
    
            for imagen in imagenes:
                temporal = imagen.with_name(
                    f"__temp_{uuid.uuid4().hex}.tmp"
                )

                imagen.rename(temporal)
                temporales.append((temporal, imagen))
            for numero, (temporal, original) in enumerate(
                temporales, start=1
            ):
                nuevo_nombre = (
                    self.carpeta / f"{numero}{original.suffix.lower()}"
                )

                temporal.rename(nuevo_nombre)
                renombradas.append(nuevo_nombre)
            self.lista.delete(0, tk.END)

            for archivo in renombradas:
                self.lista.insert(tk.END, archivo.name)

            self.estado.set(
                f"¡Proceso completado! "
                f"{len(renombradas)} imágenes enumeradas."
            )

            messagebox.showinfo(
                "Proceso terminado",
                f"Se enumeraron {len(renombradas)} imágenes."
            )

        except OSError as error:
            for temporal, original in reversed(temporales):
                if temporal.exists() and not original.exists():
                    try:
                        temporal.rename(original)
                    except OSError:
                        pass

            messagebox.showerror(
                "Error",
                f"No se pudo completar la operación:\n{error}\n\n"
                "Revisá la carpeta antes de volver a intentarlo."
            )

            self.estado.set("Se produjo un error durante el proceso.")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = EnumeradorImagenes(ventana)
    ventana.mainloop()
