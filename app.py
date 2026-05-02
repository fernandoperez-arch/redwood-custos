import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, Image as RLImage,
)
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io, os
from datetime import datetime

st.set_page_config(
    page_title="RedWood | Precificação",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY  = "#10012D"
RUST  = "#742C25"
WHITE = "#FFFFFF"
CREAM = "#DED6D0"
LNAVY = "#1A2850"
CARD  = "#162040"
RUST2 = "#8B3A2A"
GREEN = "#2E7D55"

BASE   = os.path.dirname(os.path.abspath(__file__))
LOGO_H = os.path.join(BASE, "assets", "logo_redwood_white.png")
LOGO_V = os.path.join(BASE, "assets", "logo_redwood_vertical.png")
FIB    = os.path.join(BASE, "assets", "fibonacci.png")

st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons&display=block" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');

/* Garante que classes de ícones do Streamlit usem a fonte certa (corrige texto "keyboard_double_arrow_left", "arrow_drop_down" etc.) */
.material-icons, .material-icons-outlined,
.material-symbols-outlined, .material-symbols-rounded,
[class*="material-symbols"], [class*="material-icons"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-style: normal !important;
    font-weight: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-smoothing: antialiased !important;
}}

*, body {{ font-family: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }}
.material-icons, .material-icons-outlined,
.material-symbols-outlined, .material-symbols-rounded {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}}

/* Background app com gradiente sutil */
.stApp, .main, [data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(ellipse at top left, {LNAVY}99 0%, transparent 50%),
        radial-gradient(ellipse at bottom right, {RUST}22 0%, transparent 50%),
        {NAVY} !important;
    background-attachment: fixed !important;
}}

/* Sidebar com gradiente refinado */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {LNAVY} 0%, {NAVY} 60%, {NAVY} 100%) !important;
    border-right: 1px solid {RUST}33 !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.3) !important;
}}
[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
[data-testid="stSidebar"] hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, {RUST}66, transparent) !important;
    margin: 14px 0 !important;
}}

/* Garante que botões de colapso usem o ícone correto */
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"] *,
button[kind="header"] *,
[data-testid="stSidebarHeader"] * {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
    font-feature-settings: 'liga' on !important;
    -webkit-font-feature-settings: 'liga' on !important;
}}
/* Fallback: torna invisível texto cru de ícones se o nome aparece em forma extensa  */
span[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded' !important;
    font-feature-settings: 'liga' !important;
}}

/* Wrapper do fibonacci no sidebar — deixa discreto e centralizado */
.rw-fib-wrap {{
    opacity: 0.28;
    margin: 8px auto 4px auto;
    filter: drop-shadow(0 0 6px {RUST}33);
    transition: opacity 0.3s ease;
}}
.rw-fib-wrap:hover {{ opacity: 0.55; }}

/* Tabs — mais polidas, com gradiente e indicador */
.stTabs [data-baseweb="tab-list"] {{
    background: linear-gradient(135deg, {LNAVY}, {CARD}) !important;
    border: 1px solid {RUST}33 !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 4px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25) !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {CREAM} !important;
    background-color: transparent !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: {RUST}22 !important;
    color: {WHITE} !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {RUST}, {RUST2}) !important;
    color: {WHITE} !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px {RUST}66 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ background-color: transparent !important; padding-top: 24px !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

/* Inputs — focus com glow */
.stNumberInput input, .stTextInput input, .stTextArea textarea {{
    background-color: {LNAVY} !important;
    color: {WHITE} !important;
    border: 1px solid {RUST}55 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
}}
.stNumberInput input:focus, .stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {RUST} !important;
    box-shadow: 0 0 0 3px {RUST}33 !important;
    outline: none !important;
}}
.stNumberInput label, .stTextInput label, .stTextArea label,
.stSelectbox label, .stSlider label {{
    color: {CREAM} !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.2px !important;
}}
div[data-testid="stSelectbox"] > div > div {{
    background-color: {LNAVY} !important;
    color: {WHITE} !important;
    border: 1px solid {RUST}55 !important;
    border-radius: 10px !important;
}}

/* Slider — track e thumb com cores da marca */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {RUST} !important;
    border: 2px solid {WHITE} !important;
    box-shadow: 0 2px 8px {RUST}88 !important;
}}
.stSlider [data-baseweb="slider"] > div:nth-child(2) > div:first-child {{
    background: linear-gradient(90deg, {RUST}, {RUST2}) !important;
}}

/* Botões — visualmente impecáveis */
.stButton > button, .stDownloadButton > button {{
    background: linear-gradient(135deg, {RUST} 0%, {RUST2} 100%) !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 22px !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    box-shadow:
        0 4px 14px {RUST}55,
        0 1px 0 rgba(255,255,255,0.1) inset !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}}
.stButton > button::before, .stDownloadButton > button::before {{
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: -100% !important;
    width: 100% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent) !important;
    transition: left 0.5s !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow:
        0 8px 24px {RUST}88,
        0 1px 0 rgba(255,255,255,0.15) inset !important;
    filter: brightness(1.08) !important;
}}
.stButton > button:hover::before, .stDownloadButton > button:hover::before {{ left: 100% !important; }}
.stButton > button:active, .stDownloadButton > button:active {{
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px {RUST}66 !important;
}}

/* Métricas — cards refinados com hover */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, {CARD} 0%, {LNAVY} 100%) !important;
    border: 1px solid {RUST}44 !important;
    border-radius: 14px !important;
    padding: 18px 16px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
    transition: all 0.3s ease !important;
}}
[data-testid="metric-container"]:hover {{
    border-color: {RUST}88 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
}}
[data-testid="metric-container"] label {{
    color: {CREAM} !important;
    font-size: 0.72em !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    font-weight: 600 !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {WHITE} !important;
    font-size: 1.55em !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
}}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color: #5DBA8A !important; }}

/* Cards customizados RedWood */
.rw-card {{
    background: linear-gradient(135deg, {CARD} 0%, {LNAVY} 100%);
    border: 1px solid {RUST}44;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    transition: all 0.25s ease;
}}
.rw-card:hover {{
    border-color: {RUST}88;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}}
