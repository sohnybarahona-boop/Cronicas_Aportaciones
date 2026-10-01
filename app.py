import streamlit as st
import json
import os
import pandas as pd

# ==============================================================================
# Iglesia Sabaoth - Ministerios Ebenezer
# Equipo: Crónicas Sabaoth (Control de Aportaciones y Gastos Audiovisuales)
# ==============================================================================

NOMBRE_ARCHIVO = "cronicas_control.json"

INTEGRANTES_BASE = [
    "Ramon Martinez", "Tania Dominguez", "Sohny Barahona", "Kennly Banegas",
    "Wendy Martinez", "Jassie Gonzales", "Jair Quinto", "Samuel Majano",
    "Luis Palma", "Genesis Mejia", "Jeizel Martinez", "Kimberly Amador",
    "Nahomi Bonilla", "Shaira Sofia", "Yuri Pacheco", "Carlos Pacheco",
    "Eduard Garcia", "Valeria Rodriguez", "Alexi"
]

MESES_ORDEN = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def cargar_datos():
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if "integrantes" not in datos:
                datos["integrantes"] = list(INTEGRANTES_BASE)
            if "aportaciones" not in datos:
                datos["aportaciones"] = {}
            if "gastos" not in datos:
                datos["gastos"] = []
            return datos
    return {
        "integrantes": list(INTEGRANTES_BASE),
        "aportaciones": {},
        "gastos": []
    }

