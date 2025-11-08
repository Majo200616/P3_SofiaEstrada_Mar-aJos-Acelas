import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt

class EstudioImagenologico:
    def __init__(self, volumen, datasets):
       
        # Guardamos el volumen y los datasets para acceso futuro
        self.volumen = volumen
        self.datasets = datasets

        # Atributos 
        self.study_date = None
        self.study_time = None
        self.modality = None
        self.description = None
        self.series_time = None
       
