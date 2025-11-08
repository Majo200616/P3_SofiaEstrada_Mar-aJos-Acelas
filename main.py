import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt
import cv2
from datetime import datetime
import nibabel as nib


class DicomLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.slices = []
        self.volume = None

    def load(self):
        # Leer todos los archivos DICOM en la carpeta
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.dcm')]
        datasets = [pydicom.dcmread(os.path.join(self.folder_path, f)) for f in files]

        # Ordenar por posición (eje Z)
        datasets.sort(key=lambda x: int(x.InstanceNumber))

        # Crear el volumen 3D
        self.volume = np.stack([d.pixel_array for d in datasets])
        print(f"Volumen cargado con forma: {self.volume.shape}")
        return self.volume
    
    def mostrar_cortes(self):
        
      """Muestra los tres cortes principales del volumen"""
      if self.volume is None:
          raise ValueError("Primero debes cargar los datos DICOM con el método load().")

      z, y, x = np.array(self.volume.shape) // 2  # posiciones centrales

      fig, axs = plt.subplots(1, 3, figsize=(12, 4))

      # Corte transversal (XY)
      axs[0].imshow(self.volume[z, :, :], cmap='gray')
      axs[0].set_title('Transversal (XY)')
      axs[0].axis('off')

      # Corte coronal (XZ)
      axs[1].imshow(self.volume[:, y, :], cmap='gray')
      axs[1].set_title('Coronal (XZ)')
      axs[1].axis('off')

      # Corte sagital (YZ)
      axs[2].imshow(self.volume[:, :, x], cmap='gray')
      axs[2].set_title('Sagital (YZ)')
      axs[2].axis('off')

      plt.tight_layout()
      plt.show()
    
# Clase para mostrar la información del estudio DICOM
class EstudioImaginologico:
    def __init__(self, folder_path, volume):
        """Crea un estudio imaginológico a partir de una carpeta DICOM y su volumen reconstruido."""
        self.folder_path = folder_path
        self.volume = volume

        # Tomar el primer archivo DICOM de la carpeta
        primer_archivo = [f for f in os.listdir(folder_path) if f.lower().endswith('.dcm')][0]
        ds = pydicom.dcmread(os.path.join(folder_path, primer_archivo))

        # Extraer atributos DICOM relevantes
        self.study_date = getattr(ds, "StudyDate", None)
        self.study_time = getattr(ds, "StudyTime", None)
        self.modality = getattr(ds, "Modality", None)
        self.study_description = getattr(ds, "StudyDescription", None)
        self.series_time = getattr(ds, "SeriesTime", None)

        # Calcular la duración del estudio
        self.duracion = self._calcular_duracion()

    def _calcular_duracion(self):
        """Calcula la duración (segundos) entre StudyTime y SeriesTime."""
        if not self.study_time or not self.series_time:
            return None
        try:
            h1, m1, s1 = int(self.study_time[:2]), int(self.study_time[2:4]), int(self.study_time[4:6])
            h2, m2, s2 = int(self.series_time[:2]), int(self.series_time[2:4]), int(self.series_time[4:6])
            return (h2*3600 + m2*60 + s2) - (h1*3600 + m1*60 + s1)
        except:
            return None

    def mostrar_info(self):
        """Muestra la información general del estudio"""
        print("\nInformación del Estudio Imaginológico DICOM:")
        print(f"Fecha del Estudio:       {self.study_date}")
        print(f"Hora del Estudio:        {self.study_time}")
        print(f"Modalidad:               {self.modality}")
        print(f"Descripción del Estudio: {self.study_description}")
        print(f"Hora de la Serie:        {self.series_time}")
        print(f"Duración (segundos):     {self.duracion}")
        print(f"Forma del volumen:       {self.volume.shape}")

