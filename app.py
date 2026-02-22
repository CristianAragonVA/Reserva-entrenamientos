# ============================================================
#  Excursionistas — Reserva 2026
#  App Streamlit para cuerpo técnico de fútbol
#  Datos en tiempo real desde Google Sheets (CSV público)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ─────────────────────────────────────────────
#  CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────

# ⚙️  Reemplazá este ID si cambiás el Google Sheets
SHEET_ID = "1swZ_PRVtKwm3WwKX0HKvKDJV6r_UAxo3194yBx6ipfk"

# Paleta de colores del panel
COLOR_VERDE   = "#00c46a"
COLOR_NARANJA = "#ff6b35"
COLOR_FONDO   = "#0e1117"
COLOR_CARD    = "#1c2333"
COLOR_TEXTO   = "#e8eaed"

# Colores por tipo de tarea
TIPO_COLORES = {
    "Activación":     {"border": "#ffd600", "bg": "rgba(255,214,0,0.10)",   "text": "#ffd600"},
    "Física":         {"border": "#ff4b4b", "bg": "rgba(255,75,75,0.10)",    "text": "#ff4b4b"},
    "Técnica":        {"border": "#38bdf8", "bg": "rgba(56,189,248,0.10)",   "text": "#38bdf8"},
    "Táctico":        {"border": "#00c46a", "bg": "rgba(0,196,106,0.10)",    "text": "#00c46a"},
    "Fútbol Formal":  {"border": "#a78bfa", "bg": "rgba(167,139,250,0.10)",  "text": "#a78bfa"},
    "Fútbol formal":  {"border": "#a78bfa", "bg": "rgba(167,139,250,0.10)",  "text": "#a78bfa"},
}
TIPO_DEFAULT = {"border": "#00c46a", "bg": "rgba(0,196,106,0.10)", "text": "#00c46a"}

# Orden canónico de días de la semana
DIAS_ORDEN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Orden de posiciones para agrupar plantel
POSICIONES_ORDEN = ["Arquero", "Defensor", "Mediocampista", "Delantero"]
POS_PLURAL = {
    "Arquero": "Arqueros",
    "Defensor": "Defensores",
    "Mediocampista": "Mediocampistas",
    "Delantero": "Delanteros",
}
POS_EMOJI = {
    "Arquero": "🧤",
    "Defensor": "🔵",
    "Mediocampista": "⚙️",
    "Delantero": "⚡",
}

