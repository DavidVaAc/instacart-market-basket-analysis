import streamlit as st
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
import seaborn as sns
import os
plt.style.use('dark_background')

# Configuración de la página
st.set_page_config(page_title="Instacart Insights Dashboard", layout="wide")

st.markdown(
    """
    <style>
    /* 1. Centrar todo el contenedor de la métrica */
    [data-testid="stMetric"] {
        width: fit-content;
        margin: auto;
    }

    /* 2. Centrar el Label (Título) */
    [data-testid="stMetricLabel"] > div {
        justify-content: center !important;
    }

    /* 3. Centrar el Valor (El número grande) */
    [data-testid="stMetricValue"] > div {
        justify-content: center !important;
    }

    /* 4. Centrar el Delta (La flecha y el porcentaje) */
    [data-testid="stMetricDelta"] > div {
        justify-content: center !important;
    }

    /* Forzar que el texto interno también se centre */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título y Contexto
st.title("🛒 Instacart Market Basket Analysis")
st.markdown("""
Esta aplicación interactiva presenta los hallazgos clave del análisis de comportamiento del consumidor.
*Explora las métricas de lealtad, tiempos de compra y la eficiencia del catálogo.*
""")

st.info("""### 📊 Resumen Ejecutivo: Consumer Insights & Market Basket Analysis

* **Contexto:** Este proyecto analiza un ecosistema masivo de datos transaccionales de Instacart (datos de 2017) para descifrar los patrones de compra y lealtad del usuario moderno. Este análisis transforma datos crudos de transacciones en inteligencia de negocio, identificando los motores de crecimiento y retención de la plataforma.

* **Objetivo Estratégico:** Extraer inteligencia empresarial mediante la identificación de ventanas críticas de demanda, segmentación de usuarios por tasa de retorno y optimización del mix de productos.

* **Insights de Alto Impacto:**

    1. ⏰ **Detección de Picos de Demanda:** Se identificaron ventanas críticas de saturación logística los domingos y lunes entre las 10:00 y 15:00 hrs.

    2. ⚡ **El Motor del Catálogo (Efecto Pareto)**: Existe una concentración masiva donde solo el 1.7% de los productos genera el 50% del volumen total de ventas. La operación depende de un núcleo de "Ultra-Alta Rotación".

    3. 🌿 **La Ventaja Orgánica:** El segmento orgánico domina el Top 20 de ventas y presenta una tasa de recompra significativamente superior al promedio. El consumidor valora la salud y la frescura por sobre el precio.

    4. ⏰ **Ciclos de Fidelidad Siete-Días:** El hábito de consumo es rítmico. El pico de pedidos ocurre en domingo/lunes y el tiempo de retorno más frecuente es de exactamente 7 días, lo que facilita la predicción de demanda y stock.
    
    5. 💎 **Usuarios VIP de Alto Valor:** Menos del 2% de los usuarios mueven el 10% de las transacciones. Estos clientes tienen una lealtad del 77%, lo que indica que su canasta básica está casi totalmente automatizada.

    6. 📥 **Intencionalidad "First-to-Cart":** Las bananas y los lácteos son los disparadores de la compra (lo primero que se añade al carrito). Son los productos "gancho" que inician el flujo de ingresos en cada sesión.
        """)

# Función para cargar datos (Usa @st.cache_data para que sea rápido)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_orders():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'instacart_orders.csv')
    orders = pd.read_csv(path, sep=';')
    return orders

@st.cache_data
def load_order_prod():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'order_products.csv')
    order_prods = pd.read_csv(path, sep=';')
    return order_prods

@st.cache_data
def load_products():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'products.csv')
    products = pd.read_csv(path, sep=';')
    return products

@st.cache_data
def load_departments():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'departments.csv')
    departments = pd.read_csv(path, sep=';')
    return departments

delta1 = "yellow" # Color para los deltas en las métricas
delta2 = "blue" # Color para los deltas en las métricas
delta3 = "violet" # Color para los deltas en las métricas
delta4 = "yellow" # Color para los deltas en las métricas

try:
    df_orders = load_orders()
    dias_dict = {0: 'Domingo', 1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado'}
    df_orders['order_dow'] = df_orders['order_dow'].replace(dias_dict)
    # --- SIDEBAR: Filtros ---
    dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

    # 1. Definimos el orden lógico para que los checkboxes no salgan alfabéticos

    st.sidebar.header("🛠️ Filtros de Análisis")
    st.sidebar.write("Selecciona los días para visualizar:")

    # 2. Lista para guardar los días que el usuario marque
    dias_seleccionados = []

    # 3. Creamos los checkboxes en el orden correcto
    for dia in dias:
        # Verificamos que el día exista en tus datos para evitar errores
        if dia in df_orders['order_dow'].unique():
         if st.sidebar.checkbox(dia, value=True, key=f"chk_{dia}"):
                dias_seleccionados.append(dia)

    # 4. Filtrado Dinámico
    if not dias_seleccionados:
        st.sidebar.error("⚠️ Selecciona al menos un día para mostrar resultados.")
        df_filtered = df_orders.head(0) # DataFrame vacío
    else:
        df_filtered = df_orders[df_orders['order_dow'].isin(dias_seleccionados)]

    st.sidebar.markdown("---")
    st.sidebar.write("Selecciona el Rango de Horario:")

    # Slider de rango para las 24 horas
    hora_inicio, hora_fin = st.sidebar.slider(
        "Rango de horas (00:00 - 23:00):",
        min_value=0,
        max_value=23,
        value=(0, 23) # Valor por defecto: de 0 AM a 11 PM
    )

    # Aplicar el segundo filtro al DataFrame ya filtrado por días
    df_filtered = df_filtered[
        (df_filtered['order_hour_of_day'] >= hora_inicio) & 
        (df_filtered['order_hour_of_day'] <= hora_fin)
    ]
    st.sidebar.markdown("---")

    # Filtro de Departamentos
    df_departments = load_departments()
    departments = st.sidebar.multiselect("Selecciona los departamentos:", 
                           options=sorted(df_departments['department'].unique()), 
                           default=sorted(df_departments['department'].unique())
                            )
    df_departments = df_departments[df_departments['department'].isin(departments)]

    # 1. Preparación de los datos (Top 20 Reordenados)
     
    df_products = load_products().merge(df_departments[['department_id', 'department']], on='department_id', how='inner')
    df_order_prod = load_order_prod().merge(df_products[['product_id', 'product_name', 'department']], on='product_id', how='inner')

    df_filtered = df_filtered[df_filtered['order_id'].isin(df_order_prod['order_id'].unique())]
    df_order_prod = df_order_prod.merge(df_filtered[['order_id','order_dow','order_hour_of_day', 'user_id']], on='order_id', how='inner')

    st.sidebar.markdown("---")
    with st.sidebar.expander("🔬 Nota Metodológica"):
        st.write("""
    **Enfoque Estadístico:**
    Este dashboard utiliza **análisis de densidad acumulada** para identificar el comportamiento asintótico del catálogo.
         
    * **Análisis de Densidad:** Identificación de comportamientos asintóticos en el catálogo de productos.    
    * **Segmentación de Fase:** Clasificación de lealtad basada en tasas de reincidencia por deciles de volumen.
    * **Efecto Pareto:** Modelado mediante distribuciones de frecuencia de pedidos.
    * **Dinámica Temporal:** Análisis de periodicidad en ciclos de reabastecimiento (7 días).
    * **Desarrollador:** David Valle Acosta (Físico, UNAM).
    """)


    st.divider()
    
    # --- ROW 2: Visualizaciones Temporales ---
    if not df_filtered.empty:

        st.header("⏳ Dinámicas Temporales")

        st.space()

        c1, c2 = st.columns(2)

        with c1:

            st.metric("Promedio Hora de Compra", f"{df_filtered['order_hour_of_day'].mean():.1f} hrs")

            # 1. Preparación de datos
            oders_by_hour = df_filtered.groupby('order_hour_of_day').size().reset_index(name='volumen')

            # 2. Extraer la paleta 'winter' de Seaborn para que Plotly la reconozca
            # Usamos 24 colores para representar las 24 horas del día
            winter_palette = sns.color_palette("winter", 24).as_hex()

            # 3. Crear la gráfica con Plotly Express
            fig_hours = px.bar(
                oders_by_hour, 
                x='order_hour_of_day', 
                y='volumen',
                color='volumen', # El color depende del volumen para el degradado
                color_continuous_scale=winter_palette,
                labels={'order_hour_of_day': 'Hora del día',
                        'volumen': 'Volumen de pedidos'},
                title='Distribución de pedidos por hora del día'.title()
            )

            # 4. Ajustes estéticos para que se vea "Pro" y combine con el modo oscuro
            fig_hours.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_color="white",
                                    showlegend=False,
                                    coloraxis_showscale=False, # Ocultamos la barra de escala de color lateral
                                    margin=dict(t=50, b=50, l=50, r=50)
                                    )

            fig_hours.update_xaxes(showgrid=False, tickmode='linear')
            fig_hours.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')

            # 5. Desplegar en Streamlit
            st.plotly_chart(fig_hours, use_container_width=True)

            st.info(""" Tras modelar el volumen de transacciones por hora, se identifica un comportamiento bimodal con una clara dominancia en el horario diurno. Los hallazgos principales son:

* ⚡ Meseta de Máxima Demanda (Picos Operativos): Se observa una ventana de alta intensidad entre las 09:00 y las 16:00 horas, con un volumen sostenido superior a los 35,000 pedidos. El pico máximo absoluto ocurre a las 10:00 AM, consolidándose como la hora crítica para la logística y disponibilidad de la plataforma.

* 🌅 Fase de Aceleración Matutina: A partir de las 07:00 AM, el sistema experimenta un incremento exponencial en la tasa de pedidos, marcando el inicio de la jornada operativa principal y sugiriendo un hábito de compra ligado al inicio de las actividades diarias de los usuarios.

* 📉 Desaceleración y Comportamiento Nocturno: Se detecta un descenso progresivo después de las 17:00 horas. La actividad durante la madrugada (00:00 - 06:00) es estadísticamente marginal, confirmando que el servicio tiene un uso casi exclusivamente diurno.

💡 Insight Estratégico: La concentración del 70% de la carga operativa en un bloque de 7 horas sugiere la necesidad de optimizar la asignación de repartidores y el soporte técnico durante este intervalo para mitigar posibles cuellos de botella.
            """)

        with c2:

            st.metric("Día Pico", f"{df_filtered['order_dow'].mode()[0]}")

            # 1. Preparación de los datos (manteniendo tu lógica de nombres de días)
            bar_insta_orders = df_filtered.groupby('order_dow').size().reset_index(name='volumen')
            nombres_dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

            # 2. Extraer la paleta 'cool' de Seaborn para Plotly
            # Usamos 7 colores, uno para cada día de la semana
            cool_palette = sns.color_palette("cool", 7).as_hex()

            # 3. Crear la gráfica con Plotly Express
            fig_dow = px.bar(
                bar_insta_orders,
                x='order_dow',
                y='volumen',
                color='volumen', # Aplicamos el degradado según el volumen
                color_continuous_scale=cool_palette,
                labels={
                    'order_dow': 'Día de la semana',
                    'volumen': 'Volumen de pedidos'
                        },
                title='Distribución de pedidos por día de la semana'.title()
                )

            # 4. Ajustes estéticos para modo oscuro y diseño limpio
            fig_dow.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                coloraxis_showscale=False, # Ocultamos la barra de color lateral
                showlegend=False,
                margin=dict(t=50, b=50, l=50, r=50)
            )

            # Aseguramos que los días aparezcan en el orden correcto (de Domingo a Sábado)
            fig_dow.update_xaxes(
                categoryorder='array', 
                categoryarray=nombres_dias,
                showgrid=False
            )

            fig_dow.update_yaxes(
                showgrid=True, 
                gridcolor='rgba(255,255,255,0.1)'
                )

            # 5. Desplegar en Streamlit
            st.plotly_chart(fig_dow, use_container_width=True)    

            st.info("""El análisis de volumen por día de la semana (**order_dow**) revela una concentración de demanda muy marcada en el inicio del ciclo semanal. Los hallazgos principales son:

* 🚀 **Pico de Alta Demanda (Fase de Reabastecimiento)**: El **domingo (84,090 órdenes)** y el **lunes (82,185 órdenes)** se consolidan como los días de mayor actividad transaccional. Este comportamiento sugiere que el usuario promedio de Instacart utiliza la plataforma como su herramienta principal para la planificación y compra de la despensa semanal.

* 📉 **Fase de Estabilización (Valle Semanal)**: A partir del martes, se observa una contracción en el volumen de pedidos, alcanzando su punto mínimo el **jueves (59,810 órdenes)**. Este descenso representa una caída del **28.8%** respecto al pico del domingo, marcando la ventana de menor presión operativa para la logística de entrega.

* 📈 **Recuperación de Fin de Semana**: Se detecta un repunte moderado a partir del viernes y sábado, estabilizándose por encima de las 62,000 órdenes. Esto indica una transición hacia compras de conveniencia o preparación para el fin de semana antes del gran ciclo de reabastecimiento del domingo.

💡 **Insight de Negocio**: La disparidad de volumen entre el domingo y el jueves sugiere una oportunidad para implementar estrategias de **"Dynamic Pricing"** o promociones exclusivas en días de baja demanda (miércoles/jueves) para balancear la carga operativa de los repartidores a lo largo de la semana.
            """)
    
        # --- ROW 3: El Hallazgo de Pareto ---
        # 1. Preparación de los datos (agrupando por días desde la compra previa)
        # Asegúrate de usar el DataFrame filtrado si aplica, o el original
        bar_2_data = df_filtered.groupby('days_since_prior_order').size().reset_index(name='volumen')
        bar_2_data['days_since_prior_order'] = bar_2_data['days_since_prior_order'].astype('int')

        # 2. Crear la gráfica con Plotly Express
        fig_reorder = px.bar(
            bar_2_data,
            x='days_since_prior_order',
            y='volumen',
            color='volumen', # El degradado depende del volumen de pedidos
            color_continuous_scale='Viridis', # Plotly reconoce 'Viridis' directamente
            labels={
            'days_since_prior_order': 'Días desde la compra previa',
                'volumen': 'Volumen de pedidos'
            },
            title='Distribución de pedidos según días desde la compra previa'.title()
        )

        # 3. Ajustes estéticos para modo oscuro y diseño limpio
        fig_reorder.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False, # Ocultamos la barra de escala lateral para limpieza
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50)
        )

        # 4. Configuración detallada de los ejes
        fig_reorder.update_xaxes(
            showgrid=False,
            tickmode='linear', # Mostramos todos los números del 0 al 30
            dtick=1 # Forzamos que aparezca cada día (0, 1, 2, 3...)
        )

        fig_reorder.update_yaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        )

        # 5. Desplegar en Streamlit
        st.space()
        st.space()

        c1, c2 = st.columns(2)
        c1.metric("Media", 
                    f"{df_filtered['days_since_prior_order'].mean():.0f}",
                    delta="Días desde la compra previa",
                    delta_color=delta1,
                    delta_arrow="off")
        c2.metric("Mediana", 
                    f"{df_filtered['days_since_prior_order'].median():.0f}",
                    delta="Días desde la compra previa",
                    delta_color=delta1,
                    delta_arrow="off")

        st.space()        

        st.plotly_chart(fig_reorder, use_container_width=True)

        st.info("""El estudio de la variable days_since_prior_order permite cuantificar la lealtad y los hábitos de consumo cíclicos de la base de usuarios. Los hallazgos demuestran una estructura de comportamiento altamente predecible:

* 📅 El Ciclo Semanal (Pico de los 7 días): Se observa un pico dominante a los 7 días, lo que confirma que el hábito de consumo más fuerte es el reabastecimiento semanal. La mediana ($50\%$) coincide exactamente con este valor, indicando que la mitad de los usuarios recurrentes regresan antes de una semana.

* 📈 Picos Secundarios y Periodicidad: Existe una clara presencia de picos menores a los 14 y 21 días. Estos "ecos" estadísticos sugieren segmentos de usuarios con ciclos de compra quincenales o dependientes de periodos de pago.

* 🚩 Análisis del Límite Operativo (Día 30): El volumen máximo absoluto se concentra en el día 30. No obstante, este valor debe interpretarse con cautela: estadísticamente representa un punto de acumulación (censura a la derecha). Es altamente probable que el sistema de Instacart agrupe a todos los usuarios con más de 30 días de inactividad en esta categoría, funcionando como un indicador de usuarios en riesgo de fuga (churn).

* 📉 Valores Mínimos y Frecuencia: La presencia de pedidos en el día 0 indica compras inmediatas de conveniencia o correcciones de órdenes previas, aunque representan una fracción mínima de la población.

💡 Insight de Fidelización: Los usuarios que superan el umbral de los 7-10 días sin recompra entran en una zona de "enfriamiento". Las campañas de re-engagement deberían activarse preventivamente en el día 6 para capitalizar la inercia del hábito semanal detectado.
        """)

        st.divider()

        st.header("📦 Arquitectura del Consumo")    

        st.space()

        # Filtramos por reordered == 1, agrupamos y traemos los nombres
        top_reord_data = df_order_prod[df_order_prod['reordered'] == 1].groupby('product_id').size().reset_index(name='orders')
        top_reord_data = top_reord_data.sort_values(by='orders', ascending=False).head(20)

        # Unimos con la tabla de productos para obtener los nombres
        top_reord_data = top_reord_data.merge(df_products[['product_id', 'product_name']], on='product_id', how='left')

        departments_dist = df_order_prod['department'].value_counts().reset_index()
        departments_dist['department'] = departments_dist['department'].str.title()

        # Agrupamos por 'product_id' y contamos la cantidad de 'order_id' para cada producto,
        # pero esta vez lo hacemos para los productos reordenados y no reordenados.
        reordered_vs_non = pd.pivot_table(df_order_prod, index=['product_id'], columns=['reordered'], values='order_id', aggfunc='count')

        # Rellenamos los valores ausentes con 0, 
        # ya que si no hay un valor para un producto en la columna de reordenados o no reordenados, 
        # significa que ese producto no tiene pedidos en esa categoría.
        reordered_vs_non.fillna(0, inplace=True)

        # Calculamos el total de pedidos para cada producto sumando los pedidos reordenados y no reordenados.
        reordered_vs_non['total'] = (reordered_vs_non[0] + reordered_vs_non[1])

        # Calculamos la razón de recompra dividiendo los pedidos reordenados entre el total de pedidos para cada producto.
        reordered_vs_non['razon_recompra'] = reordered_vs_non[1]/reordered_vs_non['total']
        reordered_vs_non.reset_index(inplace=True)

        # Realizamos un merge entre el DataFrame de pedidos reordenados y no reordenados y el DataFrame de productos para obtener los nombres de los productos.
        reordered_vs_non = pd.merge(reordered_vs_non, df_products[['product_id', 'product_name']], how='inner', on='product_id')
        reordered_vs_non.sort_values(['total', 'razon_recompra'], ascending=False, inplace=True)
        reordered_vs_non.reset_index(inplace=True, drop=True)

        # Creamos una nueva columna llamada 'top' que clasifica los productos en 10 grupos, cada grupo representa un decil de la contribución acumulada al total de pedidos.
        n_divisones = 10
        reordered_vs_non['top'] = ((reordered_vs_non['total'].cumsum()/reordered_vs_non['total'].sum())*n_divisones+1).astype('int').clip(1, n_divisones)
        reordered_vs_non = reordered_vs_non.iloc[:,[0, 6, 5, 1, 2, 3, 4]]

        # Creamos un DataFrame que muestra la cantidad de productos en cada grupo de 'top'
        rank_reordered_vs_non = pd.DataFrame(reordered_vs_non['top'].value_counts(ascending=True))

        # Calculamos la razón de recompra para cada grupo de 'top' dividiendo la suma de pedidos reordenados entre la suma del total de pedidos para cada grupo.
        razon_recompra =[]
        for rank in range(1,n_divisones+1):
            razon_recompra.append(reordered_vs_non[reordered_vs_non['top'] == rank][1].sum()/reordered_vs_non[reordered_vs_non['top'] == rank]['total'].sum())
        rank_reordered_vs_non['razon_recompra'] = razon_recompra           

        # --- ROW 1: Métricas de Alto Nivel ---
        col1, col2 = st.columns(2)
        col1.metric("Producto Estelelar", 
                    top_reord_data.iloc[0]['product_name'])
        col2.metric("Departamento Dominante", 
                    departments_dist.iloc[0]['department'])
        
        st.space()

        # 2. Crear la gráfica horizontal con Plotly Express
        fig_top_reord = px.bar(
            top_reord_data,
            x='orders',
            y='product_name',
            orientation='h', # Gráfica horizontal
            color='orders',
            color_continuous_scale=cool_palette,
            labels={
                'orders': 'Volumen de Recompras',
                'product_name': 'Producto'
            },
            title='Top 20 Productos Reincidentes con mas ventas'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_top_reord.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Asegura que el más vendido esté arriba
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
        )

        fig_top_reord.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig_top_reord.update_yaxes(showgrid=False)

        # 4. Desplegar en Streamlit con su Insight de Negocio
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(fig_top_reord, use_container_width=True)

            st.info("""Identificar los artículos que los usuarios vuelven a solicitar de forma recurrente permite descifrar los "básicos" indispensables del hogar. Al analizar este segmento, observamos una consistencia casi perfecta con el volumen total de ventas, pero con matices interesantes:
                    
 * 👑 **Los "Indispensables" del Inventario**: Nuevamente, la **Banana** y la **Bag of Organic Bananas** lideran el ranking. Su altísima tasa de reincidencia confirma que son productos de consumo diario y vida útil corta, lo que obliga al usuario a reponerlos en casi cada ciclo de compra (cada 7 días, como vimos en el análisis de recurrencia).

* 🧬 **Consistencia en el Perfil Orgánico**: Existe una correlación casi total entre el volumen de ventas y la reincidencia. Los productos orgánicos (fresas, espinacas, aguacates) no solo son los más comprados, sino los que presentan mayor fidelidad. Esto sugiere que el consumidor de productos orgánicos en Instacart es un **perfil de cliente recurrente**, no ocasional.

* 🥛 **La Entrada de los Lácteos**: Un hallazgo relevante en este Top es la posición de la **Organic Whole Milk** y la **Organic Half & Half**. A diferencia de otros productos que podrían ser compras impulsivas, los lácteos son marcadores de lealtad: una vez que el cliente elige una marca o tipo de leche, tiende a automatizar su compra en pedidos subsecuentes.

* 🍏 **Estabilidad de la Dieta**: La presencia de frutas como la Organic Fuji Apple y el Honeycrisp Organic indica que el usuario utiliza la plataforma para mantener hábitos alimenticios estables.

💡 **Insight de Retención**: Los productos en esta lista son los "anclas" de la aplicación. Si un cliente encuentra su marca favorita de leche o la calidad de sus bananas siempre disponible, la probabilidad de que realice su próximo pedido (el salto crítico de la compra 1 a la 2 que analizamos antes) aumenta exponencialmente. """)

        # 2. Crear la gráfica horizontal con Plotly Express
        fig_rank_reordered_vs_non = px.bar(
            rank_reordered_vs_non,
            x='count',
            y='razon_recompra',
            color='razon_recompra',
            color_continuous_scale='Viridis',
            labels={
                'count': 'Cantidad de productos por decil',
                'razon_recompra': 'Razón de recompra'
            },
            title='Razón de Recompra por Decil de ventas'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_rank_reordered_vs_non.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
            )

        fig_rank_reordered_vs_non.update_xaxes(type='category')
        fig_rank_reordered_vs_non.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')

        # 2. Crear la gráfica horizontal con Plotly Express
        fig_depts = px.bar(
            departments_dist,
            x='count',
            y='department',
            orientation='h', # Gráfica horizontal
            color='count',
            color_continuous_scale=winter_palette,
            labels={
                'count': 'Volumen pedidos por departamento',
                'department': 'Departamento'
            },
            title='Distribución y Dominancia por Departamento'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_depts.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Asegura que el más vendido esté arriba
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
        )

        fig_depts.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig_depts.update_yaxes(showgrid=False)

        with c2:
            st.plotly_chart(fig_depts, use_container_width=True)

            st.info("""Entender la macro-estructura de los pedidos permite identificar qué categorías sostienen la operación logística y cuáles son los verdaderos "imanes" de tráfico. Al analizar el volumen total por departamento, la jerarquía del sistema se revela con total claridad:

* 🌽 El "Core" de Alta Frecuencia: El departamento de Produce (frutas y verduras) no solo lidera, sino que duplica en volumen al segundo lugar. Esta dominancia absoluta confirma que Instacart es, ante todo, una herramienta de reabastecimiento de frescos. Para el negocio, esto significa que la calidad percibida en este departamento define la retención del cliente: si el aguacate llega mal, se pierde la confianza en todo el carrito.

* 🥛 Lácteos y Huevos como Pilares: Dairy Eggs ocupa el segundo puesto con una solidez notable. Al igual que las bananas en el análisis de productos, estos son artículos de "consumo invisible" pero constante. Son productos con una ventana de caducidad media, lo que refuerza la teoría de los ciclos de compra semanales (7 días) que observamos previamente.

* 🥤 La Capa de Conveniencia: Los departamentos de Snacks y Beverages completan el grupo de cabeza. A diferencia de los perecederos, estos productos tienen márgenes de ganancia más altos y una vida útil prolongada. Su alta presencia sugiere que, una vez que el usuario entra por los básicos (frutas/leche), tiende a completar su canasta con artículos de conveniencia, lo que eleva el valor del ticket promedio.

* 🧼 Segmentos de Especialidad y "Long-Tail": Departamentos como Personal Care, Babies o Pets muestran volúmenes significativamente menores. Esto indica que el usuario promedio aún no utiliza la plataforma para compras integrales de "tienda departamental", sino que mantiene una fidelidad selectiva. Aquí reside la mayor oportunidad de crecimiento mediante estrategias de cross-selling.

💡 Insight de Operación: La logística de Instacart es, esencialmente, una cadena de frío y frescos. Más del 60% de la operación se concentra en departamentos con productos sensibles a la temperatura y al tiempo. Cualquier optimización en la ruta de entrega o en el proceso de selección (picking) en estas categorías tendrá un impacto desproporcionado en la rentabilidad y satisfacción final.
""")
        st.space()
        st.space()

        col1, col2, col3 = st.columns(3) # Espacio para respirar entre métricas y gráfica

        col1.metric("10% de las transacciones",
                    f"{rank_reordered_vs_non['count'][0:1].sum():,} Productos",
                    delta=f"{rank_reordered_vs_non['count'][0:1].sum()/rank_reordered_vs_non['count'].sum():.2%} del Catálogo",
                    delta_color=delta1,
                    delta_arrow="off")  

        col2.metric("50% de las transacciones",
                    f"{rank_reordered_vs_non['count'][0:5].sum():,} Productos",
                    delta=f"{rank_reordered_vs_non['count'][0:5].sum()/rank_reordered_vs_non['count'].sum():.2%} del Catálogo",
                    delta_color=delta1,
                    delta_arrow="off")

        col3.metric("90% de las transacciones",
                    f"{rank_reordered_vs_non['count'][0:9].sum():,} Productos",
                    delta=f"{rank_reordered_vs_non['count'][0:9].sum()/rank_reordered_vs_non['count'].sum():.2%} del Catálogo",
                    delta_color=delta1,
                    delta_arrow="off") 

        st.space()          
     
        st.plotly_chart(fig_rank_reordered_vs_non, use_container_width=True)

        st.info("""
Para entender la estructura del catálogo, se implementó una segmentación de productos por deciles basada en el volumen de transacciones. Cada segmento representa exactamente el **10% del volumen total de ventas**, permitiendo contrastar la popularidad contra la lealtad (recompra).

1. 🎯 **Concentración Extrema de la Demanda (Efecto Pareto)**

    Los datos revelan una asimetría masiva en el rendimiento de los productos:

    * 💎 **La Élite del Catálogo (Decil 1)**: Únicamente **18 productos** (el $0.04\%$ del total) son responsables del primer $10\%$ de todas las ventas. Estos son los "motores" de la plataforma.

    * ⚖️ **Punto de Equilibrio ($50/1.7$)**: Los primeros 785 productos ($1.7\%$ del catálogo) generan más de la mitad del volumen transaccional.

    * 🏷️ **La "Larga Cola" (Decil 10)**: El último $10\%$ de las ventas está disperso entre 36,445 productos ($80\%$ del catálogo).

    * 🚀 **Diferencial de Velocidad**: Un producto del primer decil se vende, en promedio, 2,000 veces más que uno del último decil.

2. 🤝 **Correlación Volumen-Lealtad (Gradiente de Retención)**

    Se identificó que la popularidad no solo atrae volumen, sino que fomenta la lealtad:

    * 🧲 **Decil de Alta Fidelidad**: El primer decil presenta una razón de recompra del $76.3\%$, la más alta del sistema.

    * 📉 **Degradación Progresiva**: Existe un gradiente de lealtad decreciente de entre el $5\%$ y el $7\%$ por cada decil. A medida que un producto es menos popular, su probabilidad de ser vuelto a comprar cae drásticamente, llegando apenas al $42.4\%$ en el último decil.

💡 **Insight Estratégico**: El negocio posee un núcleo de "Ultra-Alta Rotación" extremadamente fiel. Mientras que el $80\%$ del catálogo (la Long Tail) ofrece variedad, el éxito operativo y la retención del usuario dependen casi exclusivamente del $2\%$ de los productos. Cualquier interrupción en la cadena de suministro de este núcleo tendría un impacto sistémico inmediato.
                """)
        
        st.divider()

        st.header("👤 Perfil de Cliente y Mecánicas de Consumo")

        st.space()  

        # Agrupamos por 'order_id' y contamos la cantidad de 'product_id' para cada pedido. 
        # Luego contamos la cantidad de pedidos para cada cantidad de productos por pedido, 
        # ordenamos los valores por el índice y lo guardamos en un nuevo DataFrame.
        # Finalmente, obtenemos el número de productos por pedido y el número de pedidos para cada cantidad de productos por pedido.
        qorder_vs_qproducts = pd.DataFrame(df_order_prod.groupby('order_id')['product_id'].count().value_counts().sort_index())
        qorder_vs_qproducts.index.name='number_of_products_per_order'
        qorder_vs_qproducts.rename(columns={'count': 'number_of_orders'}, inplace=True)
        qorder_vs_qproducts.reset_index(inplace=True)

        # Contamos la cantidad de ordenes por cliente y el número de clientes para cada cantidad de ordenes
        orders_per_client = df_filtered.groupby('user_id')['order_id'].count()
        dist_per_clients = pd.DataFrame(orders_per_client.value_counts()).rename(columns={'count': 'clients'})
        dist_per_clients.reset_index(inplace=True)

        clients_reord = df_order_prod

        # Creamos una tabla pivote para contar la cantidad de pedidos reordenados y no reordenados para cada cliente.
        clients_reord = pd.pivot_table(clients_reord, values='order_id', index='user_id', columns='reordered', aggfunc='count', fill_value=0)
        clients_reord.columns.name = None

        # Calculamos el total de pedidos para cada cliente sumando los pedidos reordenados y no reordenados.
        clients_reord['order_product'] = clients_reord[0]+clients_reord[1]

        # Calculamos la razón de recompra dividiendo los pedidos reordenados entre el total de pedidos para cada cliente.
        clients_reord['razon_recompra'] = clients_reord[1]/clients_reord['order_product']
        clients_reord.sort_values('order_product', inplace=True, ascending=False)
        clients_reord.reset_index(inplace=True)
        clients_reord.index = range(1,len(clients_reord.index.values)+1)
        clients_reord.index.name = 'rank'

        # Creamos una nueva columna llamada 'top' que clasifica a los clientes en 10 grupos, cada grupo representa un decil de la contribución acumulada al total de pedidos.
        n_divisones = 10
        cumsum_pct = clients_reord['order_product'].cumsum() / clients_reord['order_product'].sum()
        clients_reord['top'] = ((cumsum_pct * n_divisones).astype(int) + 1).clip(1, n_divisones)
        clients_reord = clients_reord.iloc[:,[5, 0, 1, 2, 3, 4]]       
        
        # Creamos un DataFrame que muestra la cantidad de clientes en cada grupo de 'top'
        rank_clients_reord = pd.DataFrame(clients_reord['top'].value_counts(ascending=True))

        # Calculamos la razón de recompra para cada grupo de 'top' dividiendo la suma de pedidos reordenados entre la suma del total de pedidos para cada grupo.
        razon_recompra=[]
        for indice in rank_clients_reord.index.values:
            razon_recompra.append(clients_reord[clients_reord['top'] == indice][1].sum()/clients_reord[clients_reord['top'] == indice]['order_product'].sum())
        rank_clients_reord['razon_recompra'] = razon_recompra                
        
        fig_qorder_vs_qproducts = px.bar(
            qorder_vs_qproducts,
            x='number_of_products_per_order',
            y='number_of_orders',
            color='number_of_orders',
            color_continuous_scale=winter_palette,
            labels={
                'number_of_orders': 'Volumen pedidos'.title(),
                'number_of_products_per_order': 'Número de productos en el pedido'.title()
            },
            title='Distribución de la Cantidad de Productos por Pedido'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_qorder_vs_qproducts.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Asegura que el más vendido esté arriba
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
        )

        fig_qorder_vs_qproducts.update_xaxes(type='category')
        fig_qorder_vs_qproducts.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')              

        col1, col2 = st.columns(2)
        with col1:

        # --- ROW 1: Métricas de Alto Nivel ---
            qprod_ord = df_order_prod.groupby('order_id')['product_id'].count()
            c1, c2 = st.columns(2)
            c1.metric("Media", 
                        f"{qprod_ord.mean():.0f}",
                        delta="Productos por pedido",
                        delta_color=delta2,
                        delta_arrow="off")
            c2.metric("Mediana", 
                        f"{qprod_ord.median():.0f}",
                        delta="Productos por pedido",
                        delta_color=delta2,
                        delta_arrow="off")
            
            st.space()
  
            st.plotly_chart(fig_qorder_vs_qproducts, use_container_width=True)

            st.info(r"""
                El estudio del volumen de artículos por transacción permite entender el uso que el cliente le da a la plataforma (¿compras de conveniencia o abastecimiento total?). Los datos revelan una distribución asimétrica con una "larga cola":
                
                * 📦 **El "Sweet Spot" del Carrito**: La mayoría de los pedidos se concentran en un rango de **3 a 7 productos**, alcanzando su moda (el punto más alto) en los **5 artículos**. Esto sugiere que una gran parte de las transacciones son compras de reposición rápida o categorías específicas.

                * 📊 **Tendencia Central y Dispersión**: El promedio se sitúa en $\approx 10$ artículos, pero la mediana ($50\%$) es de 8. Esta discrepancia, sumada a una desviación estándar de $7.5$, indica que aunque los carritos pequeños son más frecuentes, hay una presencia constante de pedidos medianos y grandes que elevan el ticket promedio.

                * 🐉 **Carritos de Volumen Extremo**: Se observa una extensión de la distribución que llega hasta un máximo de **127 productos**. Es aquí donde residen los datos que anteriormente identificamos con el marcador `999` (aquellos que superaron la posición 64), representando a las familias o clientes institucionales que realizan compras masivas.

                * 📉 **Compras de Conveniencia Única**: Un volumen considerable de usuarios realiza pedidos de un solo artículo ($n=1$), lo cual resalta la importancia de la logística de "última milla" para artículos de urgencia.

                💡 **Insight Logístico**: Con el 75% de las órdenes conteniendo 14 productos o menos, la operación de picking (recolección en tienda) es altamente eficiente para pedidos pequeños. Sin embargo, el segmento de carritos con $>30$ productos requiere una gestión de transporte distinta para asegurar la integridad de los productos frescos detectados en el Top 20.
            """)

        fig_orders_per_client = px.bar(
            dist_per_clients,
            x='order_id',
            y='clients',
            color='clients',
            color_continuous_scale=cool_palette,
            labels={
                'order_id': 'Pedidos por Cliente'.title(),
                'clients': 'Volumen de clientes'.title()
            },
            title='Distribución de la Cantidad de Pedidos por Cliente'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_orders_per_client.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Asegura que el más vendido esté arriba
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
        )

        fig_orders_per_client.update_xaxes(type='category')
        fig_orders_per_client.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')    

        with col2:

        # --- ROW 1: Métricas de Alto Nivel ---
            c1, c2 = st.columns(2)
            c1.metric("Media", 
                        f"{orders_per_client.mean():.0f}",
                        delta="Pedidos por cliente",
                        delta_color=delta3,
                        delta_arrow="off")
            c2.metric("Mediana", 
                        f"{orders_per_client.median():.0f}",
                        delta="Pedidos por cliente",
                        delta_color=delta3,
                        delta_arrow="off")
            
            st.space()

            st.plotly_chart(fig_orders_per_client, use_container_width=True)

            st.info(r"""
                El análisis de la frecuencia de compra por usuario único permite entender la penetración de la plataforma y el nivel de retención. Los datos revelan una base de usuarios con las siguientes características:

                * 📈 **Dominancia de Nuevos Usuarios (Adquisición)**: El volumen más alto de clientes se concentra en **1 solo pedido (55,000+ usuarios)**. Esto indica una etapa de fuerte adquisición de usuarios, pero también resalta el reto de convertirlos en compradores recurrentes.

                * 📊 **Medidas de Tendencia Central**: El promedio de órdenes por cliente es de $\approx 3.04$, mientras que la mediana se sitúa en 2.0. Esta diferencia entre la media y la mediana confirma un sesgo a la derecha; es decir, un grupo selecto de usuarios frecuentes está elevando el promedio general.

                * 🐉 **La "Larga Cola" (Power Users)**: Aunque la frecuencia decae rápidamente, existe un segmento de clientes leales que han realizado hasta **28 pedidos**. Estos "Power Users" representan el activo más valioso para la estabilidad de ingresos de la plataforma, a pesar de ser una minoría estadística.

                * 📉 **Tasa de Abandono Temprano**: Se observa una caída pronunciada entre el primer y el segundo pedido. El 75% de los clientes han realizado 4 pedidos o menos, lo que sugiere que los primeros 3 contactos con el servicio son críticos para asegurar la retención a largo plazo.

                💡 **Insight de Marketing**: Existe una oportunidad masiva en la conversión de usuarios de "un solo uso" hacia el segundo y tercer pedido. Implementar programas de **lealtad o cupones de retención** tras la primera compra podría desplazar la mediana hacia la derecha y aumentar el Life Time Value (LTV) promedio.
            """)

        fig_rank_clients_reord = px.bar(
            rank_clients_reord,
            x='count',
            y='razon_recompra',
            color='razon_recompra',
            color_continuous_scale='Viridis',
            labels={
                'count': 'Cantidad de Clientes por Decil'.title(),
                'razon_recompra': 'Razón de Recompra'.title()
            },
            title='Razón de Recompra por Decil de Clientes'.title()
            )

        # 3. Ajustes estéticos (Modo Oscuro y Limpieza)
        fig_rank_clients_reord.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            coloraxis_showscale=False,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}, # Asegura que el más vendido esté arriba
            margin=dict(t=50, b=50, l=50, r=50),
            height=600 # Un poco más de altura para que los nombres respiren
        )

        fig_rank_clients_reord.update_xaxes(type='category')
        fig_rank_clients_reord.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')

        st.space()

        st.space()

        col1, col2, col3 = st.columns(3) # Espacio para respirar entre métricas y gráfica  

        col1.metric("10% de las transacciones",
                    f"{rank_clients_reord['count'][0:1].sum():,} Clientes",
                    delta=f"{rank_clients_reord['count'][0:1].sum()/rank_clients_reord['count'].sum():.2%} de la Base Total",
                    delta_color=delta4,
                    delta_arrow="off")  

        col2.metric("50% de las transacciones",
                    f"{rank_clients_reord['count'][0:5].sum():,} Clientes",
                    delta=f"{rank_clients_reord['count'][0:5].sum()/rank_clients_reord['count'].sum():.2%} de la Base Total",
                    delta_color=delta4,
                    delta_arrow="off")

        col3.metric("90% de las transacciones",
                    f"{rank_clients_reord['count'][0:9].sum():,} Clientes",
                    delta=f"{rank_clients_reord['count'][0:9].sum()/rank_clients_reord['count'].sum():.2%} de la Base Total",
                    delta_color=delta4,
                    delta_arrow="off") 

        st.space()    

        st.plotly_chart(fig_rank_clients_reord, use_container_width=True)        

        st.info(r"""
            Se aplicó una división por deciles donde cada grupo representa el **10% del volumen total de artículos comprados**, permitiendo diseccionar la base de usuarios según su intensidad transaccional.

            1. 🎯 **Concentración de Usuarios de Alto Valor (VIPs)**

                Los datos revelan una asimetría crítica en la generación de volumen:
                
                * 🥇 **El Núcleo Transaccional (Decil 1)**: Solo **2,209 usuarios** (apenas el $1.48\%$ de la base total) son responsables del primer $10\%$ de las ventas. Estos clientes "ultra-activos" son los pilares de la estabilidad operativa.

                * 🐉 **Dispersión en la Base (Decil 10)**: En contraste, el último $10\%$ del volumen es generado por **61,966 usuarios**, lo que evidencia un segmento de clientes ocasionales o en fase de prueba.

                * 💎 **Ratio de Intensidad**: Un cliente del Decil 1 es, en promedio, **28 veces más activo** que un cliente del Decil 10.
            
            2. 📈 **Correlación Actividad-Lealtad (Gradiente de Retención)**
            
                Se confirma que a mayor volumen de compra, mayor es la fidelidad al catálogo:

                * 🤝 **Máxima Fidelidad (Decil 1)**: Presenta una tasa de recompra del $77.3\%$. Este grupo prácticamente ha automatizado su consumo.

                * 📉 **Gradiente de Descenso**: Se observa una degradación constante y predecible de aproximadamente $5\%$ por decil.

                * ⚠️ **Umbral Crítico**: Incluso en el Decil 10, la recompra se mantiene en un $42.2\%$, lo que indica que Instacart tiene una "barrera de entrada" de lealtad alta; casi la mitad de los clientes ocasionales tienden a repetir algún producto.
                """)   

    else:
        # Mensaje amigable si el usuario filtra demasiado
        st.warning("⚠️ No se encontraron pedidos para la combinación de filtros seleccionada.")
        st.info("💡 Sugerencia: Intenta seleccionar más días de la semana o ampliar el rango de horas en el sidebar.")
        
except FileNotFoundError:
    st.error("⚠️ No se encontraron los archivos de datos en la carpeta `data/`. Verifica las rutas.")

# --- Sección Final de Contacto ---
st.markdown("---") # Una línea divisoria clara


st.markdown("""
### 📫 Contacto y Colaboración
¿Listo para transformar tus datos en estrategia?
            
Actualmente abierto a colaborar en proyectos de Data Science, Machine Learning y consultoría analítica."""
)
st.markdown("---")
st.markdown(
    """
    <p style='text-align: center;'>
        <a href='https://davidvaac.github.io/DavidVaAc/'>💼 Portafolio</a> &nbsp;&nbsp; | &nbsp;&nbsp;
        <a href='https://www.linkedin.com/in/david-fernando-valle-acosta-b18268265/'>🔗 LinkedIn</a> &nbsp;&nbsp; | &nbsp;&nbsp;
        <a href='https://github.com/DavidVaAc'>📁 GitHub</a> &nbsp;&nbsp; | &nbsp;&nbsp;
        <a href='mailto:davidfervalle@gmail.com'>✉️ Email</a>
    </p>
    """, 
    unsafe_allow_html=True
)

# Un pie de página discreto
st.caption("© 2026 | Desarrollado por David Valle Acosta - Físico, UNAM")