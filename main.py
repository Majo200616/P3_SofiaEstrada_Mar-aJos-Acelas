import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt

class EstudioImaginologico:
    def __init__(self, patient_name, patient_id, study_date, study_time, modality, study_description):
        self.patient_name = patient_name
        self.patient_id = patient_id
        self.study_date = study_date
        self.study_time = study_time
        self.modality = modality
        self.study_description = study_description

    def mostrar_info(self):
        print("----- Información del Estudio Imaginológico -----")
        print(f"Nombre del Paciente:     {self.patient_name}")
        print(f"ID del Paciente:         {self.patient_id}")
        print(f"Fecha del Estudio:       {self.study_date}")
        print(f"Hora del Estudio:        {self.study_time}")
        print(f"Modalidad:               {self.modality}")
        print(f"Descripción del Estudio: {self.study_description}")



        
       