st.set_page_config(
    page_title="Excursionistas — Reserva 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Tarjeta de tarea — borde y fondo dinámico via inline style */
.tarea-card {
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-left: 4px solid #00c46a;
}
.tarea-titulo {
    font-size: 1rem;
    font-weight: 700;
    color: #e8eaed;
    margin-bottom: 4px;
}
.tarea-meta {
    font-size: 0.82rem;
    color: #8d9db6;
}
.tipo-badge {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 6px;
}
/* Encabezado de día */
.dia-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #00c46a;
    border-bottom: 1px solid rgba(0,196,106,0.3);
    padding-bottom: 4px;
    margin-bottom: 12px;
    margin-top: 4px;
}
/* Scroll horizontal para la semana de entrenamientos */
.semana-scroll-wrapper {
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 12px;
    margin: 0 -1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
.semana-scroll-wrapper::-webkit-scrollbar {
    height: 8px;
}
.semana-scroll-wrapper::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
}
.semana-scroll-wrapper::-webkit-scrollbar-thumb {
    background: rgba(0,196,106,0.4);
    border-radius: 4px;
}
.semana-scroll-wrapper::-webkit-scrollbar-thumb:hover {
    background: rgba(0,196,106,0.7);
}
/* Forzar que las columnas de streamlit dentro del wrapper no se achiquen */
.semana-scroll-wrapper [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow: visible !important;
    min-width: max-content;
}
.semana-scroll-wrapper [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 320px !important;
    flex: 0 0 320px !important;
}
/* Métricas de asistencia */
.metric-pill {
    display: inline-block;
    border-radius: 20px;
    padding: 6px 18px;
    font-weight: 700;
    font-size: 1.1rem;
    margin-right: 8px;
}
.pill-verde    { background:rgba(0,196,106,0.15);  color:#00c46a; }
.pill-rojo     { background:rgba(255,75,75,0.15);   color:#ff4b4b; }
.pill-amarillo { background:rgba(255,214,0,0.15);   color:#ffd600; }
/* Tarjeta de jugador */
.jugador-card {
    background: #1c2333;
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    margin-bottom: 12px;
    cursor: pointer;
    transition: transform .15s, box-shadow .15s;
    border: 1px solid rgba(255,255,255,0.06);
}
.jugador-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}
.jugador-nombre {
    font-size: .9rem;
    font-weight: 700;
    color: #e8eaed;
    margin: 6px 0 2px;
}
.jugador-cat {
    font-size: .78rem;
    color: #8d9db6;
}
/* Sidebar */
section[data-testid="stSidebar"] { background: #111827; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CARGA DE DATOS
# ─────────────────────────────────────────────

def _sheet_url(sheet_name: str) -> str:
    """Construye la URL de exportación CSV para una hoja del Sheets."""
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )


@st.cache_data(ttl=300)  # Refresca cada 5 minutos
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """
    Carga una hoja del Google Sheets público como DataFrame.
    Parametros:
        sheet_name: nombre exacto de la hoja (sensible a mayúsculas/tildes)
    Retorna:
        DataFrame con los datos de la hoja, o DataFrame vacío si hay error.
    """
    url = _sheet_url(sheet_name)
    try:
        df = pd.read_csv(url)
        # Limpiar nombres de columna (espacios extra)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar '{sheet_name}': {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "jugador_perfil" not in st.session_state:
    st.session_state.jugador_perfil = None
if "tema" not in st.session_state:
    st.session_state.tema = "oscuro"   # valor inicial


# ─────────────────────────────────────────────
#  SIDEBAR — NAVEGACIÓN
# ─────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/football2.png",
        width=60,
    )
    st.markdown("## Excursionistas 2026")
    st.divider()

    seccion = st.radio(
        "Navegación",
        options=["🏠 Inicio", "📅 Entrenamientos", "👥 Plantel", "🟡 Asistencia", "⚽ Post-Partido"],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("🔄 Refrescar datos"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Datos actualizados cada 5 min.")


# ─────────────────────────────────────────────
#  HELPER: carga todos los sheets de una vez
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def cargar_todo():
    plantel         = load_sheet("Plantel")
    sesiones        = load_sheet("Sesiones")
    tareas          = load_sheet("Tareas")
    asistencia      = load_sheet("Asistencia_Entrenamiento")
    partidos        = load_sheet("Partidos")
    postpartido     = load_sheet("PostPartido")
    entrenamientos  = load_sheet("Entrenamientos_Dia")   # nuevo
    return plantel, sesiones, tareas, asistencia, partidos, postpartido, entrenamientos


plantel, sesiones, tareas, asistencia, partidos, postpartido, entrenamientos = cargar_todo()


# ─────────────────────────────────────────────
#  HELPER: normalizar columna fecha
# ─────────────────────────────────────────────

def parse_fecha(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, dayfirst=True, errors="coerce")


# helper para leer categoría (admite acento o sin acento en el nombre de columna)
def get_categoria(row):
    for col in ["categoría", "categoria", "anio_nac"]:
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip() not in ("", "nan"):
            return str(row[col]).strip()
    return "—"


# ══════════════════════════════════════════════
#  🏠  INICIO
# ══════════════════════════════════════════════

if seccion == "🏠 Inicio":
    st.title("⚽ Excursionistas — Reserva 2026")
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    # — Orden del día —
    hoy = pd.Timestamp(date.today())
    DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_hoy_nombre = DIAS_ES[hoy.weekday()].title()

    with col1:
        st.subheader("📋 Orden del día")
        # Buscar sesión de la semana actual
        tareas_hoy_html = ""
        encontrado = False
        if not sesiones.empty and not entrenamientos.empty and not tareas.empty:
            df_ses_h = sesiones.copy()
            df_ses_h["fecha_inicio_semana"] = parse_fecha(df_ses_h["fecha_inicio_semana"])
            df_ses_h = df_ses_h.dropna(subset=["fecha_inicio_semana"])
            # Sesión más reciente cuya fecha_inicio <= hoy
            ses_act = df_ses_h[df_ses_h["fecha_inicio_semana"] <= hoy].sort_values(
                "fecha_inicio_semana", ascending=False
            )
            if not ses_act.empty:
                id_ses_hoy = ses_act.iloc[0]["id_sesion"]
                ids_dia_hoy = entrenamientos.loc[
                    entrenamientos["id_sesion"] == id_ses_hoy, "id_entreno_dia"
                ].tolist()
                if ids_dia_hoy and "id_entreno_dia" in tareas.columns:
                    t_hoy = tareas[tareas["id_entreno_dia"].isin(ids_dia_hoy)].copy()
                    if "dia_semana" not in t_hoy.columns:
                        dias_map = entrenamientos[entrenamientos["id_entreno_dia"].isin(ids_dia_hoy)]
                        t_hoy = t_hoy.merge(dias_map[["id_entreno_dia", "dia_semana"]], on="id_entreno_dia", how="left")
                    t_hoy["dia_semana"] = t_hoy["dia_semana"].astype(str).str.strip().str.title()
                    t_hoy = t_hoy[t_hoy["dia_semana"] == dia_hoy_nombre].sort_values("orden")
                    if not t_hoy.empty:
                        encontrado = True
                        cards = ""
                        for _, t in t_hoy.iterrows():
                            nombre  = t.get("nombre_tarea", "Sin nombre")
                            tipo    = str(t.get("tipo", "")).strip()
                            mins    = t.get("tiempo_min", "")
                            descr_v = str(t.get("descrip_tarea", "")).strip()
                            colores = TIPO_COLORES.get(tipo, TIPO_DEFAULT)
                            bc = colores["border"]; bg = colores["bg"]; tc = colores["text"]
                            mins_str = f"{int(float(mins))} min" if pd.notna(mins) and str(mins).strip() not in ("", "nan") else ""
                            tipo_h = f"<span class='tipo-badge' style='background:{bg};color:{tc};'>{tipo}</span>" if tipo and tipo.lower() not in ("nan","none","") else ""
                            mins_h = f"⏱ {mins_str}" if mins_str else ""
                            meta_h = f"<div class='tarea-meta' style='margin-top:4px;'>{tipo_h}{mins_h}</div>" if (tipo_h or mins_h) else ""
                            desc_h = (f"<div style='font-size:0.83rem;color:#e8eaed;font-weight:400;margin:5px 0 6px;line-height:1.4;'>{descr_v}</div>"
                                      if descr_v and descr_v.lower() not in ("nan","none","") else "")
                            cards += (f"<div class='tarea-card' style='background:{bg};border-left:4px solid {bc};'>"
                                      f"<div style='font-size:1.05rem;font-weight:700;color:#e8eaed;margin-bottom:2px;'>{nombre}</div>"
                                      f"{desc_h}{meta_h}</div>")
                        st.markdown(
                            f"<div style='background:{COLOR_CARD};border-radius:10px;padding:16px;'>"
                            f"<p style='color:#8d9db6;font-size:.85rem;margin:0 0 10px;'>📆 {dia_hoy_nombre}</p>"
                            f"{cards}</div>",
                            unsafe_allow_html=True,
                        )
        if not encontrado:
            st.info(f"No hay entrenamiento registrado para hoy ({dia_hoy_nombre}).")

    # — Próximo partido —
    with col2:
        st.subheader("🏟️ Próximo partido")
        if partidos.empty:
            st.info("Sin partidos registrados.")
        else:
            df_p = partidos.copy()
            df_p["fecha"] = parse_fecha(df_p["fecha"])
            hoy = pd.Timestamp(date.today())
            proximos = df_p[df_p["fecha"] >= hoy].sort_values("fecha")
            if proximos.empty:
                st.info("No hay partidos próximos cargados.")
            else:
                prox = proximos.iloc[0]
                dias_restantes = (prox["fecha"] - hoy).days
                nombre_dia = DIAS_ES[prox["fecha"].weekday()]
                horario = str(prox.get("horario", "")).strip()
                horario_html = f"&nbsp;⏰ {horario}" if horario and horario.lower() not in ("nan", "none", "") else ""
                st.markdown(f"""
                <div style='background:{COLOR_CARD};border-radius:10px;padding:20px;'>
                    <p style='color:#8d9db6;font-size:.85rem;margin:0'>Rival</p>
                    <p style='font-size:1.8rem;font-weight:800;color:{COLOR_VERDE};margin:0'>
                        {prox.get('rival','—')}
                    </p>
                    <p style='color:{COLOR_TEXTO};margin:4px 0 0;'>
                        📅 <b>{nombre_dia}</b>{horario_html}
                        &nbsp;|&nbsp; {prox.get('torneo','—')}
                    </p>
                    <p style='color:{COLOR_NARANJA};font-weight:600;margin-top:6px'>
                        ⏳ {dias_restantes} día{'s' if dias_restantes != 1 else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  📅  ENTRENAMIENTOS
# ══════════════════════════════════════════════

elif seccion == "📅 Entrenamientos":
    st.title("📅 Entrenamientos")
    st.markdown("---")

    if sesiones.empty or tareas.empty:
        st.warning("No hay datos de sesiones o tareas disponibles.")
    else:
        # ── Preparar fechas ─────────────────────────────────────────
        hoy = pd.Timestamp(date.today())
        df_ses_tmp = sesiones.copy()
        df_ses_tmp["fecha_inicio_semana"] = parse_fecha(df_ses_tmp["fecha_inicio_semana"])
        df_ses_tmp = df_ses_tmp.dropna(subset=["fecha_inicio_semana"])
        df_ses_tmp["mes"]  = df_ses_tmp["fecha_inicio_semana"].dt.month
        df_ses_tmp["anio"] = df_ses_tmp["fecha_inicio_semana"].dt.year

        MESES_ES = {
            1: "Enero", 2: "Febrero", 3: "Marzo",    4: "Abril",
            5: "Mayo",  6: "Junio",   7: "Julio",    8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
        }

        # Meses disponibles ordenados cronológicamente
        meses_disp  = sorted(df_ses_tmp[["anio", "mes"]].drop_duplicates().itertuples(index=False))
        meses_labels = [
            MESES_ES[m.mes] + (f" {m.anio}" if m.anio != hoy.year else "")
            for m in meses_disp
        ]
        meses_keys = [(m.anio, m.mes) for m in meses_disp]

        # Pre-seleccionar mes actual (o el más reciente pasado)
        mes_actual_key = (hoy.year, hoy.month)
        if mes_actual_key in meses_keys:
            idx_mes = meses_keys.index(mes_actual_key)
        else:
            pasados_mes = [(i, k) for i, k in enumerate(meses_keys) if k <= mes_actual_key]
            idx_mes = pasados_mes[-1][0] if pasados_mes else 0

        col_mes, _ = st.columns([2, 3])
        with col_mes:
            mes_label_sel = st.selectbox("📆 Mes", options=meses_labels, index=idx_mes)
        mes_sel_key = meses_keys[meses_labels.index(mes_label_sel)]

        # ── Semanas del mes seleccionado ────────────────────────────
        ses_mes = df_ses_tmp[
            (df_ses_tmp["anio"] == mes_sel_key[0]) &
            (df_ses_tmp["mes"]  == mes_sel_key[1])
        ]
        semanas_disp = sorted(ses_mes["semana_num"].dropna().unique().tolist())

        if not semanas_disp:
            st.info("No hay semanas registradas para ese mes.")
        else:
            # Auto-seleccionar semana actual dentro del mes
            pasadas_mes = ses_mes[ses_mes["fecha_inicio_semana"] <= hoy].sort_values(
                "fecha_inicio_semana", ascending=False
            )
            semana_actual = pasadas_mes.iloc[0]["semana_num"] if not pasadas_mes.empty else semanas_disp[0]
            idx_sem = semanas_disp.index(semana_actual) if semana_actual in semanas_disp else 0

            semana_sel = st.selectbox(
                "Seleccioná la semana",
                options=semanas_disp,
                index=idx_sem,
                format_func=lambda x: f"Semana {int(x)}",
            )

            # ── Filtrar sesión ──────────────────────────────────────
            sesion_sem = sesiones[sesiones["semana_num"] == semana_sel]
            if sesion_sem.empty:
                st.info("Sin sesión para esa semana.")
            else:
                id_sesion_sel = sesion_sem.iloc[0]["id_sesion"]
                tipo_sem      = sesion_sem.iloc[0].get("tipo_semana", "")
                fecha_ini     = parse_fecha(
                    pd.Series([sesion_sem.iloc[0]["fecha_inicio_semana"]])
                ).iloc[0]

                cols_info = st.columns(3)
                cols_info[0].metric("Semana", int(semana_sel))
                cols_info[1].metric("Tipo", tipo_sem if tipo_sem else "—")
                cols_info[2].metric(
                    "Inicio",
                    fecha_ini.strftime("%d/%m/%Y") if pd.notna(fecha_ini) else "—",
                )
                st.markdown("---")

                # ── Días de entrenamiento ───────────────────────────
                if not entrenamientos.empty and "id_sesion" in entrenamientos.columns:
                    dias_semana = entrenamientos[
                        entrenamientos["id_sesion"] == id_sesion_sel
                    ].copy()
                else:
                    dias_semana = pd.DataFrame()

                if dias_semana.empty:
                    st.info("No hay días de entrenamiento registrados para esta semana.")
                else:
                    ids_dia = dias_semana["id_entreno_dia"].tolist()

                    if "id_entreno_dia" in tareas.columns:
                        tareas_sem = tareas[tareas["id_entreno_dia"].isin(ids_dia)].copy()
                        if "dia_semana" not in tareas_sem.columns:
                            tareas_sem = tareas_sem.merge(
                                dias_semana[["id_entreno_dia", "dia_semana"]],
                                on="id_entreno_dia",
                                how="left",
                            )
                    else:
                        tareas_sem = (
                            tareas[tareas["id_sesion"] == id_sesion_sel].copy()
                            if "id_sesion" in tareas.columns else pd.DataFrame()
                        )

                    if tareas_sem.empty:
                        st.info("No hay tareas cargadas para esta semana.")
                    else:
                        tareas_sem["dia_semana"] = tareas_sem["dia_semana"].astype(str).str.strip().str.title()
                        tareas_sem = tareas_sem[
                            ~tareas_sem["dia_semana"].str.lower().isin(["nan", "none", ""])
                        ]

                        st.markdown("<div class='semana-scroll-wrapper'>", unsafe_allow_html=True)
                        cols_dias = st.columns(7, gap="medium")
                        for col_widget, dia in zip(cols_dias, DIAS_ORDEN):
                            with col_widget:
                                st.markdown(f"<div class='dia-header'>📆 {dia}</div>", unsafe_allow_html=True)
                                if dia in tareas_sem["dia_semana"].values:
                                    tareas_dia = (
                                        tareas_sem[tareas_sem["dia_semana"] == dia]
                                        .sort_values("orden")
                                    )
                                    for _, t in tareas_dia.iterrows():
                                        nombre = t.get("nombre_tarea", "Sin nombre")
                                        tipo   = str(t.get("tipo", "")).strip()
                                        mins   = t.get("tiempo_min", "")
                                        yt_url = str(t.get("link_youtube", "")).strip()

                                        colores = TIPO_COLORES.get(tipo, TIPO_DEFAULT)
                                        border_color = colores["border"]
                                        bg_color     = colores["bg"]
                                        text_color   = colores["text"]

                                        mins_str  = f"{int(float(mins))} min" if pd.notna(mins) and str(mins).strip() not in ("", "nan") else ""
                                        tipo_html = (
                                            f"<span class='tipo-badge' style='background:{bg_color};color:{text_color};'>"
                                            f"{tipo}</span>"
                                        ) if tipo and tipo.lower() not in ("nan", "none", "") else ""
                                        mins_html = f"⏱ {mins_str}" if mins_str else ""

                                        meta_html = (
                                            f"<div class='tarea-meta' style='margin-top:4px;'>{tipo_html}{mins_html}</div>"
                                        ) if (tipo_html or mins_html) else ""

                                        descr_val = str(t.get("descrip_tarea", "")).strip()
                                        descr_html = (
                                            f"<div style='font-size:0.83rem;color:#e8eaed;font-weight:400;"
                                            f"margin:5px 0 6px;line-height:1.4;'>{descr_val}</div>"
                                        ) if descr_val and descr_val.lower() not in ("nan", "none", "") else ""

                                        yt_html = (
                                            f"<div style='margin-top:8px;'>"
                                            f"<a href='{yt_url}' target='_blank' "
                                            f"style='font-size:0.8rem;color:#38bdf8;text-decoration:none;'>"
                                            f"▶ Ver vídeo</a></div>"
                                        ) if yt_url and yt_url.lower() not in ("", "nan", "none") else ""

                                        st.markdown(
                                            f"<div class='tarea-card' style='background:{bg_color};border-left:4px solid {border_color};'>"
                                            f"<div style='font-size:1.05rem;font-weight:700;color:#e8eaed;margin-bottom:2px;'>{nombre}</div>"
                                            f"{descr_html}"
                                            f"{meta_html}"
                                            f"{yt_html}"
                                            f"</div>",
                                            unsafe_allow_html=True,
                                        )
                                else:
                                    st.caption("Sin tareas")
                        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  👥  PLANTEL
# ══════════════════════════════════════════════

elif seccion == "👥 Plantel":

    # ── Sub-vista: perfil individual ──────────────────────────────
    if st.session_state.jugador_perfil is not None:
        jug_nombre = st.session_state.jugador_perfil
        if st.button("← Volver al plantel"):
            st.session_state.jugador_perfil = None
            st.rerun()

        if not plantel.empty and jug_nombre in plantel["nombre"].values:
            jug    = plantel[plantel["nombre"] == jug_nombre].iloc[0]
            id_jug = jug["id_jugador"]

            st.title(f"👤 {jug['nombre']}")
            st.markdown("---")

            col_foto, col_datos = st.columns([1, 3], gap="large")

            with col_foto:
                foto_url = str(jug.get("foto_url", "")).strip()
                if foto_url and foto_url.lower() not in ("nan", "none", ""):
                    st.image(foto_url, width=200)
                else:
                    st.markdown(
                        f"<div style='width:180px;height:180px;background:{COLOR_CARD};"
                        f"border-radius:16px;display:flex;align-items:center;"
                        f"justify-content:center;font-size:5rem;'>👤</div>",
                        unsafe_allow_html=True,
                    )

            with col_datos:
                col_a, col_b = st.columns(2)
                col_a.markdown(f"**Posición:** {jug.get('posicion','—')}")
                col_b.markdown(f"**Categoría:** {get_categoria(jug)}")

                # Conteo de asistencia
                if not asistencia.empty:
                    ast_jug      = asistencia[asistencia["id_jugador"] == id_jug]
                    presente     = int((ast_jug["estado"] == "Presente").sum())
                    ausente      = int((ast_jug["estado"] == "Ausente").sum())
                    diferenciado = int((ast_jug["estado"] == "Diferenciado").sum())
                    total        = presente + ausente + diferenciado

                    st.markdown("#### 📊 Asistencia a entrenamientos")
                    st.markdown(
                        f"<span class='metric-pill pill-verde'>✅ Presente: {presente}</span>"
                        f"<span class='metric-pill pill-rojo'>❌ Ausente: {ausente}</span>"
                        f"<span class='metric-pill pill-amarillo'>⚠️ Diferenciado: {diferenciado}</span>",
                        unsafe_allow_html=True,
                    )
                    if total > 0:
                        fig_pie = px.pie(
                            values=[presente, ausente, diferenciado],
                            names=["Presente", "Ausente", "Diferenciado"],
                            color_discrete_sequence=[COLOR_VERDE, "#ff4b4b", "#ffd600"],
                            hole=0.45,
                        )
                        fig_pie.update_layout(
                            margin=dict(t=10, b=10, l=10, r=10),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            legend=dict(font=dict(color="#e8eaed")),
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Sin datos de asistencia.")

                # Estadísticas de partidos
                st.markdown("#### ⚽ Estadísticas de partidos")
                if not postpartido.empty:
                    pp_jug = postpartido[postpartido["id_jugador"] == id_jug].copy()
                    if not pp_jug.empty:
                        for col_pp in ["minutos", "goles", "asistencias"]:
                            if col_pp in pp_jug.columns:
                                pp_jug[col_pp] = pd.to_numeric(pp_jug[col_pp], errors="coerce").fillna(0)
                        mc1, mc2, mc3, mc4 = st.columns(4)
                        mc1.metric("Partidos",    len(pp_jug))
                        mc2.metric("Minutos",     int(pp_jug["minutos"].sum()) if "minutos" in pp_jug.columns else "—")
                        mc3.metric("Goles",       int(pp_jug["goles"].sum())   if "goles" in pp_jug.columns else "—")
                        mc4.metric("Asistencias", int(pp_jug["asistencias"].sum()) if "asistencias" in pp_jug.columns else "—")
                    else:
                        st.info("Sin estadísticas de partidos.")
                else:
                    st.info("Sin datos de postpartido.")

                with st.expander("📈 Más estadísticas (próximamente)"):
                    st.info("Aquí se agregarán métricas de rendimiento físico, posesión, pressing, etc.")

    # ── Vista principal: tarjetas por posición ────────────────────
    else:
        st.title("👥 Plantel")
        st.markdown("---")

        if plantel.empty:
            st.warning("No hay datos de plantel disponibles.")
        else:
            # Agrupar por posición (orden POSICIONES_ORDEN + el resto)
            posiciones_en_plantel = plantel["posicion"].dropna().unique().tolist()
            orden = [p for p in POSICIONES_ORDEN if p in posiciones_en_plantel]
            orden += [p for p in posiciones_en_plantel if p not in POSICIONES_ORDEN]

            CARDS_POR_FILA = 5

            for pos in orden:
                jugadores_pos = plantel[plantel["posicion"] == pos].reset_index(drop=True)
                emoji_pos  = POS_EMOJI.get(pos, "👤")
                titulo_pos = POS_PLURAL.get(pos, f"{pos}s")
                st.markdown(f"### {emoji_pos} {titulo_pos}")

                for fila_start in range(0, len(jugadores_pos), CARDS_POR_FILA):
                    fila = jugadores_pos.iloc[fila_start : fila_start + CARDS_POR_FILA]
                    cols_cards = st.columns(len(fila), gap="small")
                    for col_c, (_, jug_row) in zip(cols_cards, fila.iterrows()):
                        with col_c:
                            foto_url  = str(jug_row.get("foto_url", "")).strip()
                            categoria = get_categoria(jug_row)
                            nombre    = jug_row.get("nombre", "")

                            # Foto o avatar
                            if foto_url and foto_url.lower() not in ("nan", "none", ""):
                                st.image(foto_url, use_column_width=True)
                            else:
                                st.markdown(
                                    "<div style='height:120px;background:#1c2333;"
                                    "border-radius:10px;display:flex;align-items:center;"
                                    "justify-content:center;font-size:3rem;'>👤</div>",
                                    unsafe_allow_html=True,
                                )

                            st.markdown(
                                f"<div style='text-align:center;padding:4px 0;'>"
                                f"<div style='font-weight:700;color:#e8eaed;font-size:.9rem;'>{nombre}</div>"
                                f"<div style='color:#8d9db6;font-size:.78rem;'>{categoria}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                            # Botón para ingresar al perfil
                            if st.button("Ver perfil", key=f"btn_{jug_row['id_jugador']}", use_container_width=True):
                                st.session_state.jugador_perfil = nombre
                                st.rerun()

                st.markdown("---")


# ══════════════════════════════════════════════
#  🟡  ASISTENCIA
# ══════════════════════════════════════════════

elif seccion == "🟡 Asistencia":
    st.title("🟡 Asistencia a Entrenamientos")
    st.markdown("---")

    if sesiones.empty or asistencia.empty:
        st.warning("No hay datos de sesiones o asistencia disponibles.")
    else:
        # ── Selector de semana ──────────────────────────────────────
        df_ses = sesiones.copy()
        df_ses["fecha_inicio_semana"] = parse_fecha(df_ses["fecha_inicio_semana"])
        df_ses["label"] = df_ses.apply(
            lambda r: f"Semana {int(r['semana_num'])}  —  "
                      f"{r['fecha_inicio_semana'].strftime('%d/%m/%Y') if pd.notna(r['fecha_inicio_semana']) else ''}",
            axis=1,
        )
        df_ses_sorted = df_ses.sort_values("fecha_inicio_semana", ascending=False)

        semana_label = st.selectbox(
            "Seleccioná la semana",
            options=df_ses_sorted["label"].tolist(),
        )
        id_sesion_sel = df_ses_sorted.loc[
            df_ses_sorted["label"] == semana_label, "id_sesion"
        ].values[0]

        # ── Resolver id_entreno_dia de esa semana ───────────────────
        if not entrenamientos.empty and "id_sesion" in entrenamientos.columns:
            ids_dia_semana = entrenamientos.loc[
                entrenamientos["id_sesion"] == id_sesion_sel, "id_entreno_dia"
            ].tolist()
        else:
            ids_dia_semana = []

        # ── Filtrar asistencia ───────────────────────────────────────
        if "id_entreno_dia" in asistencia.columns and ids_dia_semana:
            ast_fil = asistencia[asistencia["id_entreno_dia"].isin(ids_dia_semana)].copy()
        elif "id_sesion" in asistencia.columns:
            # fallback: la tabla aún tiene id_sesion directamente
            ast_fil = asistencia[asistencia["id_sesion"] == id_sesion_sel].copy()
        else:
            ast_fil = pd.DataFrame()

        if ast_fil.empty:
            st.info("Sin datos de asistencia para este día.")
        else:
            # Join con plantel para mostrar nombres
            if not plantel.empty:
                ast_fil = ast_fil.merge(
                    plantel[["id_jugador", "nombre", "posicion"]],
                    on="id_jugador",
                    how="left",
                )

            # Métricas rápidas
            presente     = int((ast_fil["estado"] == "Presente").sum())
            ausente      = int((ast_fil["estado"] == "Ausente").sum())
            diferenciado = int((ast_fil["estado"] == "Diferenciado").sum())
            total        = len(ast_fil)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", total)
            c2.metric("✅ Presentes",     presente)
            c3.metric("❌ Ausentes",      ausente)
            c4.metric("⚠️ Diferenciados", diferenciado)

            st.markdown("---")

            col_tabla, col_grafico = st.columns([3, 2], gap="large")

            with col_tabla:
                st.subheader("📋 Detalle")
                cols_vis = [c for c in ["nombre", "posicion", "estado"] if c in ast_fil.columns]

                def color_estado(val):
                    colores = {
                        "Presente": "color: #00c46a; font-weight:700",
                        "Ausente": "color: #ff4b4b; font-weight:700",
                        "Diferenciado": "color: #ffd600; font-weight:700",
                    }
                    return colores.get(val, "")

                styled = (
                    ast_fil[cols_vis]
                    .sort_values("estado")
                    .style.applymap(color_estado, subset=["estado"])
                )
                st.dataframe(styled, use_container_width=True, hide_index=True)

            with col_grafico:
                st.subheader("📊 Distribución")
                fig_bar = px.bar(
                    x=["Presente", "Ausente", "Diferenciado"],
                    y=[presente, ausente, diferenciado],
                    color=["Presente", "Ausente", "Diferenciado"],
                    color_discrete_map={
                        "Presente": COLOR_VERDE,
                        "Ausente": "#ff4b4b",
                        "Diferenciado": "#ffd600",
                    },
                    labels={"x": "Estado", "y": "Jugadores"},
                    text_auto=True,
                )
                fig_bar.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8eaed"),
                    margin=dict(t=10, b=10),
                )
                fig_bar.update_xaxes(showgrid=False)
                fig_bar.update_yaxes(gridcolor="rgba(255,255,255,0.07)")
                st.plotly_chart(fig_bar, use_container_width=True)

                fig_pie = px.pie(
                    values=[presente, ausente, diferenciado],
                    names=["Presente", "Ausente", "Diferenciado"],
                    color_discrete_sequence=[COLOR_VERDE, "#ff4b4b", "#ffd600"],
                    hole=0.4,
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8eaed"),
                    margin=dict(t=10, b=10),
                    legend=dict(font=dict(color="#e8eaed")),
                )
                st.plotly_chart(fig_pie, use_container_width=True)


# ══════════════════════════════════════════════
#  ⚽  POST-PARTIDO
# ══════════════════════════════════════════════

elif seccion == "⚽ Post-Partido":
    st.title("⚽ Post-Partido")
    st.markdown("---")

    if partidos.empty or postpartido.empty:
        st.warning("No hay datos de partidos o estadísticas disponibles.")
    else:
        df_par = partidos.copy()
        df_par["fecha"] = parse_fecha(df_par["fecha"])
        df_par["label"] = df_par.apply(
            lambda r: f"{r['fecha'].strftime('%d/%m/%Y') if pd.notna(r['fecha']) else '—'}  vs  "
                      f"{r.get('rival','?')}  ({r.get('torneo','—')})",
            axis=1,
        )
        df_par_sorted = df_par.sort_values("fecha", ascending=False)

        partido_label = st.selectbox("Seleccioná el partido", df_par_sorted["label"].tolist())
        id_partido_sel = df_par_sorted.loc[
            df_par_sorted["label"] == partido_label, "id_partido"
        ].values[0]

        # Filtrar post-partido
        pp_fil = postpartido[postpartido["id_partido"] == id_partido_sel].copy()

        if pp_fil.empty:
            st.info("Sin estadísticas para este partido.")
        else:
            # Join con plantel
            if not plantel.empty:
                pp_fil = pp_fil.merge(
                    plantel[["id_jugador", "nombre", "posicion"]],
                    on="id_jugador",
                    how="left",
                )

            # Convertir numéricas
            for col in ["minutos", "goles", "asistencias"]:
                if col in pp_fil.columns:
                    pp_fil[col] = pd.to_numeric(pp_fil[col], errors="coerce").fillna(0).astype(int)

            pp_fil = pp_fil.sort_values("minutos", ascending=False)

            # — Tabla —
            st.subheader("📋 Estadísticas del partido")
            cols_vis = [c for c in ["nombre", "posicion", "minutos", "goles", "asistencias"] if c in pp_fil.columns]
            st.dataframe(pp_fil[cols_vis], use_container_width=True, hide_index=True)

            st.markdown("---")

            # — Gráficos —
            st.subheader("📊 Gráficos")

            tab_min, tab_gol, tab_ast = st.tabs(["⏱ Minutos", "⚽ Goles", "🅰️ Asistencias"])

            def bar_chart(df, col_y, title, color):
                """Helper para gráfico de barras horizontales."""
                df_plot = df[["nombre", col_y]].sort_values(col_y, ascending=True)
                fig = px.bar(
                    df_plot,
                    x=col_y,
                    y="nombre",
                    orientation="h",
                    title=title,
                    color_discrete_sequence=[color],
                    labels={"nombre": "", col_y: ""},
                    text_auto=True,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8eaed"),
                    margin=dict(t=40, b=10, l=10, r=10),
                    height=max(300, 30 * len(df_plot)),
                )
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)")
                return fig

            with tab_min:
                if "minutos" in pp_fil.columns:
                    st.plotly_chart(
                        bar_chart(pp_fil, "minutos", "Minutos jugados", COLOR_VERDE),
                        use_container_width=True,
                    )

            with tab_gol:
                if "goles" in pp_fil.columns:
                    goleadores = pp_fil[pp_fil["goles"] > 0]
                    if goleadores.empty:
                        st.info("Sin goles registrados en este partido.")
                    else:
                        st.plotly_chart(
                            bar_chart(goleadores, "goles", "Goles", COLOR_NARANJA),
                            use_container_width=True,
                        )

            with tab_ast:
                if "asistencias" in pp_fil.columns:
                    asistidores = pp_fil[pp_fil["asistencias"] > 0]
                    if asistidores.empty:
                        st.info("Sin asistencias registradas en este partido.")
                    else:
                        st.plotly_chart(
                            bar_chart(asistidores, "asistencias", "Asistencias", "#a78bfa"),
                            use_container_width=True,
                        )

            # — Resumen global del partido —
            st.markdown("---")
            st.subheader("📈 Resumen global")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Jugadores",   len(pp_fil))
            rc2.metric("Min. totales", int(pp_fil["minutos"].sum()) if "minutos" in pp_fil.columns else "—")
            rc3.metric("Goles",        int(pp_fil["goles"].sum())   if "goles"   in pp_fil.columns else "—")
            rc4.metric("Asistencias",  int(pp_fil["asistencias"].sum()) if "asistencias" in pp_fil.columns else "—")
