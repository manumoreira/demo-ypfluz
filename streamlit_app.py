# -*- coding: utf-8 -*-
# Copyright 2024-2025 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(
    page_title="Dashboard Monitor de Marca YPF Luz",
    page_icon="img/logo.png",
    layout="wide",
)

"""
# Dashboard Monitor de Marca YPF Luz

Navega los indicadores más importantes del estudio de mercado.
"""

# Display the custom logo image
st.image("img/logo.png", width=100)  # Adjust width as needed

"" 
""  # Add some space.

cols = st.columns([1, 3])

# Available charts - you can add more as you create CSV files
AVAILABLE_CHARTS = [
    "importancia_energia",
    "importancia_renovables",
    "conocimiento_espontaneo",
    "conocimiento_guiado",
    # Add more chart files here as you create them
]

# Chart display names for better UI
CHART_DISPLAY_NAMES = {
    "importancia_energia": "Importancia Energía",
    "importancia_renovables": "Importancia Energías Renovables",
    "conocimiento_espontaneo": "Conocimiento de la marca TOP OF MIND",
    "conocimiento_guiado": "Conocimiento total de marcas guiado"
    # Add display names for your charts
}

CHART_TYPES = {
       "importancia_energia": "pie",        # categorical data -> pie chart
       "importancia_renovables": "stacked_bar",     # multiple categories -> stacked bar
       "conocimiento_espontaneo": "grouped_bar",
       "conocimiento_guiado": "grouped_bar",
}


top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

selected_charts = AVAILABLE_CHARTS

# Wave comparison selector
WAVES = ["Ola 1", "Ola 2"]

with top_left_cell:
    # Buttons for picking waves to compare
    selected_waves = st.multiselect(
        "Ondas a comparar",
        options=WAVES,
        default=WAVES,
    )

if not selected_waves:
    top_left_cell.warning("Selecciona al menos una ola para comparar", icon=":material/warning:")
    st.stop()

right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

@st.cache_resource(show_spinner=False)
def load_data(chart_name):
    """Load specific chart data from CSV"""
    csv_path = f"data/{chart_name}.csv"
    try:
        data = pd.read_csv(csv_path)
        if data.empty:
            raise RuntimeError(f"CSV file {chart_name} is empty.")
        return data
    except FileNotFoundError:
        raise RuntimeError(f"Chart file not found: {chart_name}")
    except Exception as e:
        raise RuntimeError(f"Error loading {chart_name}: {str(e)}")

def process_survey_data(data, selected_waves):
    """Process survey data for visualization"""
    # Ensure we only include selected waves
    available_waves = [col for col in data.columns if col in selected_waves and col != data.columns[0]]
    
    if not available_waves:
        return None
    
    # Create processed data with category and wave values
    processed_data = []
    category_col = data.columns[0]  # First column is category
    
    for _, row in data.iterrows():
        category = row[category_col]
        if pd.isna(category) or category == "":
            continue
            
        for wave in available_waves:
            if wave in data.columns and not pd.isna(row[wave]):
                value = row[wave]
                # Clean percentage values
                if isinstance(value, str) and '%' in value:
                    try:
                        value = float(value.replace('%', ''))
                    except ValueError:
                        continue
                elif isinstance(value, (int, float)):
                    value = float(value)
                else:
                    continue
                    
                processed_data.append({
                    'Category': category,
                    'Wave': wave,
                    'Value': value
                })
    
    return pd.DataFrame(processed_data) if processed_data else None

