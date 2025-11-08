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
    
carpeta = r"datos\PPMI\3128\MPRAGE_GRAPPA"
loader= DicomLoader(carpeta)
volumen= loader.load()
loader.mostrar_cortes()  