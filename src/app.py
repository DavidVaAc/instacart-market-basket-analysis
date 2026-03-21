import streamlit as st
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
import seaborn as sns
import os
plt.style.use('dark_background')

# Configuración de la página
st.set_page_config(page_title="Instacart Insights Dashboard", layout="wide")

# Título y Contexto
st.title("🛒 Instacart Market Basket Analysis")
st.markdown("""
Esta aplicación interactiva presenta los hallazgos clave del análisis de comportamiento del consumidor.
*Explora las métricas de lealtad, tiempos de compra y la eficiencia del catálogo.*
""")

# Función para cargar datos (Usa @st.cache_data para que sea rápido)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'instacart_orders.csv')
    orders = pd.read_csv(path, sep=';')
    return orders

def load_order_prod():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'order_products.csv')
    order_prods = pd.read_csv(path, sep=';')
    return order_prods

def load_products():
    # Asegúrate de que las rutas coincidan con tu estructura
    path = os.path.join(BASE_DIR, '..', 'data', 'products.csv')
    products = pd.read_csv(path, sep=';')
    return products

try:
    df_orders = load_data()
    dias_dict = {0: 'Domingo', 1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado'}
    df_orders['order_dow'] = df_orders['order_dow'].replace(dias_dict)
    # --- SIDEBAR: Filtros ---
    dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

    # 1. Definimos el orden lógico para que los checkboxes no salgan alfabéticos

    st.sidebar.header("📅 Filtros de Análisis")
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


    st.divider()

    # --- ROW 2: Visualizaciones Temporales ---
    st.header("⏰ Dinámicas Temporales")

    st.space()

    # --- ROW 1: Métricas de Alto Nivel ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Órdenes", f"{len(df_filtered):,}")
    col2.metric("Promedio Hora de Compra", f"{df_filtered['order_hour_of_day'].mean():.1f} hrs")
    col3.metric("Día Pico", f"{df_filtered['order_dow'].mode()[0]}")

    c1, c2 = st.columns(2)

    with c1:
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
        st.plotly_chart(fig_hours)

        st.info("**⏰ Estrategia Horaria:** El 65% de la carga ocurre entre las 10am y 4pm. Optimizar el personal en esta ventana es clave para la eficiencia operativa.")

    with c2:
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

        st.info("**📅 Estrategia Semanal:** El pico de Domingo/Lunes valida el hábito de 'despensa semanal'. Las promociones de retención son más efectivas los fines de semana.")
    
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

    st.plotly_chart(fig_reorder, use_container_width=True)

    st.info(" 💡 **Insight de Negocio:** El pico en el día 7 revela ciclos de lealtad semanal.")

    st.divider()

    st.header("📊 El Factor de Retención")    

    # 1. Preparación de los datos (Top 20 Reordenados)
    df_order_prod = load_order_prod().merge(df_filtered[['order_id','order_dow','order_hour_of_day']], on='order_id', how='inner') 
    df_products = load_products()
    # Filtramos por reordered == 1, agrupamos y traemos los nombres
    top_reord_data = df_order_prod[df_order_prod['reordered'] == 1].groupby('product_id').size().reset_index(name='orders')
    top_reord_data = top_reord_data.sort_values(by='orders', ascending=False).head(20)

    # Unimos con la tabla de productos para obtener los nombres
    top_reord_data = top_reord_data.merge(df_products[['product_id', 'product_name']], on='product_id', how='left')

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

        st.info("""
 * 👑 **Los "Indispensables" del Inventario**: Nuevamente, la **Banana** y la **Bag of Organic Bananas** lideran el ranking. Su altísima tasa de reincidencia confirma que son productos de consumo diario y vida útil corta, lo que obliga al usuario a reponerlos en casi cada ciclo de compra (cada 7 días, como vimos en el análisis de recurrencia).

* 🧬 **Consistencia en el Perfil Orgánico**: Existe una correlación casi total entre el volumen de ventas y la reincidencia. Los productos orgánicos (fresas, espinacas, aguacates) no solo son los más comprados, sino los que presentan mayor fidelidad. Esto sugiere que el consumidor de productos orgánicos en Instacart es un **perfil de cliente recurrente**, no ocasional.

* 🥛 **La Entrada de los Lácteos**: Un hallazgo relevante en este Top es la posición de la **Organic Whole Milk** y la **Organic Half & Half**. A diferencia de otros productos que podrían ser compras impulsivas, los lácteos son marcadores de lealtad: una vez que el cliente elige una marca o tipo de leche, tiende a automatizar su compra en pedidos subsecuentes.

* 🍏 **Estabilidad de la Dieta**: La presencia de frutas como la Organic Fuji Apple y el Honeycrisp Organic indica que el usuario utiliza la plataforma para mantener hábitos alimenticios estables.

💡 **Insight de Retención**: Los productos en esta lista son los "anclas" de la aplicación. Si un cliente encuentra su marca favorita de leche o la calidad de sus bananas siempre disponible, la probabilidad de que realice su próximo pedido (el salto crítico de la compra 1 a la 2 que analizamos antes) aumenta exponencialmente. """)

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
    reordered_vs_non = pd.merge(reordered_vs_non, df_products[['product_id', 'product_name']], how='left', on='product_id')
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

        # 2. Crear la gráfica horizontal con Plotly Express
    fig_rank_reordered_vs_non = px.bar(
        rank_reordered_vs_non,
      x='count',
      y='razon_recompra',
      color='razon_recompra',
      color_continuous_scale=winter_palette,
       labels={
          'count': 'Cantidad de productos por decil',
          'razon_recompra': 'Razón de recompra'
       },
       title='Razón de Recompra por Decil'.title()
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

    fig_rank_reordered_vs_non.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', type='category')
    fig_rank_reordered_vs_non.update_yaxes(showgrid=False)

    with c2:
        st.plotly_chart(fig_rank_reordered_vs_non, use_container_width=True)

        st.info("""
Para entender la estructura del catálogo, se implementó una segmentación por deciles basada en el volumen de transacciones. Cada segmento representa exactamente el **10% del volumen total de ventas**, permitiendo contrastar la popularidad contra la lealtad (recompra).

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
      

        
except FileNotFoundError:
    st.error("⚠️ No se encontraron los archivos de datos en la carpeta `data/`. Verifica las rutas.")