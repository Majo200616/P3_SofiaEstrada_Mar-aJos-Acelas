# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 14:35:49 2025

@author: Sofia
"""

import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import cv2
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
      plt.subplot(131)
      plt.imshow(self.volume[z, :, :], cmap='gray')
      plt.title('Transversal (XY)')
      plt.axis('off')

      # Corte coronal (XZ)
      plt.subplot(132)
      plt.imshow(self.volume[:, y, :], cmap='gray')
      plt.title('Coronal (XZ)')
      plt.axis('off')

      # Corte sagital (YZ)
      plt.subplot(133)
      plt.imshow(self.volume[:, :, x], cmap='gray')
      plt.title('Sagital (YZ)')
      plt.axis('off')

      plt.tight_layout()
      plt.show()

      
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
        t1 = datetime.strptime(self.study_time.split('.')[0], "%H%M%S")
        t2 = datetime.strptime(self.series_time.split('.')[0], "%H%M%S")
        duracion = t2 - t1
        return duracion

    def mostrar_info(self):
        """Muestra la información general del estudio"""
        print("\nInformación del Estudio Imaginológico DICOM:")
        print(f"Fecha del Estudio: {self.study_date}")
        print(f"Hora del Estudio: {self.study_time}")
        print(f"Modalidad: {self.modality}")
        print(f"Descripción del Estudio: {self.study_description}")
        print(f"Hora de la Serie: {self.series_time}")
        print(f"Duración: {self.duracion}")
        print(f"Forma del volumen: {self.volume.shape}")

class GestionImagenes:
    
    def __init__(self, volume, carpeta):
        self.volume = volume
        self.carpeta= carpeta

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

    def segmentar(self, corte, tipo_binarizacion, nombre_archivo):
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
        cv2.imwrite(f"{nombre_archivo}.jpg", segmentada)
        print(f"Imagen segmentada guardada como {nombre_archivo}.jpg")

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
    
    def transformacion_morfologica(self, tipo_corte, indice, operacion, kernel_size=3, nombre_archivo=None):
        """
        Aplica una transformación morfológica (erode, dilate, open, close)
        sobre un corte del volumen, normaliza a uint8, muestra y guarda el resultado.
        """
        # Obtener el corte solicitado
        corte = self.obtener_corte(tipo_corte, indice)

        # Normalizar a uint8 para OpenCV
        img_uint8 = ((corte - np.min(corte)) / (np.max(corte) - np.min(corte)) * 255).astype(np.uint8)

        # Crear kernel cuadrado del tamaño indicado
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        # Elegir la operación
        if operacion == "erode":
            resultado = cv2.erode(img_uint8, kernel, iterations=1)
        elif operacion == "dilate":
            resultado = cv2.dilate(img_uint8, kernel, iterations=1)
        elif operacion == "open":
            resultado = cv2.morphologyEx(img_uint8, cv2.MORPH_OPEN, kernel)
        elif operacion == "close":
            resultado = cv2.morphologyEx(img_uint8, cv2.MORPH_CLOSE, kernel)
        else:
            raise ValueError("Operación morfológica no válida. Usa: 'erode', 'dilate', 'open' o 'close'.")

        # Mostrar imagen resultante
        plt.figure(figsize=(8, 4))
        plt.subplot(1, 2, 1)
        plt.imshow(img_uint8, cmap='gray')
        plt.title("Corte original")
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(resultado, cmap='gray')
        plt.title(f"Transformación: {operacion} (kernel={kernel_size})")
        plt.axis('off')
        plt.show()

        # Guardar imagen
      
        cv2.imwrite(f"{nombre_archivo}.png", resultado)
        print(f"Imagen guardada como {nombre_archivo}.png")

        return resultado
    
    def convertir_a_nifti(self, nombre_salida="resultado.nii"):
        """Convierte la carpeta DICOM asociada en un archivo NIfTI (.nii)."""
        archivos = [os.path.join(self.carpeta, f) for f in os.listdir(self.carpeta) if f.endswith(".dcm")]
        if not archivos:
            print("No se encontraron archivos DICOM en la carpeta.")
            return

        slices = [pydicom.dcmread(a) for a in archivos]
        slices.sort(key=lambda s: float(s.ImagePositionPatient[2]) if "ImagePositionPatient" in s else 0)
        volumen = np.stack([s.pixel_array for s in slices], axis=-1)

        try:
            pixel_spacing = slices[0].PixelSpacing
            slice_thickness = float(slices[0].SliceThickness)
        except:
            pixel_spacing = [1.0, 1.0]
            slice_thickness = 1.0

        affine = np.diag([pixel_spacing[0], pixel_spacing[1], slice_thickness, 1])
        nifti_img = nib.Nifti1Image(volumen, affine)
        nib.save(nifti_img, nombre_salida)
        print(f"Conversión completada. Archivo guardado como: {nombre_salida}")
    

class GestorObjetos:
    def __init__(self):
        self.objetos = {}

    def registrar(self, nombre, objeto):
        """Agrega o actualiza un objeto almacenado."""
        self.objetos[nombre] = objeto

    def obtener(self, nombre):
        """Devuelve un objeto almacenado por su nombre."""
        return self.objetos.get(nombre)

    def listar(self):
        """Devuelve una lista con los nombres de los objetos almacenados."""
        return list(self.objetos.keys())
    
carpeta = r"datos\PPMI\3128\MPRAGE_GRAPPA"

gestor_objetos = GestorObjetos()

loader= DicomLoader(carpeta)
gestor_objetos.registrar("loader", loader)

volumen= loader.load()
#loader.mostrar_cortes()  
estudio = EstudioImaginologico(carpeta, volumen)
gestor_objetos.registrar("estudio", estudio)
#estudio.mostrar_info()
gestor = GestionImagenes(volumen, carpeta)
gestor_objetos.registrar("gestor", gestor)

#tipo_corte = "axial"
#indice = 100  # puedes probar otros números dentro del rango
#tipo_binarizacion = "tozero"  # o "truncado", "tozero", etc.

#corte = gestor.obtener_corte(tipo_corte, indice)
#gestor.segmentar(corte, tipo_binarizacion)
#gestor.zoom_y_recorte(nombre_archivo="recorte_prueba")
"""gestor.transformacion_morfologica(
    tipo_corte="coronal",   # 'axial', 'coronal' o 'sagital'
    indice=100,           # número de corte
    operacion="erode",     # 'erode', 'dilate', 'open', 'close'
    kernel_size=10,        # tamaño que luego ingresará el usuario en el menú
    nombre_archivo="resultado_open"
)"""
gestor.convertir_a_nifti("archivo_nifti.nii")