.rw-card-green {{
    background: linear-gradient(135deg, #0D2B1A 0%, #1A4030 100%);
    border: 1px solid {GREEN}66;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 4px 14px rgba(46,125,85,0.18);
    transition: all 0.25s ease;
}}
.rw-card-green:hover {{
    border-color: {GREEN};
    box-shadow: 0 6px 22px rgba(46,125,85,0.3);
}}

/* Header de seção */
.rw-section {{
    background: linear-gradient(90deg, {RUST} 0%, {RUST2} 50%, {RUST}88 100%);
    color: {WHITE};
    padding: 11px 22px;
    border-radius: 10px;
    font-size: 0.95em;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin: 22px 0 12px 0;
    box-shadow: 0 4px 14px {RUST}55;
    border-left: 4px solid {WHITE}55;
}}

/* Total card — destaque máximo com brilho */
.rw-total {{
    background: linear-gradient(135deg, {RUST} 0%, {RUST2} 50%, #5C2018 100%);
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    margin: 20px 0;
    box-shadow:
        0 12px 40px {RUST}66,
        0 0 0 1px {RUST}88,
        inset 0 1px 0 rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}}
.rw-total::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    animation: shimmer 8s ease-in-out infinite;
    pointer-events: none;
}}
@keyframes shimmer {{
    0%, 100% {{ transform: translate(-30%, -30%); }}
    50% {{ transform: translate(30%, 30%); }}
}}
.rw-total h2 {{ color: {WHITE} !important; margin: 0 !important; font-size: 2.6em !important; font-weight: 800 !important; letter-spacing: -1px !important; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
.rw-total p {{ color: {CREAM} !important; margin: 6px 0 0 0 !important; font-size: 0.95em !important; }}

/* Gain card — verde com brilho sutil */
.rw-gain {{
    background: linear-gradient(135deg, {GREEN}33 0%, {GREEN}11 100%);
    border: 1px solid {GREEN}66;
    border-radius: 16px;
    padding: 26px;
    text-align: center;
    margin: 18px 0;
    box-shadow: 0 8px 28px rgba(46,125,85,0.25), inset 0 1px 0 rgba(93,186,138,0.15);
}}
.rw-gain h2 {{ color: #5DBA8A !important; margin: 0 !important; font-size: 2.4em !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }}
.rw-gain p {{ color: {CREAM} !important; margin: 6px 0 0 0 !important; }}

/* Info banner */
.rw-info {{
    background: {LNAVY};
    border-left: 3px solid {RUST};
    padding: 12px 16px;
    border-radius: 0 10px 10px 0;
    margin: 8px 0;
}}
.rw-info p {{ color: {CREAM} !important; margin: 0 !important; font-size: 0.9em !important; }}

/* Badge */
.badge {{
    display: inline-block;
    background: linear-gradient(135deg, {RUST}33, {RUST}55);
    color: {WHITE};
    border: 1px solid {RUST}88;
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.76em;
    font-weight: 600;
    margin: 2px;
}}

/* Tipografia */
h1 {{
    color: {WHITE} !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    background: linear-gradient(135deg, {WHITE} 0%, {CREAM} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
h2, h3 {{ color: {WHITE} !important; font-weight: 700 !important; }}
p, .stMarkdown p {{ color: {WHITE}; }}
hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, {RUST}66, transparent) !important;
    margin: 20px 0 !important;
}}

/* Caption */
[data-testid="stCaptionContainer"], .stCaption, small {{
    color: {CREAM} !important;
    opacity: 0.85 !important;
}}

/* Expander/accordion (caso use) */
.streamlit-expanderHeader, [data-testid="stExpander"] {{
    background: {LNAVY} !important;
    border: 1px solid {RUST}44 !important;
    border-radius: 10px !important;
}}

/* Scrollbar custom */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {NAVY}; }}
::-webkit-scrollbar-thumb {{
    background: linear-gradient(180deg, {RUST}88, {RUST2}88);
    border-radius: 10px;
    border: 2px solid {NAVY};
}}
::-webkit-scrollbar-thumb:hover {{ background: linear-gradient(180deg, {RUST}, {RUST2}); }}

/* Toolbar/header do streamlit — discreto */
[data-testid="stHeader"] {{ background: transparent !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}

/* Animação de entrada para cards */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.rw-card, .rw-card-green, .rw-total, .rw-gain, [data-testid="metric-container"] {{
    animation: fadeInUp 0.4s ease-out;
}}
</style>
""", unsafe_allow_html=True)

def fmt(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def fmt_h(h): return f"{h:.1f}h"

def custo_lista_ui(chave, placeholder="Novo item"):
    upd = []
    for i, c in enumerate(st.session_state[chave]):
        ca, cb, cc = st.columns([3, 2, 0.5])
        with ca: nome_c = st.text_input("", value=c["item"], key=f"{chave}_nome_{i}", label_visibility="collapsed")
        with cb: val_c  = st.number_input("", value=float(c["valor"]), min_value=0.0, step=10.0,
                                          key=f"{chave}_val_{i}", label_visibility="collapsed", format="%.2f")
        with cc: rem    = st.button("x", key=f"{chave}_del_{i}")
        if not rem: upd.append({"item": nome_c, "valor": val_c})
    st.session_state[chave] = upd
    na, nb, nc = st.columns([3, 2, 0.5])
    with na: n_item = st.text_input("", key=f"{chave}_n_item", placeholder=placeholder, label_visibility="collapsed")
    with nb: n_val  = st.number_input("", min_value=0.0, step=10.0, key=f"{chave}_n_val",
                                      label_visibility="collapsed", format="%.2f")
    with nc:
        st.write("")
        if st.button("+", key=f"{chave}_add"):
            if n_item.strip():
                st.session_state[chave].append({"item": n_item, "valor": n_val})
                st.rerun()
    total = sum(c["valor"] for c in st.session_state[chave])
    st.markdown(
        f"<div style='text-align:right;margin-top:4px;'>"
        f"<span style='color:{CREAM};font-size:0.82em;'>Total: </span>"
        f"<b style='color:{WHITE};font-size:0.95em;'>{fmt(total)}</b></div>",
        unsafe_allow_html=True)
    return total

def init_state():
    if "consultores" not in st.session_state:
        st.session_state["consultores"] = [{"nome": "Fernando Richard", "valor_hora": 300.0}]
    if "etapas" not in st.session_state:
        st.session_state["etapas"] = []
    if "custos_fixos" not in st.session_state:
        st.session_state["custos_fixos"] = [
            {"item": "Mensalidade Plataforma", "valor": 250.0},
            {"item": "Adobe Creative Cloud",   "valor":  50.0},
            {"item": "Claude (IA)",             "valor": 120.0},
            {"item": "Contador",                "valor": 400.0},
        ]
    if "custos_viagem" not in st.session_state:
        st.session_state["custos_viagem"] = [
            {"item": "Hospedagem",                        "valor": 0.0},
            {"item": "Passagem Aérea",                    "valor": 0.0},
            {"item": "Aluguel de Carro",                  "valor": 0.0},
            {"item": "Combustível",                       "valor": 0.0},
            {"item": "Ajuda de Custo (dentro do estado)", "valor": 0.0},
            {"item": "Ajuda de Custo (fora do estado)",   "valor": 0.0},
            {"item": "Outros Deslocamentos",              "valor": 0.0},
        ]
    if "custos_terceiros" not in st.session_state:
        st.session_state["custos_terceiros"] = []
    if "custos_marketing" not in st.session_state:
        st.session_state["custos_marketing"] = []

init_state()

def gerar_pdf_interno(empresa_nome, empresa_email, cliente_nome, projeto_nome,
                      etapas, consultores, custos_fixos,
                      custo_labor, fixos_alocados, valor_margem,
                      valor_total_proj, lucro_liq, margem_pct,
                      total_horas_proj, dados_cons,
                      mes_ref, ano_ref, logo_path,
                      custos_viagem=None, custos_terceiros=None, custos_marketing=None,
                      custo_extras=0.0, empresa_cnpj="", imposto=0.0, aliquota_imposto=0):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)
    C_NAVY  = colors.HexColor("#10012D")
    C_RUST  = colors.HexColor("#742C25")
    C_WHITE = colors.white
    C_CREAM = colors.HexColor("#DED6D0")
    C_LGRAY = colors.HexColor("#F4F2F0")
    C_DGRAY = colors.HexColor("#2A2A2A")
    C_GREEN = colors.HexColor("#2E7D55")
    styles  = getSampleStyleSheet()
    def sty(name, **kw): return ParagraphStyle(name, parent=styles["Normal"], **kw)
    s_title = sty("T",  fontSize=16, textColor=C_WHITE, fontName="Helvetica-Bold", spaceAfter=2)
    s_sub   = sty("S",  fontSize=10, textColor=C_CREAM, spaceAfter=1)
    s_sec   = sty("Se", fontSize=11, textColor=C_WHITE, fontName="Helvetica-Bold")
    s_tl    = sty("TL", fontSize=10, textColor=C_CREAM, alignment=TA_CENTER)
    s_tv    = sty("TV", fontSize=18, textColor=C_WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_tv2   = sty("TV2",fontSize=16, textColor=colors.HexColor("#5DBA8A"), fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_foot  = sty("F",  fontSize=8,  textColor=C_CREAM, alignment=TA_CENTER)
    W = A4[0] - 4*cm
    elems = []

    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=4.5*cm, height=3.5*cm, kind="proportional")
    else:
        logo = Paragraph("<b>RedWood</b>", sty("LH", textColor=C_WHITE, fontSize=18))

    fib_img = RLImage(FIB, width=3.8*cm, height=2.35*cm, kind="proportional") if os.path.exists(FIB) else Spacer(1, 1)

    cnpj_txt = f"CNPJ: {empresa_cnpj}  ·  " if empresa_cnpj else ""
    info = [
        Paragraph(empresa_nome or "RedWood Estratégia & Impacto", s_title),
        Paragraph(f"{empresa_email or ''}{'  ·  ' if empresa_email and empresa_cnpj else ''}{cnpj_txt.rstrip('  · ')}", s_sub),
        Spacer(1, 4),
        Paragraph("Relatório Interno de Custos e Ganhos",
                  sty("PT", fontSize=11, textColor=C_RUST, fontName="Helvetica-Bold")),
        Paragraph(f"Projeto: {projeto_nome or '—'}  ·  Cliente: {cliente_nome or '—'}  ·  {mes_ref}/{ano_ref}", s_sub),
    ]
    inner = Table([[logo, info, fib_img]], colWidths=[4.5*cm, W-8.5*cm, 4*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_NAVY), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),14), ("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(0,-1),10), ("LEFTPADDING",(1,0),(1,-1),20),
        ("RIGHTPADDING",(2,0),(2,-1),10), ("ALIGN",(2,0),(2,-1),"RIGHT"),
    ]))
    outer = Table([[inner]], colWidths=[W])
    outer.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),C_NAVY),("BOX",(0,0),(-1,-1),2,C_RUST)]))
    elems += [outer, Spacer(1, 0.5*cm)]

    def sec_hdr(text):
        t = Table([[Paragraph(text, s_sec)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C_RUST),
            ("LEFTPADDING",(0,0),(-1,-1),14),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        return t

    def dtbl(headers, rows, widths=None, last_bold=False):
        if not widths: widths = [W/len(headers)]*len(headers)
        data = [headers]+rows
        t = Table(data, colWidths=widths, repeatRows=1)
        s = [
            ("BACKGROUND",(0,0),(-1,0),C_NAVY), ("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,0),9),
            ("ALIGN",(0,0),(-1,0),"CENTER"),
            ("TOPPADDING",(0,0),(-1,0),9), ("BOTTOMPADDING",(0,0),(-1,0),9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_LGRAY,C_WHITE]),
            ("FONTSIZE",(0,1),(-1,-1),9), ("TEXTCOLOR",(0,1),(-1,-1),C_DGRAY),
            ("ALIGN",(-1,1),(-1,-1),"RIGHT"), ("ALIGN",(-2,1),(-2,-1),"RIGHT"),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#DDDDDD")),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,1),(-1,-1),6), ("BOTTOMPADDING",(0,1),(-1,-1),6),
            ("BOX",(0,0),(-1,-1),1,colors.HexColor("#CCCCCC")),
        ]
        if last_bold and rows:
            s += [
                ("BACKGROUND",(0,len(rows)),(-1,len(rows)),C_NAVY),
                ("TEXTCOLOR",(0,len(rows)),(-1,len(rows)),C_WHITE),
                ("FONTNAME",(0,len(rows)),(-1,len(rows)),"Helvetica-Bold"),
            ]
        t.setStyle(TableStyle(s))
        return t

    def pct_bar(pct):
        filled = max(1, int(pct / 5))
        bar = "█" * filled + "░" * (20 - filled)
        return f"{bar}  {pct:.1f}%"

    custos_viagem    = custos_viagem    or []
    custos_terceiros = custos_terceiros or []
    custos_marketing = custos_marketing or []
    tv = sum(c["valor"] for c in custos_viagem)
    tt = sum(c["valor"] for c in custos_terceiros)
    tm = sum(c["valor"] for c in custos_marketing)

    # 1. Resumo Financeiro com %
    elems.append(sec_hdr("1. COMPOSIÇÃO DE CUSTOS E RECEITA"))
    elems.append(Spacer(1, 0.2*cm))
    custo_base = custo_labor + fixos_alocados + custo_extras
    rows_comp = [
        ["Labor (Consultores)",   fmt(custo_labor),    f"{custo_labor/valor_total_proj*100:.1f}%"    if valor_total_proj else "0%"],
        ["Custos Fixos Rateados", fmt(fixos_alocados), f"{fixos_alocados/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"],
    ]
    if tv > 0:
        rows_comp.append(["Deslocamento & Viagem", fmt(tv), f"{tv/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
    if tt > 0:
        rows_comp.append(["Terceiros",  fmt(tt), f"{tt/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
    if tm > 0:
        rows_comp.append(["Marketing",  fmt(tm), f"{tm/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
    rows_comp += [
        ["Margem de Lucro",       fmt(valor_margem), f"{valor_margem/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"],
        [f"Impostos ({aliquota_imposto}%)", fmt(imposto), f"{imposto/valor_total_proj*100:.1f}%"  if valor_total_proj else "0%"],
        ["LUCRO LÍQUIDO",         fmt(lucro_liq),    f"{lucro_liq/valor_total_proj*100:.1f}%"    if valor_total_proj else "0%"],
        ["RECEITA TOTAL",         fmt(valor_total_proj), "100,0%"],
    ]
    t1 = dtbl(["Componente", "Valor (R$)", "% da Receita"], rows_comp,
              [9*cm, 4.5*cm, 3.5*cm], last_bold=True)
    elems += [t1, Spacer(1, 0.4*cm)]

    # 2. Ganhos por Consultor com %
    elems.append(sec_hdr("2. GANHOS POR CONSULTOR"))
    elems.append(Spacer(1, 0.2*cm))
    rows_cons = []
    for d in dados_cons:
        pct_lab  = (d["ganho"] / custo_labor * 100)  if custo_labor  else 0
        pct_rec  = (d["ganho"] / valor_total_proj * 100) if valor_total_proj else 0
        rows_cons.append([
            d["nome"],
            f"{d['horas']:.0f}h",
            fmt(d["valor_hora"]),
            fmt(d["ganho"]),
            f"{pct_lab:.1f}%",
            f"{pct_rec:.1f}%",
        ])
    rows_cons.append(["TOTAL", fmt_h(total_horas_proj), "—", fmt(custo_labor), "100,0%",
                       f"{custo_labor/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
    t2 = dtbl(["Consultor", "Horas", "R$/h", "Ganho Bruto", "% do Labor", "% da Receita"],
              rows_cons, [4*cm, 2*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm], last_bold=True)
    elems += [t2, Spacer(1, 0.4*cm)]

    # 3. Custos Fixos com %
    elems.append(sec_hdr("3. CUSTOS FIXOS MENSAIS RATEADOS"))
    elems.append(Spacer(1, 0.2*cm))
    total_fix_mes = sum(c["valor"] for c in custos_fixos)
    rows_fix = []
    for c in custos_fixos:
        pct_fix = (c["valor"] / total_fix_mes * 100) if total_fix_mes else 0
        pct_rec = (c["valor"] / valor_total_proj * 100) if valor_total_proj else 0
        rows_fix.append([c["item"], fmt(c["valor"]), f"{pct_fix:.1f}%", fmt(fixos_alocados * (c["valor"]/total_fix_mes) if total_fix_mes else 0), f"{pct_rec * (fixos_alocados/total_fix_mes if total_fix_mes else 0):.1f}%"])
    rows_fix.append(["TOTAL MENSAL", fmt(total_fix_mes), "100,0%", fmt(fixos_alocados), "—"])
    t3 = dtbl(["Item", "Custo Mensal", "% dos Fixos", "Rateado ao Projeto", "% da Receita"],
              rows_fix, [5.5*cm, 2.8*cm, 2.2*cm, 3.5*cm, 3*cm], last_bold=True)
    elems += [t3, Spacer(1, 0.4*cm)]

    # 4. Deslocamento & Viagem
    if tv > 0 or custos_viagem:
        elems.append(sec_hdr("4. DESLOCAMENTO & VIAGEM"))
        elems.append(Spacer(1, 0.2*cm))
        rows_v = [[c["item"], fmt(c["valor"]),
                   f"{c['valor']/tv*100:.1f}%" if tv else "0%",
                   f"{c['valor']/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"]
                  for c in custos_viagem if c["valor"] > 0]
        if rows_v:
            rows_v.append(["TOTAL", fmt(tv), "100,0%",
                           f"{tv/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
            t4 = dtbl(["Item", "Valor (R$)", "% Deslocamento", "% da Receita"],
                      rows_v, [7*cm, 3.5*cm, 3.5*cm, 3*cm], last_bold=True)
            elems.append(t4)
        elems.append(Spacer(1, 0.4*cm))

    # 5. Terceiros
    if tt > 0 or custos_terceiros:
        elems.append(sec_hdr("5. CUSTOS COM TERCEIROS"))
        elems.append(Spacer(1, 0.2*cm))
        rows_t = [[c["item"], fmt(c["valor"]),
                   f"{c['valor']/tt*100:.1f}%" if tt else "0%",
                   f"{c['valor']/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"]
                  for c in custos_terceiros if c["valor"] > 0]
        if rows_t:
            rows_t.append(["TOTAL", fmt(tt), "100,0%",
                           f"{tt/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
            t5 = dtbl(["Item", "Valor (R$)", "% Terceiros", "% da Receita"],
                      rows_t, [7*cm, 3.5*cm, 3.5*cm, 3*cm], last_bold=True)
            elems.append(t5)
        elems.append(Spacer(1, 0.4*cm))

    # 6. Marketing
    if tm > 0 or custos_marketing:
        elems.append(sec_hdr("6. CUSTOS DE MARKETING"))
        elems.append(Spacer(1, 0.2*cm))
        rows_m = [[c["item"], fmt(c["valor"]),
                   f"{c['valor']/tm*100:.1f}%" if tm else "0%",
                   f"{c['valor']/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"]
                  for c in custos_marketing if c["valor"] > 0]
        if rows_m:
            rows_m.append(["TOTAL", fmt(tm), "100,0%",
                           f"{tm/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"])
            t6 = dtbl(["Item", "Valor (R$)", "% Marketing", "% da Receita"],
                      rows_m, [7*cm, 3.5*cm, 3.5*cm, 3*cm], last_bold=True)
            elems.append(t6)
        elems.append(Spacer(1, 0.4*cm))

    # 7. Resultado final
    elems.append(sec_hdr("7. RESULTADO FINAL DA EMPRESA"))
    elems.append(Spacer(1, 0.2*cm))
    s_imp = sty("TI", fontSize=10, textColor=colors.HexColor("#CC4444"), alignment=TA_CENTER)
    s_imp_v = sty("TV3", fontSize=14, textColor=colors.HexColor("#CC4444"), fontName="Helvetica-Bold", alignment=TA_CENTER)
    tb = Table([
        [Paragraph("RECEITA TOTAL", s_tl), Paragraph(fmt(valor_total_proj), s_tv)],
        [Paragraph(f"IMPOSTOS ({aliquota_imposto}%)", s_imp), Paragraph(fmt(imposto), s_imp_v)],
        [Paragraph("LUCRO LÍQUIDO DA EMPRESA", sty("TL2", fontSize=10, textColor=colors.HexColor("#5DBA8A"), alignment=TA_CENTER)),
         Paragraph(fmt(lucro_liq), s_tv2)],
    ], colWidths=[W/2, W/2])
    tb.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(1,0),C_RUST),
        ("BACKGROUND",(0,1),(1,1),colors.HexColor("#2D0A0A")),
        ("BACKGROUND",(0,2),(1,2),colors.HexColor("#0D2B1A")),
        ("TOPPADDING",(0,0),(-1,-1),14), ("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),20), ("RIGHTPADDING",(0,0),(-1,-1),20),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEBELOW",(0,0),(-1,1),1,C_NAVY),
    ]))
    elems += [tb, Spacer(1, 0.3*cm)]

    elems.append(HRFlowable(width=W, thickness=1, color=C_RUST))
    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph(
        f"DOCUMENTO INTERNO CONFIDENCIAL  ·  {empresa_nome or 'RedWood'}  ·  "
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", s_foot))
    doc.build(elems)
    buffer.seek(0)
    return buffer.read()

def gerar_pdf_cliente(empresa_nome, empresa_email, cliente_nome, cliente_email,
                      projeto_nome, projeto_descricao, etapas, consultores,
                      valor_total, mes_ref, ano_ref, logo_path, observacoes,
                      empresa_cnpj=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)
    C_NAVY  = colors.HexColor("#10012D")
    C_RUST  = colors.HexColor("#742C25")
    C_WHITE = colors.white
    C_CREAM = colors.HexColor("#DED6D0")
    C_LGRAY = colors.HexColor("#F4F2F0")
    C_DGRAY = colors.HexColor("#2A2A2A")
    styles  = getSampleStyleSheet()
    def sty(name, **kw): return ParagraphStyle(name, parent=styles["Normal"], **kw)
    s_title = sty("T",  fontSize=18, textColor=C_WHITE, fontName="Helvetica-Bold", spaceAfter=2)
    s_sub   = sty("S",  fontSize=10, textColor=C_CREAM, spaceAfter=1)
    s_sec   = sty("Se", fontSize=11, textColor=C_WHITE, fontName="Helvetica-Bold")
    s_body  = sty("B",  fontSize=10, textColor=C_DGRAY, leading=14)
    s_tl    = sty("TL", fontSize=10, textColor=C_CREAM, alignment=TA_CENTER)
    s_tv    = sty("TV", fontSize=20, textColor=C_WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_foot  = sty("F",  fontSize=8,  textColor=C_CREAM, alignment=TA_CENTER)
    s_obs   = sty("O",  fontSize=9,  textColor=C_DGRAY, leading=14)
    W = A4[0] - 4*cm
    elems = []

    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=4.5*cm, height=3.5*cm, kind="proportional")
    else:
        logo = Paragraph("<b>RedWood</b>", sty("LH", textColor=C_WHITE, fontSize=18))

    fib_img = RLImage(FIB, width=3.8*cm, height=2.35*cm, kind="proportional") if os.path.exists(FIB) else Spacer(1, 1)

    cnpj_line = f"CNPJ: {empresa_cnpj}" if empresa_cnpj else ""
    info = [
        Paragraph(empresa_nome or "RedWood Estratégia & Impacto", s_title),
        Paragraph("  ·  ".join(filter(None, [empresa_email, cnpj_line])), s_sub),
        Spacer(1, 4),
        Paragraph("Proposta Técnica e Comercial",
                  sty("PT", fontSize=11, textColor=C_RUST, fontName="Helvetica-Bold")),
        Paragraph(f"{mes_ref} / {ano_ref}", s_sub),
    ]
    inner = Table([[logo, info, fib_img]], colWidths=[4.5*cm, W-8.5*cm, 4*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_NAVY), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),14), ("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(0,-1),10), ("LEFTPADDING",(1,0),(1,-1),20),
        ("RIGHTPADDING",(2,0),(2,-1),10), ("ALIGN",(2,0),(2,-1),"RIGHT"),
    ]))
    outer = Table([[inner]], colWidths=[W])
    outer.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_NAVY), ("BOX",(0,0),(-1,-1),2,C_RUST),
    ]))
    elems += [outer, Spacer(1, 0.5*cm)]

    def sec_hdr(text):
        t = Table([[Paragraph(text, s_sec)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C_RUST),
            ("LEFTPADDING",(0,0),(-1,-1),14),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        return t

    def dtbl(headers, rows, widths=None, last_bold=False):
        if not widths: widths = [W/len(headers)]*len(headers)
        data = [headers]+rows
        t = Table(data, colWidths=widths, repeatRows=1)
        s = [
            ("BACKGROUND",(0,0),(-1,0),C_NAVY), ("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,0),9),
            ("ALIGN",(0,0),(-1,0),"CENTER"),
            ("TOPPADDING",(0,0),(-1,0),9), ("BOTTOMPADDING",(0,0),(-1,0),9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_LGRAY,C_WHITE]),
            ("FONTSIZE",(0,1),(-1,-1),9), ("TEXTCOLOR",(0,1),(-1,-1),C_DGRAY),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#DDDDDD")),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,1),(-1,-1),6), ("BOTTOMPADDING",(0,1),(-1,-1),6),
            ("BOX",(0,0),(-1,-1),1,colors.HexColor("#CCCCCC")),
        ]
        if last_bold and rows:
            s += [
                ("BACKGROUND",(0,len(rows)),(-1,len(rows)),C_NAVY),
                ("TEXTCOLOR",(0,len(rows)),(-1,len(rows)),C_WHITE),
                ("FONTNAME",(0,len(rows)),(-1,len(rows)),"Helvetica-Bold"),
            ]
        t.setStyle(TableStyle(s))
        return t

    elems.append(sec_hdr("1. IDENTIFICAÇÃO"))
    elems.append(Spacer(1, 0.2*cm))
    id_rows = [
        ["Empresa Contratante", cliente_nome or "—"],
        ["E-mail / Contato",    cliente_email or "—"],
        ["Projeto",             projeto_nome or "—"],
    ]
    elems += [dtbl(["Campo","Informação"], id_rows, [5*cm, W-5*cm]), Spacer(1, 0.4*cm)]

    prox = 2
    if projeto_descricao:
        elems.append(sec_hdr(f"{prox}. DESCRIÇÃO DO PROJETO"))
        elems.append(Spacer(1, 0.2*cm))
        elems.append(Paragraph(projeto_descricao, s_body))
        elems.append(Spacer(1, 0.4*cm))
        prox += 1

    elems.append(sec_hdr(f"{prox}. EQUIPE TÉCNICA"))
    elems.append(Spacer(1, 0.2*cm))
    total_horas_proj = sum(sum(e["horas"].get(c["nome"],0) for c in consultores) for e in etapas)
    eq_rows = [[c["nome"], fmt_h(sum(e["horas"].get(c["nome"],0) for e in etapas))]
               for c in consultores if sum(e["horas"].get(c["nome"],0) for e in etapas) > 0]
    eq_rows.append(["TOTAL", fmt_h(total_horas_proj)])
    elems += [dtbl(["Consultor(a)","Horas"], eq_rows, [12*cm,5*cm], last_bold=True), Spacer(1,0.4*cm)]
    prox += 1

    if etapas:
        elems.append(sec_hdr(f"{prox}. ETAPAS DA CONSULTORIA"))
        elems.append(Spacer(1, 0.2*cm))
        et_rows = []
        for i, e in enumerate(etapas):
            horas_etapa = sum(e["horas"].get(c["nome"],0) for c in consultores)
            valor_etapa = sum(e["horas"].get(c["nome"],0)*c["valor_hora"] for c in consultores)
            et_rows.append([str(i+1), e["nome"], e.get("descricao",""), fmt_h(horas_etapa), fmt(valor_etapa)])
        elems += [dtbl(["Nº","Etapa","Descrição","Horas","Valor (R$)"], et_rows,
                       [1*cm,4*cm,7*cm,2.5*cm,2.5*cm]), Spacer(1,0.4*cm)]
        prox += 1

    elems.append(sec_hdr(f"{prox}. VALOR TOTAL DO PROJETO"))
    elems.append(Spacer(1, 0.2*cm))
    tb = Table([[Paragraph("VALOR TOTAL DA CONSULTORIA",s_tl), Paragraph(fmt(valor_total),s_tv)]],
               colWidths=[W/2,W/2])
    tb.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_RUST),
        ("TOPPADDING",(0,0),(-1,-1),18), ("BOTTOMPADDING",(0,0),(-1,-1),18),
        ("LEFTPADDING",(0,0),(-1,-1),20), ("RIGHTPADDING",(0,0),(-1,-1),20),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    elems += [tb, Spacer(1,0.4*cm)]

    if observacoes:
        prox += 1
        elems.append(sec_hdr(f"{prox}. OBSERVAÇÕES"))
        elems.append(Spacer(1, 0.2*cm))
        elems.append(Paragraph(observacoes, s_obs))
        elems.append(Spacer(1, 0.3*cm))

    elems.append(HRFlowable(width=W, thickness=1, color=C_RUST))
    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph(
        f"{empresa_nome or 'RedWood Estratégia & Impacto'}  ·  {empresa_email or ''}  ·  "
        f"Gerado em {datetime.now().strftime('%d/%m/%Y')}  ·  Confidencial", s_foot))
    doc.build(elems)
    buffer.seek(0)
    return buffer.read()

with st.sidebar:
    if os.path.exists(LOGO_H):
        st.image(LOGO_H, use_container_width=True)
    if os.path.exists(FIB):
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("<div class='rw-fib-wrap'>", unsafe_allow_html=True)
            st.image(FIB, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<p style='color:{CREAM};font-size:0.85em;text-align:center;'>Precificação de Projetos</p>", unsafe_allow_html=True)
    st.markdown("---")
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes_ref = st.selectbox("Mês", meses, index=datetime.now().month-1, label_visibility="collapsed")
    ano_ref = st.number_input("Ano", 2020, 2035, datetime.now().year, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<p style='color:{CREAM};font-weight:600;font-size:0.85em;'>MARGEM DE LUCRO</p>", unsafe_allow_html=True)
    margem_pct = st.slider("Margem (%)", 0, 100, 30, 5, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<p style='color:{CREAM};font-weight:600;font-size:0.85em;'>IMPOSTOS SOBRE RECEITA</p>", unsafe_allow_html=True)
    aliquota_imposto = st.slider("Impostos (%)", 0, 40, 12, 1, label_visibility="collapsed")
    st.markdown(f"<p style='color:{CREAM};font-size:0.75em;margin-top:2px;'>Ex: Simples Nacional, ISS, PIS/COFINS...</p>", unsafe_allow_html=True)

st.markdown(
    f"<h1 style='color:{WHITE};font-size:2em;margin-bottom:4px;'>Precificação de Projetos</h1>"
    f"<p style='color:{CREAM};margin-top:0;'>RedWood Estratégia & Impacto — {mes_ref} {ano_ref}</p>",
    unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏢  Empresa & Consultores",
    "📋  Etapas da Consultoria",
    "📊  Custos & Ganhos Internos",
    "📄  Proposta & PDF Cliente",
])

with tab1:
    col_e, col_c = st.columns([1,1])

    with col_e:
        st.markdown("<div class='rw-section'>Dados da Empresa</div>", unsafe_allow_html=True)
        empresa_nome  = st.text_input("Nome da empresa",  value="RedWood Estratégia & Impacto", key="empresa_nome")
        empresa_email = st.text_input("E-mail", value="contato@redwoodimpacto.com.br", key="empresa_email")
        empresa_cnpj  = st.text_input("CNPJ", value="", key="empresa_cnpj", placeholder="00.000.000/0001-00")

        st.markdown("<div class='rw-section'>Custos Fixos Mensais</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='rw-info'><p>Rateados proporcionalmente ao projeto.</p></div>", unsafe_allow_html=True)
        custos_upd = []
        for i, c in enumerate(st.session_state["custos_fixos"]):
            ca, cb, cc = st.columns([3,2,0.5])
            with ca: nome_c = st.text_input("", value=c["item"], key=f"cf_nome_{i}", label_visibility="collapsed")
            with cb: val_c  = st.number_input("", value=float(c["valor"]), min_value=0.0, step=10.0, key=f"cf_val_{i}", label_visibility="collapsed", format="%.2f")
            with cc:  rem   = st.button("✕", key=f"cf_del_{i}")
            if not rem: custos_upd.append({"item": nome_c, "valor": val_c})
        st.session_state["custos_fixos"] = custos_upd

        na, nb, nc = st.columns([3,2,0.5])
        with na: n_item = st.text_input("", key="cf_n_item", placeholder="Novo item", label_visibility="collapsed")
        with nb: n_val  = st.number_input("", min_value=0.0, step=10.0, key="cf_n_val", label_visibility="collapsed", format="%.2f")
        with nc:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("＋", key="cf_add"):
                if n_item.strip():
                    st.session_state["custos_fixos"].append({"item": n_item, "valor": n_val})
                    st.rerun()

        total_fixos = sum(c["valor"] for c in st.session_state["custos_fixos"])
        st.markdown(
            f"<div class='rw-card' style='margin-top:12px;'>"
            f"<p style='color:{CREAM};margin:0 0 4px 0;font-size:0.8em;'>TOTAL CUSTOS FIXOS / MÊS</p>"
            f"<p style='color:{WHITE};font-size:1.8em;font-weight:700;margin:0;'>{fmt(total_fixos)}</p>"
            f"</div>", unsafe_allow_html=True)

    with col_c:
        st.markdown("<div class='rw-section'>Consultores</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='rw-info'><p>Nome e valor da hora técnica de cada consultor.</p></div>", unsafe_allow_html=True)
        cons_upd = []
        for i, c in enumerate(st.session_state["consultores"]):
            ca, cb, cc = st.columns([2.5,2,0.5])
            with ca: nome_c = st.text_input("Nome", value=c["nome"], key=f"con_nome_{i}", label_visibility="collapsed")
            with cb: vh     = st.number_input("R$/h", value=float(c["valor_hora"]), min_value=0.0, step=10.0, key=f"con_vh_{i}", label_visibility="collapsed", format="%.2f")
            with cc: rem    = st.button("✕", key=f"con_del_{i}")
            if not rem: cons_upd.append({"nome": nome_c, "valor_hora": vh})
        st.session_state["consultores"] = cons_upd

        ca2, cb2, cc2 = st.columns([2.5,2,0.5])
        with ca2: n_nome = st.text_input("", key="con_n_nome", placeholder="Nome do consultor", label_visibility="collapsed")
        with cb2: n_vh   = st.number_input("", min_value=0.0, step=10.0, value=300.0, key="con_n_vh", label_visibility="collapsed", format="%.2f")
        with cc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("＋", key="con_add"):
                if n_nome.strip():
                    st.session_state["consultores"].append({"nome": n_nome, "valor_hora": n_vh})
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        for c in st.session_state["consultores"]:
            st.markdown(
                f"<div class='rw-card'>"
                f"<p style='color:{WHITE};font-weight:700;margin:0;'>{c['nome']}</p>"
                f"<p style='color:{CREAM};font-size:0.9em;margin:2px 0 0 0;'>"
                f"Taxa: <b style='color:{WHITE};'>{fmt(c['valor_hora'])}/hora</b></p>"
                f"</div>", unsafe_allow_html=True)

with tab2:
    col_info, col_etapas = st.columns([1, 1.5])

    with col_info:
        st.markdown("<div class='rw-section'>Dados do Projeto</div>", unsafe_allow_html=True)
        cliente_nome      = st.text_input("Nome do cliente / empresa", key="cli_nome")
        cliente_email     = st.text_input("E-mail do cliente", key="cli_email")
        projeto_nome      = st.text_input("Nome do projeto", key="proj_nome")
        projeto_descricao = st.text_area("Descrição do projeto", key="proj_desc", height=120,
                                          placeholder="Descreva o escopo da consultoria...")
        st.markdown("<div class='rw-section'>Horas Disponíveis</div>", unsafe_allow_html=True)
        horas_mes_total = st.number_input("Horas totais disponíveis / mês", min_value=1, max_value=1000, value=160)
        st.session_state["horas_mes_total"] = horas_mes_total

    with col_etapas:
        st.markdown("<div class='rw-section'>Nova Etapa</div>", unsafe_allow_html=True)
        ne_nome = st.text_input("Nome da etapa", key="ne_nome", placeholder="Ex: Diagnóstico Inicial")
        ne_desc = st.text_input("Descrição (opcional)", key="ne_desc", placeholder="Ex: Levantamento documental")
        st.caption("Horas por consultor:")
        ne_horas = {}
        for c in st.session_state["consultores"]:
            ne_horas[c["nome"]] = st.number_input(
                f"{c['nome']} (h)", min_value=0.0, step=1.0,
                key=f"ne_h_{c['nome']}", format="%.1f")
        if st.button("Adicionar Etapa", key="add_etapa"):
            if ne_nome.strip():
                st.session_state["etapas"].append(
                    {"nome": ne_nome, "descricao": ne_desc, "horas": ne_horas.copy()})
                st.rerun()

        if st.session_state["etapas"]:
            st.markdown("<div class='rw-section'>Etapas Adicionadas</div>", unsafe_allow_html=True)
            etapas_manter = []
            for i, e in enumerate(st.session_state["etapas"]):
                horas_e = sum(e["horas"].get(c["nome"],0) for c in st.session_state["consultores"])
                valor_e = sum(e["horas"].get(c["nome"],0)*c["valor_hora"] for c in st.session_state["consultores"])
                ca, cb = st.columns([5,1])
                with ca:
                    badges = "".join([
                        f"<span class='badge'>{c['nome']}: {e['horas'].get(c['nome'],0):.0f}h</span>"
                        for c in st.session_state["consultores"] if e["horas"].get(c["nome"],0)>0])
                    st.markdown(
                        f"<div class='rw-card'>"
                        f"<p style='color:{WHITE};font-weight:700;margin:0;'>{i+1}. {e['nome']}</p>"
                        f"<p style='color:{CREAM};font-size:0.85em;margin:2px 0 6px 0;'>{e.get('descricao','')}</p>"
                        f"{badges}"
                        f"<p style='color:{CREAM};margin:8px 0 0 0;font-size:0.85em;'>"
                        f"Total: <b style='color:{WHITE};'>{horas_e:.0f}h</b>  · "
                        f"Valor: <b style='color:{WHITE};'>{fmt(valor_e)}</b></p>"
                        f"</div>", unsafe_allow_html=True)
                with cb:
                    st.write("")
                    st.write("")
                    if not st.button("Remover", key=f"del_etapa_{i}"):
                        etapas_manter.append(e)
            st.session_state["etapas"] = etapas_manter

    st.markdown("---")
    st.markdown("<div class='rw-section'>Custos Adicionais do Projeto</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='rw-info'><p>Custos variáveis específicos deste projeto — somados ao valor final.</p></div>",
        unsafe_allow_html=True)

    cv1, cv2, cv3 = st.columns(3)
    with cv1:
        st.markdown(f"<p style='color:{CREAM};font-weight:700;margin:0 0 8px 0;'>Deslocamento & Viagem</p>", unsafe_allow_html=True)
        total_viagem = custo_lista_ui("custos_viagem", "Ex: Táxi, pedágio...")
    with cv2:
        st.markdown(f"<p style='color:{CREAM};font-weight:700;margin:0 0 8px 0;'>Terceiros</p>", unsafe_allow_html=True)
        total_terceiros = custo_lista_ui("custos_terceiros", "Ex: Designer, fotógrafo...")
    with cv3:
        st.markdown(f"<p style='color:{CREAM};font-weight:700;margin:0 0 8px 0;'>Marketing</p>", unsafe_allow_html=True)
        total_marketing = custo_lista_ui("custos_marketing", "Ex: Anúncios, materiais...")

    st.session_state["total_viagem"]    = total_viagem
    st.session_state["total_terceiros"] = total_terceiros
    st.session_state["total_marketing"] = total_marketing

with tab3:
    consultores   = st.session_state["consultores"]
    etapas        = st.session_state["etapas"]
    total_fixos   = sum(c["valor"] for c in st.session_state["custos_fixos"])
    horas_mes_tot = st.session_state.get("horas_mes_total", 160)

    dados_cons = []
    for c in consultores:
        horas = sum(e["horas"].get(c["nome"],0) for e in etapas)
        ganho = horas * c["valor_hora"]
        dados_cons.append({"nome": c["nome"], "valor_hora": c["valor_hora"], "horas": horas, "ganho": ganho})

    total_horas_proj = sum(d["horas"] for d in dados_cons)
    custo_labor      = sum(d["ganho"] for d in dados_cons)
    proporcao        = min(total_horas_proj / max(horas_mes_tot, 1), 1.0)
    fixos_alocados   = total_fixos * proporcao
    custo_viagem     = st.session_state.get("total_viagem", 0.0)
    custo_terceiros  = st.session_state.get("total_terceiros", 0.0)
    custo_marketing  = st.session_state.get("total_marketing", 0.0)
    custo_extras     = custo_viagem + custo_terceiros + custo_marketing
    custo_base       = custo_labor + fixos_alocados + custo_extras
    valor_margem     = custo_base * (margem_pct / 100)
    valor_total_proj = custo_base + valor_margem
    st.session_state["valor_total_proj"] = valor_total_proj

    st.markdown("<div class='rw-section'>Resumo do Projeto</div>", unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Total de Horas",       fmt_h(total_horas_proj))
    with m2: st.metric("Labor",                fmt(custo_labor))
    with m3: st.metric("Fixos Rateados",       fmt(fixos_alocados))
    with m4: st.metric("Extras do Projeto",    fmt(custo_extras))
    with m5: st.metric("Margem de Lucro",      fmt(valor_margem), delta=f"{margem_pct}%")

    st.markdown(
        f"<div class='rw-total'>"
        f"<p>VALOR TOTAL PARA O CLIENTE</p>"
        f"<h2>{fmt(valor_total_proj)}</h2>"
        f"<p>Labor {fmt(custo_labor)}  ·  Fixos {fmt(fixos_alocados)}  ·  "
        f"Extras {fmt(custo_extras)}  ·  Margem {fmt(valor_margem)}</p>"
        f"</div>", unsafe_allow_html=True)

    st.markdown("<div class='rw-section'>Ganhos por Consultor</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rw-info'><p>Valores internos — não aparecem no PDF do cliente.</p></div>", unsafe_allow_html=True)

    if dados_cons and custo_labor > 0:
        cols = st.columns(min(len(dados_cons), 3))
        for i, d in enumerate(dados_cons):
            pct = (d["ganho"] / custo_labor * 100) if custo_labor > 0 else 0
            with cols[i % 3]:
                st.markdown(
                    f"<div class='rw-card-green'>"
                    f"<p style='color:{CREAM};margin:0 0 4px 0;font-size:0.8em;text-transform:uppercase;'>{d['nome']}</p>"
                    f"<p style='color:#5DBA8A;font-size:1.9em;font-weight:700;margin:0;'>{fmt(d['ganho'])}</p>"
                    f"<p style='color:{CREAM};font-size:0.85em;margin:4px 0 0 0;'>"
                    f"{d['horas']:.0f}h × {fmt(d['valor_hora'])}/h  ·  {pct:.1f}% do labor</p>"
                    f"</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='rw-info'><p>Adicione etapas com horas para ver os ganhos.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='rw-section'>Resultado da Empresa</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    imposto   = valor_total_proj * (aliquota_imposto / 100)
    lucro_liq = valor_total_proj - custo_labor - fixos_alocados - custo_extras - imposto
    receita_h = valor_total_proj / total_horas_proj if total_horas_proj > 0 else 0
    with ca:
        st.markdown(
            f"<div class='rw-gain'><p>LUCRO LÍQUIDO DA EMPRESA</p>"
            f"<h2>{fmt(lucro_liq)}</h2>"
            f"<p>Receita {fmt(valor_total_proj)}  ·  Impostos ({aliquota_imposto}%) {fmt(imposto)}</p>"
            f"</div>", unsafe_allow_html=True)
    with cb:
        st.markdown(
            f"<div class='rw-card' style='border-color:{RUST}88;'>"
            f"<p style='color:{CREAM};margin:0 0 8px 0;font-size:0.85em;'>DETALHAMENTO</p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Receita total: <b>{fmt(valor_total_proj)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Labor: <b>{fmt(custo_labor)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Custos fixos alocados: <b>{fmt(fixos_alocados)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Deslocamento & Viagem: <b>{fmt(custo_viagem)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Terceiros: <b>{fmt(custo_terceiros)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Marketing: <b>{fmt(custo_marketing)}</b></p>"
            f"<p style='color:{RUST};margin:2px 0;'>Impostos ({aliquota_imposto}%): <b>{fmt(imposto)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Receita por hora: <b>{fmt(receita_h)}/h</b></p>"
            f"<p style='color:#5DBA8A;margin:8px 0 0 0;font-weight:700;font-size:1.1em;'>Lucro líquido: {fmt(lucro_liq)}</p>"
            f"</div>", unsafe_allow_html=True)

    # Percentuais visuais na tela
    st.markdown("<div class='rw-section'>Composição Percentual da Receita</div>", unsafe_allow_html=True)
    ORANGE = "#C97A20"
    PURPLE = "#6B4FA0"
    TEAL   = "#1F7A7A"
    if valor_total_proj > 0:
        itens_pct = [
            ("Labor (Consultores)",    custo_labor,     RUST),
            ("Custos Fixos Rateados",  fixos_alocados,  LNAVY),
            ("Deslocamento & Viagem",  custo_viagem,    ORANGE),
            ("Terceiros",              custo_terceiros,  PURPLE),
            ("Marketing",              custo_marketing,  TEAL),
            (f"Impostos ({aliquota_imposto}%)", imposto, "#8B0000"),
            ("Lucro Líquido",          lucro_liq,       GREEN),
        ]
        for label, valor, cor in itens_pct:
            if valor <= 0 and label not in ("Labor (Consultores)", "Lucro Líquido"):
                continue
            pct = valor / valor_total_proj * 100
            st.markdown(
                f"<div style='margin:6px 0;'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:3px;'>"
                f"<span style='color:{CREAM};font-size:0.88em;'>{label}</span>"
                f"<span style='color:{WHITE};font-weight:700;font-size:0.88em;'>{fmt(valor)}  —  {pct:.1f}%</span>"
                f"</div>"
                f"<div style='background:{LNAVY};border-radius:4px;height:10px;'>"
                f"<div style='background:{cor};width:{pct:.1f}%;height:10px;border-radius:4px;'></div>"
                f"</div></div>",
                unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='rw-info'><p>Configure etapas e consultores para ver os percentuais.</p></div>", unsafe_allow_html=True)

    # Botão PDF Interno
    st.markdown("---")
    st.markdown("<div class='rw-section'>Relatório Interno PDF</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rw-info'><p>Relatório completo com percentuais de custos — uso exclusivo interno da RedWood.</p></div>", unsafe_allow_html=True)

    if st.button("📊  Gerar Relatório Interno PDF"):
        if valor_total_proj == 0:
            st.warning("Configure as etapas e consultores antes de gerar o relatório.")
        else:
            pdf_int = gerar_pdf_interno(
                empresa_nome=st.session_state.get("empresa_nome","RedWood Estratégia & Impacto"),
                empresa_email=st.session_state.get("empresa_email",""),
                cliente_nome=st.session_state.get("cli_nome",""),
                projeto_nome=st.session_state.get("proj_nome",""),
                etapas=etapas,
                consultores=consultores,
                custos_fixos=st.session_state.get("custos_fixos",[]),
                custo_labor=custo_labor,
                fixos_alocados=fixos_alocados,
                valor_margem=valor_margem,
                valor_total_proj=valor_total_proj,
                lucro_liq=lucro_liq,
                margem_pct=margem_pct,
                total_horas_proj=total_horas_proj,
                dados_cons=dados_cons,
                mes_ref=mes_ref,
                ano_ref=ano_ref,
                logo_path=LOGO_V,
                custos_viagem=st.session_state.get("custos_viagem",[]),
                custos_terceiros=st.session_state.get("custos_terceiros",[]),
                custos_marketing=st.session_state.get("custos_marketing",[]),
                custo_extras=custo_extras,
                empresa_cnpj=st.session_state.get("empresa_cnpj",""),
                imposto=imposto,
                aliquota_imposto=aliquota_imposto,
            )
            nome_int = f"Interno_{(st.session_state.get('proj_nome') or 'Projeto').replace(' ','_')}_{mes_ref}_{ano_ref}.pdf"
            st.download_button(
                label="⬇️  Baixar Relatório Interno",
                data=pdf_int,
                file_name=nome_int,
                mime="application/pdf",
            )
            st.success("Relatório interno gerado com percentuais de todos os custos!")

with tab4:
    consultores  = st.session_state["consultores"]
    etapas       = st.session_state["etapas"]
    valor_total  = st.session_state.get("valor_total_proj", 0.0)

    st.markdown("<div class='rw-section'>Prévia da Proposta para o Cliente</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rw-info'><p>O PDF mostra apenas o <b>valor total</b> — sem custos internos, margens ou ganhos.</p></div>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown(
            f"<div class='rw-card'>"
            f"<p style='color:{CREAM};font-size:0.8em;margin:0 0 4px 0;'>CLIENTE</p>"
            f"<p style='color:{WHITE};font-size:1.1em;font-weight:700;margin:0;'>{st.session_state.get('cli_nome','—') or '—'}</p>"
            f"<p style='color:{CREAM};font-size:0.85em;margin:2px 0 0 0;'>{st.session_state.get('cli_email','') or ''}</p>"
            f"</div>", unsafe_allow_html=True)
    with cb:
        st.markdown(
            f"<div class='rw-card'>"
            f"<p style='color:{CREAM};font-size:0.8em;margin:0 0 4px 0;'>PROJETO</p>"
            f"<p style='color:{WHITE};font-size:1.1em;font-weight:700;margin:0;'>{st.session_state.get('proj_nome','—') or '—'}</p>"
            f"<p style='color:{CREAM};font-size:0.85em;margin:2px 0 0 0;'>{mes_ref} {ano_ref}</p>"
            f"</div>", unsafe_allow_html=True)

    if etapas:
        st.markdown(f"<p style='color:{CREAM};font-weight:600;margin:16px 0 8px 0;'>ETAPAS</p>", unsafe_allow_html=True)
        for i, e in enumerate(etapas):
            horas_e = sum(e["horas"].get(c["nome"],0) for c in consultores)
            valor_e = sum(e["horas"].get(c["nome"],0)*c["valor_hora"] for c in consultores)
            st.markdown(
                f"<div class='rw-card' style='padding:14px 18px;'>"
                f"<p style='color:{WHITE};font-weight:700;margin:0;'>{i+1}. {e['nome']}</p>"
                f"<p style='color:{CREAM};font-size:0.85em;margin:2px 0 0 0;'>"
                f"{e.get('descricao','')}{'  ·  ' if e.get('descricao') else ''}{horas_e:.0f}h  ·  {fmt(valor_e)}</p>"
                f"</div>", unsafe_allow_html=True)

    total_h = sum(sum(e["horas"].get(c["nome"],0) for c in consultores) for e in etapas)
    st.markdown(
        f"<div class='rw-total'><p>VALOR TOTAL DA PROPOSTA</p>"
        f"<h2>{fmt(valor_total)}</h2>"
        f"<p>{total_h:.0f} horas  ·  {len(etapas)} etapa{'s' if len(etapas)!=1 else ''}</p>"
        f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='rw-section'>Gerar PDF</div>", unsafe_allow_html=True)
    observacoes_pdf = st.text_area("Observações para o cliente (opcional)",
                                    placeholder="Ex: Condições de pagamento, prazo de entrega...",
                                    height=80, key="obs_pdf")

    if st.button("📄  Gerar PDF da Proposta"):
        if valor_total == 0:
            st.warning("Configure as etapas e consultores antes de gerar o PDF.")
        else:
            pdf_bytes = gerar_pdf_cliente(
                empresa_nome=st.session_state.get("empresa_nome","RedWood Estratégia & Impacto"),
                empresa_email=st.session_state.get("empresa_email",""),
                cliente_nome=st.session_state.get("cli_nome",""),
                cliente_email=st.session_state.get("cli_email",""),
                projeto_nome=st.session_state.get("proj_nome",""),
                projeto_descricao=st.session_state.get("proj_desc",""),
                etapas=etapas,
                consultores=consultores,
                valor_total=valor_total,
                mes_ref=mes_ref,
                ano_ref=ano_ref,
                logo_path=LOGO_V,
                observacoes=observacoes_pdf,
                empresa_cnpj=st.session_state.get("empresa_cnpj",""),
            )
            nome_arq = f"Proposta_{(st.session_state.get('cli_nome') or 'Cliente').replace(' ','_')}_{mes_ref}_{ano_ref}.pdf"
            st.download_button(
                label="⬇️  Baixar PDF da Proposta",
                data=pdf_bytes,
                file_name=nome_arq,
                mime="application/pdf",
            )
            st.success("PDF gerado! Apenas o valor total é visível para o cliente.")
