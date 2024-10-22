# src/ui/mostrar_reporte.py

import streamlit as st
import matplotlib.pyplot as plt


def mostrar_reporte(mapped_result_primary, mapped_result_secondary_masas=None, mapped_result_secondary_calcifi=None):
    """
    Genera y muestra un reporte basado en los resultados de la clasificación de la mamografía.

    :param mapped_result_primary: Resultado de la clasificación primaria.
    :param mapped_result_secondary_masas: Resultado de la clasificación secundaria para masas (opcional).
    :param mapped_result_secondary_calcifi: Resultado de la clasificación secundaria para calcificaciones (opcional).
    """
    st.header("Reporte de Clasificación de Mamografías")

    st.subheader("Resultados de la Clasificación Primaria")
    if mapped_result_primary:
        st.write(f"**{mapped_result_primary['label'].capitalize()}**: {mapped_result_primary['score'] * 100:.2f}%")
    else:
        st.write("No se obtuvieron resultados de la clasificación primaria.")

    if mapped_result_primary and mapped_result_primary['label'] == 'masas' and mapped_result_secondary_masas:
        st.subheader("Resultados de la Clasificación Secundaria para Masas")
        st.write(
            f"**{mapped_result_secondary_masas['label'].capitalize()}**: {mapped_result_secondary_masas['score'] * 100:.2f}%")

    if mapped_result_primary and mapped_result_primary[
        'label'] == 'calcificaciones' and mapped_result_secondary_calcifi:
        st.subheader("Resultados de la Clasificación Secundaria para Calcificaciones")
        st.write(
            f"**{mapped_result_secondary_calcifi['label'].capitalize()}**: {mapped_result_secondary_calcifi['score'] * 100:.2f}%")

    st.markdown("---")  # Separador

    st.subheader("Distribución de Resultados")
    labels = []
    scores = []

    # Datos para la clasificación primaria
    if mapped_result_primary:
        labels.append(mapped_result_primary['label'].capitalize())
        scores.append(mapped_result_primary['score'] * 100)

    # Datos para la clasificación secundaria
    if mapped_result_secondary_masas:
        labels.append(mapped_result_secondary_masas['label'].capitalize())
        scores.append(mapped_result_secondary_masas['score'] * 100)

    if mapped_result_secondary_calcifi:
        labels.append(mapped_result_secondary_calcifi['label'].capitalize())
        scores.append(mapped_result_secondary_calcifi['score'] * 100)

    if labels and scores:
        fig, ax = plt.subplots()
        ax.bar(labels, scores, color=['#4CAF50', '#FF9800', '#F44336'])
        ax.set_ylabel('Puntuación (%)')
        ax.set_title('Distribución de Resultados de Clasificación')
        for i, v in enumerate(scores):
            ax.text(i, v + 1, f"{v:.2f}%", ha='center')
        st.pyplot(fig)
    else:
        st.write("No hay datos suficientes para mostrar la distribución de resultados.")

    st.markdown("---")  # Separador

    st.subheader("Detalles Adicionales")
    # Aquí puedes añadir más información relevante, como gráficos, tablas, etc.
    st.write("### Análisis Adicional")
    st.write("Esta sección puede incluir análisis más detallados, gráficos de precisión, tablas resumen, etc.")

    st.markdown("---")  # Separador

    st.subheader("Conclusiones")
    st.write("### Conclusiones del Reporte")
    st.write("Basado en los resultados de la clasificación, se pueden extraer las siguientes conclusiones:")
    st.write("- **Etiqueta Principal:** Detalles sobre la etiqueta principal clasificada.")
    st.write("- **Etiqueta Secundaria:** Detalles sobre la etiqueta secundaria clasificada.")
    st.write("- **Recomendaciones:** Sugerencias basadas en la clasificación obtenida.")

    st.markdown("---")  # Separador

    st.subheader("Información Adicional")
    st.write("### Información Relevante")
    st.write("Puedes incluir cualquier información adicional que consideres importante para el reporte.")
