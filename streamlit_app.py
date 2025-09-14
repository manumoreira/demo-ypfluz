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
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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
logo_path = get_resource_path("img/logo.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=500)  # Adjust width as needed
else:
    st.write("🏢 YPF Luz Dashboard")  # Fallback if image not found

# Warning message
st.warning("⚠️ Este Dashboard contiene información aleatoria a modo ilustrativo. \n El dashboard a entregar va a contener la información y los filtros acordados con el cliente.")

"" 
""  # Add some space.

cols = st.columns([1, 3])

# Available charts - you can add more as you create CSV files
AVAILABLE_CHARTS = [
    "importancia_energia",
    "importancia_renovables",
    "conocimiento_espontaneo",
    "conocimiento_guiado",
    "tipo_energia"
    # Add more chart files here as you create them
]

# Chart display names for better UI
CHART_DISPLAY_NAMES = {
    "importancia_energia": "Importancia Energía",
    "importancia_renovables": "Importancia Energías Renovables",
    "conocimiento_espontaneo": "Conocimiento de la marca TOP OF MIND",
    "conocimiento_guiado": "Conocimiento total de marcas guiado",
    "tipo_energia": "Tipo de energia renovable que provee YPF Luz (Espontáneo)"
    # Add display names for your charts
}

CHART_TYPES = {
       "importancia_energia": "pie",        # categorical data -> pie chart
       "importancia_renovables": "stacked_bar",     # multiple categories -> stacked bar
       "conocimiento_espontaneo": "grouped_bar",
       "conocimiento_guiado": "grouped_bar",
       "tipo_energia": "grouped_bar"
}


top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

selected_charts = AVAILABLE_CHARTS

# Wave comparison selector
WAVES = ["Ola1", "Ola2"]

RUBROS = [
     "Total",
    "Mineria",           # Not "Minería"
    "Agroindustria", 
    "Quimica",           # Not "Química"
    "Tecnologia",        # Not "Tecnología" 
    "Transporte",
    "Salud",
    "Renovables"
]

# Update the CHART_DISPLAY_NAMES for rubros if you want full names in the UI
RUBRO_DISPLAY_NAMES = {
    "Total": "Total",
    "Mineria": "Minería/ Metalmecánica",
    "Agroindustria": "Agroindustria/ Alimentación y bebidas",
    "Quimica": "Industria Química / Petroquímica / Plástico",
    "Tecnologia": "Tecnología de datos / telecomunicaciones / Economía del conocimiento",
    "Transporte": "Transporte / logística",
    "Salud": "Salud / Laboratorios",
    "Renovables": "Productos / Servicios para Energías renovables"
}

with top_left_cell:
    # Buttons for picking waves to compare
    selected_waves = st.multiselect(
        "Olas a comparar",
        options=WAVES,
        default=WAVES,
    )
    
    # Rubro selector with display names
    selected_rubros = st.multiselect(
        "Rubros a mostrar",
        options=list(RUBRO_DISPLAY_NAMES.keys()),  # Use short keys for filtering
        default=["Total"],  # Default to Total only
        format_func=lambda x: RUBRO_DISPLAY_NAMES[x],  # Display full names
        help="Selecciona los rubros/industrias a incluir en el análisis"
    )
if not selected_waves or not selected_rubros:
    if not selected_waves:
        top_left_cell.warning("Selecciona al menos una ola para comparar", icon=":material/warning:")
    if not selected_rubros:
        top_left_cell.warning("Selecciona al menos un rubro para mostrar", icon=":material/warning:")
    st.stop()

right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

@st.cache_resource(show_spinner=False)
def load_data(chart_name):
    """Load specific chart data from CSV"""
    csv_path = get_resource_path(f"data/{chart_name}.csv")
    try:
        data = pd.read_csv(csv_path)
        if data.empty:
            raise RuntimeError(f"CSV file {chart_name} is empty.")
        return data
    except FileNotFoundError:
        raise RuntimeError(f"Chart file not found: {chart_name}")
    except Exception as e:
        raise RuntimeError(f"Error loading {chart_name}: {str(e)}")

def process_survey_data(data, selected_waves, selected_rubros=None):
    """Process survey data with Wave_Rubro column format (Option 2)"""
    
    if data.empty or len(data.columns) < 2:
        return None
    
    # Get the category column (first column)
    category_col = data.columns[0]
    
    # Get all data columns (skip the first category column)
    data_columns = data.columns[1:].tolist()
    
    # Melt the data to convert from wide to long format
    melted_data = pd.melt(data, 
                         id_vars=[category_col], 
                         value_vars=data_columns,
                         var_name='Wave_Rubro', 
                         value_name='Value')
    
    # Split the Wave_Rubro column into separate Wave and Rubro columns
    # Handle cases where there might be underscores in the rubro names
    split_data = melted_data['Wave_Rubro'].str.split('_', n=1, expand=True)
    melted_data['Wave'] = split_data[0]
    melted_data['Rubro'] = split_data[1]
    
    # Clean up column names
    melted_data = melted_data.rename(columns={category_col: 'Category'})
    melted_data = melted_data.drop('Wave_Rubro', axis=1)
    
    # Clean up the values - remove percentage signs and convert to float
    melted_data['Value'] = melted_data['Value'].astype(str)
    melted_data['Value'] = melted_data['Value'].str.replace('%', '').str.strip()
    
    # Convert to numeric, handling any errors
    melted_data['Value'] = pd.to_numeric(melted_data['Value'], errors='coerce')
    
    # Remove rows with missing or invalid data
    melted_data = melted_data.dropna()
    
    # Filter by selected waves
    if selected_waves:
        melted_data = melted_data[melted_data['Wave'].isin(selected_waves)]
    
    # Filter by selected rubros (if specified)
    if selected_rubros:
        melted_data = melted_data[melted_data['Rubro'].isin(selected_rubros)]
    
    # Remove empty categories or percentage total rows
    melted_data = melted_data[
        (melted_data['Category'].notna()) & 
        (melted_data['Category'].str.strip() != '') &
        (~melted_data['Category'].str.contains('%', na=False))
    ]
    
    return melted_data if not melted_data.empty else None

# Update your RUBROS list to match the column naming in your CSV
# Make sure these match exactly what comes after the underscore in your columns

# ADD THIS FUNCTION RIGHT HERE:
def create_chart(chart_name, data, chart_type, show_rubro_legend=True):
    """Create appropriate chart based on chart type"""
    chart_title = CHART_DISPLAY_NAMES.get(chart_name, chart_name)
    
    if chart_type == "pie":
        # NEW: Create side-by-side pie charts for each wave
        unique_waves = sorted(data['Wave'].unique())
        
        if len(unique_waves) == 1:
            # Single wave - show one pie chart
            wave = unique_waves[0]
            pie_data = data[data['Wave'] == wave].copy()
            
            chart = alt.Chart(pie_data).mark_arc(
                outerRadius=120,
                innerRadius=50,
                stroke="#fff"
            ).encode(
                theta=alt.Theta("Value:Q"),
                color=alt.Color("Category:N", 
                              scale=alt.Scale(scheme='category10'),
                              legend=alt.Legend(orient="right")),
                tooltip=['Category:N', 'Value:Q', 'Wave:N']
            ).properties(
                title=f"{chart_title} ({wave})",
                height=400,
                width=400
            )
        else:
    # Multiple waves - create individual pie charts and concatenate horizontally
            charts = []
            
            for i, wave in enumerate(unique_waves):
                wave_data = data[data['Wave'] == wave].copy()
                
                # Show legend only on the last chart
                show_legend = (i == len(unique_waves) - 1)
                
                pie_chart = alt.Chart(wave_data).mark_arc(
                    outerRadius=100,
                    innerRadius=40,
                    stroke="#fff",
                    strokeWidth=2
                ).encode(
                    theta=alt.Theta("Value:Q"),
                    color=alt.Color("Category:N", 
                                scale=alt.Scale(scheme='category10'),
                                legend=alt.Legend(
                                    orient="right",
                                    title="Categorías"
                                ) if show_legend else None),
                    tooltip=['Category:N', 'Value:Q', 'Wave:N']
                ).properties(
                    title=f"Ola {wave}",
                    height=350,
                    width=450  # Your adjusted width
                )
                
                charts.append(pie_chart)
            
            # Concatenate charts horizontally with spacing
            chart = alt.hconcat(*charts, spacing=40).resolve_scale(
                color='shared'  # Ensures same colors for same categories
            ).properties(
                title=chart_title
            )
            
    elif chart_type == "stacked_bar":
        # Stacked bar chart (unchanged)
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
        # Grouped/clustered bar chart (unchanged)
        chart = alt.Chart(data).mark_bar(
            opacity=0.8
        ).encode(
            x=alt.X('Category:N', title='Categoría'),
            y=alt.Y('Value:Q', title='Porcentaje (%)'),
            color=alt.Color('Wave:N', title='Ola', scale=alt.Scale(scheme='category10')),
            xOffset=alt.XOffset('Wave:N'),
            tooltip=['Category:N', 'Wave:N', 'Value:Q']
        ).properties(
            title=chart_title,
            height=400
        ).resolve_scale(
            x='independent'
        )
        
    else:  # default bar chart (unchanged)
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
        
        processed_main_data = process_survey_data(main_chart_data, selected_waves, selected_rubros)
        
        if processed_main_data is not None and not processed_main_data.empty:
            with right_cell:
                chart_type = CHART_TYPES.get(selected_charts[0], "bar")
                st.write(f"Chart type: {chart_type}")  # Debug line
                chart = create_chart(selected_charts[0], processed_main_data, chart_type, show_rubro_legend=len(selected_rubros) > 1)
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
# Fixed version of the individual charts section
if len(selected_charts) > 1:
    """
    ## Análisis Individual de Gráficos
    
    Comparación detallada entre olas para cada indicador seleccionado.
    """

    NUM_COLS = 2
    chart_cols = st.columns(NUM_COLS)

    for i, chart_name in enumerate(selected_charts[1:], 1):  # Skip first chart (already shown above)
        try:
            # FIX: Load the specific chart data, not main_chart_data
            chart_data = load_data(chart_name)
            
            # FIX: Process the specific chart_data, not main_chart_data
            processed_data = process_survey_data(chart_data, selected_waves, selected_rubros)
            
            if processed_data is not None and not processed_data.empty:
                # FIX: Use the correct chart_name and processed_data
                chart_type = CHART_TYPES.get(chart_name, "bar")
                chart = create_chart(chart_name, processed_data, chart_type, show_rubro_legend=len(selected_rubros) > 1)
                
                cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
                cell.altair_chart(chart, use_container_width=True)
            else:
                cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
                cell.warning(f"No se pudieron procesar los datos para {chart_name}")
                
        except Exception as e:
            cell = chart_cols[(i-1) % NUM_COLS].container(border=True)
            cell.error(f"Error loading {chart_name}: {str(e)}")
            cell.exception(e)

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