def guardar_datos(datos):
    with open(NOMBRE_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Configuración de página
st.set_page_config(
    page_title="Crónicas Sabaoth - Control Finanzas",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Crónicas Sabaoth - Control de Aportaciones y Gastos")

# Cargar base de datos
datos = cargar_datos()

# Menú lateral de navegación
menu = st.sidebar.selectbox(
    "Navegación / Menú",
    [
        "📊 Cuadro Resumen y Finanzas",
        "💵 Registrar Aportación",
        "📅 Registrar / Crear Mes",
        "🛒 Registrar Gasto",
        "👥 Gestionar Integrantes"
    ]
)

# ------------------------------------------------------------------------------
# 1. CUADRO RESUMEN Y FINANZAS GENERALES
# ------------------------------------------------------------------------------
if menu == "📊 Cuadro Resumen y Finanzas":
    st.header("📊 Resumen Financiero y Tabla General")

    meses_registrados = list(datos["aportaciones"].keys())
    meses_ordenados = sorted(
        meses_registrados,
        key=lambda m: MESES_ORDEN.index(m) if m in MESES_ORDEN else 99
    )

    # Cálculo de aportaciones
    totales_integrante = {p: 0.0 for p in datos["integrantes"]}
    totales_mes = {m: 0.0 for m in meses_ordenados}
    total_aportaciones = 0.0

    tabla_data = []
    for persona in datos["integrantes"]:
        fila = {"Integrante": persona}
        tot_pers = 0.0
        for m in meses_ordenados:
            monto = float(datos["aportaciones"][m].get(persona, 0.0))
            fila[m] = f"{monto:.2f} €" if monto > 0 else "-"
            tot_pers += monto
            totales_mes[m] += monto
        
        fila["Total (€)"] = f"{tot_pers:.2f} €"
        totales_integrante[persona] = tot_pers
        total_aportaciones += tot_pers
        tabla_data.append(fila)

    total_gastos = sum(float(g["monto"]) for g in datos["gastos"])
    saldo_neto = total_aportaciones - total_gastos

    # Métricas superiores
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Aportaciones", f"{total_aportaciones:.2f} €")
    col2.metric("Total Gastos", f"{total_gastos:.2f} €")
    col3.metric("Saldo Neto Disponible", f"{saldo_neto:.2f} €")

    st.divider()

    # Tabla de Aportaciones
    st.subheader("📋 Tabla Resumen de Aportaciones")
    if tabla_data and meses_ordenados:
        df = pd.DataFrame(tabla_data)
        
        # Fila de totales por mes
        fila_totales = {"Integrante": "TOTAL MENSUAL (€)"}
        for m in meses_ordenados:
            fila_totales[m] = f"{totales_mes[m]:.2f} €"
        fila_totales["Total (€)"] = f"{total_aportaciones:.2f} €"
        
        df = pd.concat([df, pd.DataFrame([fila_totales])], ignore_index=True)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay meses registrados en el sistema. Registra un mes en el menú lateral.")

    st.divider()

    # Desglose de Gastos
    st.subheader("🛒 Desglose de Gastos Registrados")
    if datos["gastos"]:
        df_gastos = pd.DataFrame(datos["gastos"])
        df_gastos.columns = ["Concepto / Descripción", "Monto (€)"]
        df_gastos["Monto (€)"] = df_gastos["Monto (€)"].apply(lambda x: f"{float(x):.2f} €")
        st.dataframe(df_gastos, use_container_width=True)
    else:
        st.write("No hay gastos registrados en el sistema.")

# ------------------------------------------------------------------------------
# 2. REGISTRAR APORTACIÓN (Monto Exacto)
# ------------------------------------------------------------------------------
elif menu == "💵 Registrar Aportación":
    st.header("💵 Registrar Aportación Individual")

    meses_registrados = list(datos["aportaciones"].keys())
    if not meses_registrados:
        st.warning("Debes registrar primero un mes en la sección 'Registrar / Crear Mes'.")
    else:
        mes_sel = st.selectbox("Selecciona el mes:", meses_registrados)
        integrante_sel = st.selectbox("Selecciona el integrante:", datos["integrantes"])

        monto_actual = float(datos["aportaciones"][mes_sel].get(integrante_sel, 0.0))
        st.info(f"Monto actual registrado para **{integrante_sel}** en **{mes_sel}**: **{monto_actual:.2f} €**")

        nuevo_monto = st.number_input("Monto aportado (€):", min_value=0.0, step=1.0, value=monto_actual)

        if st.button("Guardar Aportación", type="primary"):
            datos["aportaciones"][mes_sel][integrante_sel] = nuevo_monto
            guardar_datos(datos)
            st.success(f"¡Aportación de {nuevo_monto:.2f} € registrada para {integrante_sel} en {mes_sel}!")

# ------------------------------------------------------------------------------
# 3. REGISTRAR / CREAR MES
# ------------------------------------------------------------------------------
elif menu == "📅 Registrar / Crear Mes":
    st.header("📅 Crear o Activar Mes")

    nuevo_mes = st.selectbox("Selecciona un mes para habilitar:", MESES_ORDEN)

    if st.button("Registrar Mes", type="primary"):
        if nuevo_mes in datos["aportaciones"]:
            st.warning(f"El mes de {nuevo_mes} ya está registrado.")
        else:
            datos["aportaciones"][nuevo_mes] = {p: 0.0 for p in datos["integrantes"]}
            guardar_datos(datos)
            st.success(f"¡Mes de {nuevo_mes} creado e inicializado correctamente!")

# ------------------------------------------------------------------------------
# 4. REGISTRAR GASTO
# ------------------------------------------------------------------------------
elif menu == "🛒 Registrar Gasto":
    st.header("🛒 Registrar Nuevo Gasto")

    concepto = st.text_input("Descripción / Concepto del gasto (ej. Cables, Baterías):")
    monto_gasto = st.number_input("Monto gastado (€):", min_value=0.1, step=0.5)

    if st.button("Registrar Gasto", type="primary"):
        if not concepto.strip():
            st.error("Debes ingresar una descripción para el gasto.")
        else:
            datos["gastos"].append({"concepto": concepto.strip(), "monto": monto_gasto})
            guardar_datos(datos)
            st.success(f"¡Gasto registrado: '{concepto}' por {monto_gasto:.2f} €!")

# ------------------------------------------------------------------------------
# 5. GESTIONAR INTEGRANTES
# ------------------------------------------------------------------------------
elif menu == "👥 Gestionar Integrantes":
    st.header("👥 Agregar o Eliminar Integrantes")

    tab1, tab2 = st.tabs(["➕ Agregar Integrante", "❌ Eliminar Integrante"])

    with tab1:
        nuevo_integrante = st.text_input("Nombre y Apellido del nuevo integrante:")
        if st.button("Agregar a Crónicas"):
            nombre_limpio = nuevo_integrante.strip()
            if not nombre_limpio:
                st.error("El nombre no puede estar vacío.")
            elif nombre_limpio in datos["integrantes"]:
                st.warning(f"'{nombre_limpio}' ya forma parte del equipo.")
            else:
                datos["integrantes"].append(nombre_limpio)
                for m in datos["aportaciones"]:
                    datos["aportaciones"][m][nombre_limpio] = 0.0
                guardar_datos(datos)
                st.success(f"¡'{nombre_limpio}' agregado exitosamente al equipo!")

    with tab2:
        if datos["integrantes"]:
            integrante_elim = st.selectbox("Selecciona el integrante a eliminar:", datos["integrantes"])
            if st.button("Eliminar Integrante", type="primary"):
                datos["integrantes"].remove(integrante_elim)
                for m in datos["aportaciones"]:
                    if integrante_elim in datos["aportaciones"][m]:
                        del datos["aportaciones"][m][integrante_elim]
                guardar_datos(datos)
                st.success(f"¡'{integrante_elim}' ha sido eliminado del equipo!")
        else:
            st.info("No hay integrantes en la lista.")