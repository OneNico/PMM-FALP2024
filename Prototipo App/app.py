# app.py
# Archivo principal que lanza la app en Streamlit

import streamlit as st
from src.modulos.gestion_dicom import gestionar_dicom
from src.modulos.procesamiento_i import procesamiento_individual
from src.modulos.procesamiento_m import procesamiento_masivo
from src.ui.visual import main  # Importa la función correcta


if __name__ == "__main__":
        main()


