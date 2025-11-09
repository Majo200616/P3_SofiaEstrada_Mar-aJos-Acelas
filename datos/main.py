# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 18:15:42 2025

@author: Sofia
"""

import Implemementacion

def main():
    print("=== SISTEMA DE GESTIÓN DE IMÁGENES MÉDICAS ===")
    carpeta = input("Ingrese la ruta de la carpeta DICOM: ").strip()
    # Limpia espacios o saltos de línea del input

    # Crear el cargador
    loader = Implemementacion.DicomLoader(carpeta)
    volumen = loader.load()
    loader.mostrar_cortes()

    # Crear el estudio
    estudio = Implemementacion.EstudioImaginologico(carpeta, volumen)

    # Crear el gestor de imágenes
    gestor = Implemementacion.GestionImagenes(volumen, carpeta)

    # Registrar objetos
    gestor_objetos = Implemementacion.GestorObjetos()
    gestor_objetos.registrar("loader", loader)
    gestor_objetos.registrar("estudio", estudio)
    gestor_objetos.registrar("gestor", gestor)

    # Mostrar menú principal
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Ver información del estudio")
        print("2. Segmentación")
        print("3. Transformación morfológica")
        print("4. Recorte y zoom")
        print("5. Convertir a NIfTI")
        print("6. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            estudio.mostrar_info()
            input("\nPresione Enter para volver al menú")

        elif opcion == "2":
            tipo = input("Tipo de corte (transversal/coronal/sagital): ")
            indice = int(input("Índice del corte: "))
            tipo_bin = input("Tipo de binarización (binario/binario_inv/truncado/tozero/tozero_inv): ")
            nombre = input("Nombre para guardar el archivo: ")
            corte = gestor.obtener_corte(tipo, indice)
            gestor.segmentar(corte, tipo_bin, nombre)

        elif opcion == "3":
            tipo = input("Tipo de corte (transversal(x)/coronal(y)/sagital(z)): ")
            indice = int(input("Índice del corte: "))
            operacion = input("Operación (erode/dilate/open/close): ")
            kernel = int(input("Tamaño del kernel: "))
            nombre = input("Nombre para guardar el archivo: ")
            gestor.transformacion_morfologica(tipo, indice, operacion, kernel, nombre)

        elif opcion == "4":
            nombre = input("Nombre para guardar el recorte: ")
            gestor.zoom_y_recorte(nombre_archivo=nombre)
            print("Archivo guardado exitosamente")

        elif opcion == "5":
            nombre = input("Nombre del archivo NIfTI (sin extensión): ")
            gestor.convertir_a_nifti(nombre + ".nii")
            print("Archivo guardado exitosamente")

        elif opcion == "6":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida.")
            
if __name__ == "__main__":
    main()