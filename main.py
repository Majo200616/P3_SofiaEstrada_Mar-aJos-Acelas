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

# Clase para mostrar la información del estudio DICOM
class EstudioImaginologico:
    def __init__(self, folder_path):
        """Lee automáticamente los metadatos DICOM desde la carpeta"""
        self.folder_path = folder_path  # Guarda la ruta del estudio
        
        # Tomar el primer archivo DICOM de la carpeta
        primer_archivo = [f for f in os.listdir(folder_path) if f.lower().endswith('.dcm')][0]
        ruta_archivo = os.path.join(folder_path, primer_archivo)
        
        # Cargar ese archivo usando pydicom
        ds = pydicom.dcmread(ruta_archivo)
        
        # Extraer automáticamente los atributos DICOM con seguridad
        self.study_date = getattr(ds, "StudyDate", None)
        self.study_time = getattr(ds, "StudyTime", None)
        self.modality = getattr(ds, "Modality", None)
        self.study_description = getattr(ds, "StudyDescription", None)
        self.series_time = getattr(ds, "SeriesTime", None)

    def mostrar_info(self):
        """Muestra la información general del estudio DICOM"""
        print("\nInformación del Estudio Imaginológico DICOM:")
        print(f"Fecha del Estudio:       {self.study_date}")
        print(f"Hora del Estudio:        {self.study_time}")
        print(f"Modalidad:               {self.modality}")
        print(f"Descripción del Estudio: {self.study_description}")
        print(f"Hora de la Serie:        {self.series_time}")



# Crear e imprimir la información del estudio
estudio = EstudioImaginologico(carpeta)  # Crear el estudio leyendo la carpeta automáticamente
estudio.mostrar_info()                   # Mostrar la información leída desde el DICOM

    




       