# ADD THIS FUNCTION RIGHT HERE:
def create_chart(chart_name, data, chart_type):
    """Create appropriate chart based on chart type"""
    chart_title = CHART_DISPLAY_NAMES.get(chart_name, chart_name)
    
    if chart_type == "pie":
        # Pie chart - use only latest wave (Ola 2) for single pie
        latest_wave = "Ola 2" if "Ola 2" in data['Wave'].values else data['Wave'].iloc[0]
        pie_data = data[data['Wave'] == latest_wave].copy()
        
        chart = alt.Chart(pie_data).mark_arc(
            outerRadius=120,
            innerRadius=50,
            stroke="#fff"
        ).encode(
            theta=alt.Theta("Value:Q"),
            color=alt.Color("Category:N", 
                          scale=alt.Scale(scheme='category10'),
                          legend=alt.Legend(orient="right")),
            tooltip=['Category:N', 'Value:Q']
        ).properties(
            title=f"{chart_title} ({latest_wave})",
            height=400
        )
        
    elif chart_type == "stacked_bar":
        # Stacked bar chart
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X('Wave:N', title='Ola'),
            y=alt.Y('Value:Q', title='Porcentaje (%)'),
            color=alt.Color('Category:N', 
                          scale=alt.Scale(scheme='category10'),
                          legend=alt.Legend(orient="right")),
            tooltip=['Category:N', 'Wave:N', 'Value:Q']
        ).properties(
            title=chart_title,
            height=400
        )
    elif chart_type == "grouped_bar":
        # Grouped/clustered bar chart - shows separate bars for each wave within each category
        chart = alt.Chart(data).mark_bar(
            opacity=0.8
        ).encode(
            x=alt.X('Category:N', title='Categoría'),
            y=alt.Y('Value:Q', title='Porcentaje (%)'),
            color=alt.Color('Wave:N', title='Ola', scale=alt.Scale(scheme='category10')),
            xOffset=alt.XOffset('Wave:N'),  # This creates the grouping effect
            tooltip=['Category:N', 'Wave:N', 'Value:Q']
        ).properties(
            title=chart_title,
            height=400
        ).resolve_scale(
            x='independent'
        )
        
    else:  # default bar chart
        chart = alt.Chart(data).mark_bar(
            opacity=0.8
        ).encode(
            x=alt.X('Category:N', title='Categoría'),
            y=alt.Y('Value:Q', title='Porcentaje (%)'),
            color=alt.Color('Wave:N', title='Ola', scale=alt.Scale(scheme='category10')),
            tooltip=['Category:N', 'Wave:N', 'Value:Q']
        ).properties(
            title=chart_title,
            height=400
        )
    
    return chart

# Load and display the first chart in the main area
if selected_charts:
    try:
        main_chart_data = load_data(selected_charts[0])
        
        processed_main_data = process_survey_data(main_chart_data, selected_waves)
        
        if processed_main_data is not None and not processed_main_data.empty:
            with right_cell:
                chart_type = CHART_TYPES.get(selected_charts[0], "bar")
                st.write(f"Chart type: {chart_type}")  # Debug line
                chart = create_chart(selected_charts[0], processed_main_data, chart_type)
                st.altair_chart(chart, use_container_width=True)
        else:
            right_cell.warning(f"No se pudieron procesar los datos para {selected_charts[0]}")
            
    except Exception as e:
        right_cell.error(f"Error loading main chart: {str(e)}")
        st.exception(e)  # This will show the full error traceback

# Summary metrics
bottom_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)


""
""

# Display individual charts for all selected charts
if len(selected_charts) > 1:
    """
    ## Análisis Individual de Gráficos
    
    Comparación detallada entre olas para cada indicador seleccionado.
    """

    NUM_COLS = 2
    chart_cols = st.columns(NUM_COLS)

    for i, chart_name in enumerate(selected_charts[1:], 1):  # Skip first chart (already shown above)
        try:
            chart_data = load_data(chart_name)
            processed_data = process_survey_data(chart_data, selected_waves)
            
            if processed_data is not None and not processed_data.empty:
                chart_type = CHART_TYPES.get(chart_name, "bar")
                chart = create_chart(chart_name, processed_data, chart_type)
                
                cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
                cell.altair_chart(chart, use_container_width=True)
            else:
                cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
                cell.warning(f"No se pudieron procesar los datos para {chart_name}")
                
        except Exception as e:
            cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
            cell.error(f"Error loading {chart_name}: {str(e)}")
            cell.exception(e)  # Show full error for debugging

""
""

## Datos en Bruto

# Show raw data for selected charts
#for chart_name in selected_charts:
#    try:
#        chart_data = load_data(chart_name)
#        chart_title = CHART_DISPLAY_NAMES.get(chart_name, chart_name)
#        st.subheader(f"Datos: {chart_title}")
#        st.dataframe(chart_data, use_container_width=True)
#    except Exception as e:
#        st.error(f"Error loading data for {chart_name}: {str(e)}")