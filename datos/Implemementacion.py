# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 14:35:49 2025

@author: Sofia
"""

import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os

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


    
    
carpeta = r"datos\PPMI\3128\MPRAGE_GRAPPA"
loader= DicomLoader(carpeta)
volumen= loader.load()
loader.mostrar_cortes()  
estudio = EstudioImaginologico(carpeta, volumen)
estudio.mostrar_info()