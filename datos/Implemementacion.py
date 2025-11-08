# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 14:35:49 2025

@author: Sofia
"""

import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os

def normalizar(img):
    img = img.astype(np.float32)
    min_val, max_val = np.min(img), np.max(img)
    if max_val == min_val:
        return np.zeros_like(img, dtype=np.uint8)
    img = (img - min_val) / (max_val - min_val) * 255
    return img.astype(np.uint8)

class ArchivosDICOM:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.slices = []
        self.volumen = None
        self.pixel_spacing = None
        self.slice_thickness = None

    def leer_archivos(self):
        archivos = [f for f in os.listdir(self.carpeta) if not f.startswith('.')]
        slices = []
        for archivo in archivos:
            path = os.path.join(self.carpeta, archivo)
            try:
                ds = pydicom.dcmread(path)
                if hasattr(ds, 'pixel_array'):
                    slices.append(ds)
            except:
                pass

        if not slices:
            raise ValueError("No se encontraron archivos DICOM válidos.")

        # Ordenar por coordenada Z real
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        self.slices = slices

        # Obtener espaciamientos físicos
        self.pixel_spacing = [float(x) for x in slices[0].PixelSpacing]
        self.slice_thickness = float(slices[0].SliceThickness)

    def reconstruir_3D(self):
        self.leer_archivos()
        imagenes = []
        for s in self.slices:
            arr = s.pixel_array.astype(np.float32)
            slope = getattr(s, "RescaleSlope", 1)
            intercept = getattr(s, "RescaleIntercept", 0)
            arr = arr * slope + intercept
            imagenes.append(arr)
        self.volumen = np.stack(imagenes, axis=0)
        print(f"Volumen reconstruido con forma: {self.volumen.shape}")
        return self.volumen

    def mostrar_cortes(self):
        if self.volumen is None:
            print("Primero reconstruye el volumen.")
            return

        vol = self.volumen
        z, y, x = vol.shape

        # Cortes centrales
        corte_trans = normalizar(vol[z//2, :, :])
        corte_coronal = normalizar(vol[:, y//2, :])
        corte_sagital = normalizar(vol[:, :, x//2])

        # Proporciones físicas (mm)
        aspect_z = self.slice_thickness / self.pixel_spacing[0]

        plt.figure(figsize=(15, 5))

        plt.subplot(131)
        plt.imshow(corte_sagital[:,128], cmap='gray', aspect=aspect_z)
        plt.title("Corte Sagital")

        plt.subplot(132)
        plt.imshow(corte_trans[:,128], cmap='gray')
        plt.title("Corte Transversal")

        plt.subplot(133)
        plt.imshow(corte_coronal[:,:,128], cmap='gray', aspect=aspect_z)
        plt.title("Corte Coronal")

        plt.tight_layout()
        plt.show()
carpeta = r"datos\PPMI\3128\MPRAGE_GRAPPA"
gestor = ArchivosDICOM(carpeta)
gestor.reconstruir_3D()
gestor.mostrar_cortes()