class GestionImagenes:
    def __init__(self, volume):
        self.volume = volume

    def obtener_corte(self, tipo, indice):
        """Devuelve el corte solicitado según tipo ('axial', 'coronal', 'sagital') e índice."""
        if tipo == "axial":
            return self.volume[indice, :, :]
        elif tipo == "coronal":
            return self.volume[:, indice, :]
        elif tipo == "sagital":
            return self.volume[:, :, indice]
        else:
            raise ValueError("Tipo de corte no válido")

    def segmentar(self, corte, tipo_binarizacion):
        """Aplica segmentación (binarización) según el tipo especificado."""
        metodos = {
            "binario": cv2.THRESH_BINARY,
            "binario_inv": cv2.THRESH_BINARY_INV,
            "truncado": cv2.THRESH_TRUNC,
            "tozero": cv2.THRESH_TOZERO,
            "tozero_inv": cv2.THRESH_TOZERO_INV
        }

        metodo = metodos.get(tipo_binarizacion.lower())
        if metodo is None:
            raise ValueError("Tipo de binarización no válido")

        umbral, segmentada = cv2.threshold(corte, 100, 255, metodo)

        plt.figure(figsize=(8, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(corte, cmap='gray')
        plt.title("Original")
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(segmentada, cmap='gray')
        plt.title(f"Segmentada ({tipo_binarizacion})")
        plt.axis('off')

        plt.show()

        return segmentada
    
    def zoom_y_recorte(self, pixel_spacing=(1, 1), slice_thickness=1, nombre_archivo=None):
        """Realiza un zoom sobre el corte central, dibuja el cuadro y guarda el recorte."""
        corte = self.volume[self.volume.shape[0] // 2, :, :]

        img_norm = ((corte - np.min(corte)) / (np.max(corte) - np.min(corte)) * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_norm, cv2.COLOR_GRAY2BGR)

        h, w = img_bgr.shape[:2]
        x, y, ancho, alto = w // 4, h // 4, w // 2, h // 2

        cv2.rectangle(img_bgr, (x, y), (x + ancho, y + alto), (0, 255, 255), 2)

        dim_x_mm = ancho * pixel_spacing[0]
        dim_y_mm = alto * pixel_spacing[1]
        texto = f"{dim_x_mm:.1f}mm x {dim_y_mm:.1f}mm, Espesor: {slice_thickness}mm"
        cv2.putText(img_bgr, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

        recorte = img_norm[y:y+alto, x:x+ancho]
        recorte_zoom = cv2.resize(recorte, (w, h), interpolation=cv2.INTER_CUBIC)

        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        axs[0].imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        axs[0].set_title("Corte original con cuadro")
        axs[0].axis('off')

        axs[1].imshow(recorte_zoom, cmap='gray')
        axs[1].set_title("Recorte con zoom")
        axs[1].axis('off')

        plt.tight_layout()
        plt.show()

        # Guardar si se proporciona un nombre
        if nombre_archivo:
            cv2.imwrite(f"{nombre_archivo}.png", recorte_zoom)
            print(f"Imagen recortada guardada como {nombre_archivo}.png")

        return recorte_zoom
    
    def aplicar_morfologia(self, imagen, operacion, kernel_size=3, nombre_salida=None):
        """Aplica una transformación morfológica a la imagen dada."""
    
        if imagen.dtype != np.uint8:
            imagen = ((imagen - np.min(imagen)) / (np.max(imagen) - np.min(imagen)) * 255).astype(np.uint8)
    
        # Crear kernel morfológico
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
        # Aplicar la operación correspondiente
        if operacion == 'erode':
            resultado = cv2.erode(imagen, kernel, iterations=1)
        elif operacion == 'dilate':
            resultado = cv2.dilate(imagen, kernel, iterations=1)
        elif operacion == 'open':
            resultado = cv2.morphologyEx(imagen, cv2.MORPH_OPEN, kernel)
        elif operacion == 'close':
            resultado = cv2.morphologyEx(imagen, cv2.MORPH_CLOSE, kernel)
        else:
            raise ValueError("Operación morfológica no válida. Usa: 'erode', 'dilate', 'open' o 'close'.")
    
        # Mostrar el resultado
        plt.imshow(resultado, cmap='gray')
        plt.title(f"aplicar_morfologia: {operacion}")
        plt.axis('off')
        plt.show()
    
        # Guardar la imagen resultante
        if nombre_salida is None:
            nombre_salida = f"morfologia_{operacion}.png"
        cv2.imwrite(nombre_salida, resultado)
        print(f"Imagen morfológica guardada como {nombre_salida}")
    
        return resultado

def zoom_y_recorte(volume, pixel_spacing=(1,1), slice_thickness=1):
    """
    Realiza un 'zoom' en el corte central del volumen, dibuja un cuadro de recorte,
    normaliza, redimensiona y muestra ambas imágenes con OpenCV.
    """
    # Seleccionar el corte central
    corte = volume[volume.shape[0] // 2, :, :]

    #Normalización a uint8 según la fórmula dada
    img_norm = ((corte - np.min(corte)) / (np.max(corte) - np.min(corte)) * 255).astype(np.uint8)

    # Convertir a BGR para dibujar colores
    img_bgr = cv2.cvtColor(img_norm, cv2.COLOR_GRAY2BGR)

    # Definir región de interés (ROI) para el recorte
    h, w = img_bgr.shape[:2]
    x, y, ancho, alto = w // 4, h // 4, w // 2, h // 2  # recorte central

    # Dibujar el cuadro amarillo sobre la imagen original
    cv2.rectangle(img_bgr, (x, y), (x + ancho, y + alto), (0, 255, 255), 2)

    # Calcular dimensiones físicas en mm (usando pixelSpacing y SliceThickness)
    dim_x_mm = ancho * pixel_spacing[0]
    dim_y_mm = alto * pixel_spacing[1]
    texto = f"{dim_x_mm:.1f}mm x {dim_y_mm:.1f}mm, Espesor: {slice_thickness}mm"

    # Escribir el texto sobre la imagen
    cv2.putText(img_bgr, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    #Recorte de la región seleccionada
    recorte = img_norm[y:y+alto, x:x+ancho]

    #Redimensionar el recorte (zoom)
    recorte_zoom = cv2.resize(recorte, (w, h), interpolation=cv2.INTER_CUBIC)

    #Mostrar ambas imágenes con matplotlib
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    axs[0].title("Corte original con cuadro")
    axs[0].axis('off')

    axs[1].imshow(recorte_zoom, cmap='gray')
    axs[1].set_title("Recorte con zoom")
    axs[1].axis('off')

    plt.tight_layout()
    plt.show()

    # Guardar el recorte zoom como archivo PNG
    nombre = input("Ingrese el nombre para guardar la imagen recortada: ")
    cv2.imwrite(f"{nombre}.png", recorte_zoom)
    print(f"Imagen recortada guardada como {nombre}.png")






def convertir_a_nifti(carpeta_dicom, nombre_salida="resultado.nii"):
    """
    Convierte una carpeta con archivos DICOM a formato NIfTI (.nii).
    
    Parámetros:
        carpeta_dicom (str): ruta a la carpeta que contiene los archivos DICOM
        nombre_salida (str): nombre del archivo .nii de salida
    """
    #Leer todos los archivos DICOM de la carpeta
    archivos = [os.path.join(carpeta_dicom, f) for f in os.listdir(carpeta_dicom) if f.endswith(".dcm")]
    if not archivos:
        print("No se encontraron archivos DICOM en la carpeta.")
        return

    #Cargar las imágenes y ordenarlas por su posición en el eje Z
    slices = [pydicom.dcmread(a) for a in archivos]
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]) if "ImagePositionPatient" in s else 0)

    #Crear un volumen 3D con los píxeles de cada corte
    volumen = np.stack([s.pixel_array for s in slices], axis=-1)

    #Extraer el tamaño de píxel y el espesor del corte (si están disponibles)
    try:
        pixel_spacing = slices[0].PixelSpacing
        slice_thickness = float(slices[0].SliceThickness)
    except:
        pixel_spacing = [1.0, 1.0]
        slice_thickness = 1.0

    # Crear la matriz de afinidad (define la orientación espacial del volumen)
    affine = np.diag([pixel_spacing[0], pixel_spacing[1], slice_thickness, 1])

    #Crear el objeto NIfTI
    nifti_img = nib.Nifti1Image(volumen, affine)

    #Guardar el archivo
    nib.save(nifti_img, nombre_salida)
    print(f"Conversión completada. Archivo guardado como: {nombre_salida}")
 
  

carpeta = r"C:\Users\jacel\OneDrive\Documents\GitHub\P3_SofiaEstrada_Mar-aJos-Acelas\datos\datos\PPMI\3128\MPRAGE_GRAPPA"
loader= DicomLoader(carpeta)
volumen= loader.load()
#loader.mostrar_cortes()  
#estudio = EstudioImaginologico(carpeta, volumen)
#estudio.mostrar_info()
gestor = GestionImagenes(volumen)
#tipo_corte = "axial"
#indice = 100  # puedes probar otros números dentro del rango
#tipo_binarizacion = "tozero"  # o "truncado", "tozero", etc.

#corte = gestor.obtener_corte(tipo_corte, indice)
#gestor.segmentar(corte, tipo_binarizacion)
#gestor.zoom_y_recorte(nombre_archivo="recorte_prueba")
corte = gestor.obtener_corte("coronal", 100)
gestor.aplicar_morfologia(corte, operacion="erode", kernel_size=10, nombre_salida="resultado_open.png")


convertir_a_nifti(carpeta, "paciente3128.nii")
                



       
