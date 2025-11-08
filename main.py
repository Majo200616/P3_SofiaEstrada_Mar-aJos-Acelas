import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt

class DicomLoader:
    def _init_(self, folder_path):
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

class EstudioImaginologico:
    def __init__(self, patient_name, patient_id, study_date, study_time, modality, study_description):
        self.patient_name = patient_name
        self.patient_id = patient_id
        self.study_date = study_date
        self.study_time = study_time
        self.modality = modality
        self.study_description = study_description

    def mostrar_info(self):
        print("Información del Estudio Imaginológico DICOM:")
        print(f"Nombre del Paciente:     {self.patient_name}")
        print(f"ID del Paciente:         {self.patient_id}")
        print(f"Fecha del Estudio:       {self.study_date}")
        print(f"Hora del Estudio:        {self.study_time}")
        print(f"Modalidad:               {self.modality}")
        print(f"Descripción del Estudio: {self.study_description}")

    




       
