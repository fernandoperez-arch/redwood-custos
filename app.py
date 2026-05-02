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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RedWood | Gestão de Custos",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand ──────────────────────────────────────────────────────────────────────
NAVY  = "#10012D"
RUST  = "#742C25"
WHITE = "#FFFFFF"
CREAM = "#DED6D0"
LNAVY = "#1A2850"
CARD  = "#162040"
RUST2 = "#8B3A2A"

BASE   = os.path.dirname(os.path.abspath(__file__))
LOGO_H = os.path.join(BASE, "assets", "logo_redwood_white.png")
LOGO_V = os.path.join(BASE, "assets", "logo_redwood_vertical.png")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap');
*, body {{ font-family: 'Figtree', sans-serif !important; }}

.stApp, .main, [data-testid="stAppViewContainer"] {{ background-color: {NAVY} !important; }}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {LNAVY} 0%, {NAVY} 100%) !important;
    border-right: 2px solid {RUST}55 !important;
}}
[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}

.stTabs [data-baseweb="tab-list"] {{
    background-color: {LNAVY}; border-radius: 12px; padding: 6px; gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {CREAM} !important; background-color: transparent;
    border-radius: 8px; font-weight: 500; padding: 8px 20px;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {RUST}, {RUST2}) !important;
    color: {WHITE} !important; font-weight: 600;
}}
.stTabs [data-baseweb="tab-panel"] {{ background-color: transparent; padding-top: 20px; }}

.stNumberInput input, .stTextInput input {{
    background-color: {LNAVY} !important; color: {WHITE} !important;
    border: 1px solid {RUST}66 !important; border-radius: 8px !important;
}}
.stNumberInput label, .stTextInput label, .stSelectbox label,
.stSlider label, .stRadio label {{
    color: {CREAM} !important; font-weight: 500 !important;
}}
div[data-testid="stSelectbox"] > div > div {{
    background-color: {LNAVY} !important; color: {WHITE} !important;
    border: 1px solid {RUST}66 !important; border-radius: 8px !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {RUST}, {RUST2}) !important;
    color: {WHITE} !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 1rem !important;
    padding: 14px 28px !important; width: 100% !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; }}

[data-testid="metric-container"] {{
    background: linear-gradient(135deg, {CARD}, {LNAVY}) !important;
    border: 1px solid {RUST}44 !important; border-radius: 12px !important;
    padding: 18px !important;
}}
[data-testid="metric-container"] label {{
    color: {CREAM} !important; font-size: 0.82em !important;
    text-transform: uppercase; letter-spacing: 0.5px;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {WHITE} !important; font-size: 1.7em !important; font-weight: 700 !important;
}}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color: {CREAM} !important; }}

.rw-card {{
    background: linear-gradient(135deg, {CARD}, {LNAVY});
    border: 1px solid {RUST}44; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 14px;
}}
.rw-section {{
    background: linear-gradient(90deg, {RUST}CC, {RUST}66);
    color: {WHITE}; padding: 10px 20px; border-radius: 8px;
    font-size: 1em; font-weight: 700; letter-spacing: 0.5px;
    text-transform: uppercase; margin: 20px 0 10px 0;
}}
.rw-total {{
    background: linear-gradient(135deg, {RUST}, {RUST2});
    border-radius: 14px; padding: 28px; text-align: center;
    margin: 20px 0; box-shadow: 0 8px 32px {RUST}44;
}}
.rw-total h2 {{ color: {WHITE}; margin: 0; font-size: 2.8em; font-weight: 700; }}
.rw-total p  {{ color: {CREAM}; margin: 6px 0 0 0; font-size: 1em; }}
.rw-info {{
    background: {LNAVY}; border-left: 3px solid {RUST};
    padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0;
}}
.rw-info p {{ color: {CREAM}; margin: 0; font-size: 0.9em; }}

h1, h2, h3 {{ color: {WHITE} !important; }}
p, .stMarkdown p {{ color: {WHITE}; }}
hr {{ border-color: {RUST}44 !important; margin: 20px 0 !important; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calc_inss_empregado(salario: float) -> float:
    faixas = [(1412.00, 0.075), (2666.68, 0.09), (4000.03, 0.12), (7786.02, 0.14)]
    inss, anterior = 0.0, 0.0
    for teto, aliq in faixas:
        if salario <= anterior:
            break
        inss += (min(salario, teto) - anterior) * aliq
        anterior = teto
    return min(inss, 908.86)


def calc_irrf(salario: float, inss: float) -> float:
    base = salario - inss
    faixas = [
        (2259.20,       0.000,   0.00),
        (2826.65,       0.075, 169.44),
        (3751.05,       0.150, 381.44),
        (4664.68,       0.225, 662.77),
        (float("inf"), 0.275, 896.00),
    ]
    for teto, aliq, ded in faixas:
        if base <= teto:
            return max(0.0, base * aliq - ded)
    return 0.0


def encargos_empresa(salario_bruto: float) -> dict:
    return {
        "INSS Patronal (20%)":           salario_bruto * 0.20,
        "FGTS (8%)":                     salario_bruto * 0.08,
        "RAT/FAP (~2%)":                 salario_bruto * 0.02,
        "Terceiros/Sesc/Senai (~5,8%)":  salario_bruto * 0.058,
        "Provisão 13º (8,33%)":          salario_bruto * 0.0833,
        "Provisão Férias (11,11%)":      salario_bruto * 0.1111,
    }


# ── PDF Generator ──────────────────────────────────────────────────────────────
def gerar_pdf(
    nome_consultor, mes_ref, ano_ref, tipo_rem, salario_bruto,
    custo_rem, custos_fixos, total_fixos, custo_base,
    margem_pct, valor_margem, valor_total, custo_hora, horas_mes,
    nome_empresa, observacoes, logo_path,
) -> bytes:

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
    )

    C_NAVY  = colors.HexColor("#10012D")
    C_RUST  = colors.HexColor("#742C25")
    C_WHITE = colors.white
    C_CREAM = colors.HexColor("#DED6D0")
    C_LGRAY = colors.HexColor("#F4F2F0")
    C_DGRAY = colors.HexColor("#333333")

    styles = getSampleStyleSheet()

    def sty(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    s_title    = sty("T",  fontSize=20, textColor=C_WHITE, alignment=TA_LEFT, spaceAfter=3, fontName="Helvetica-Bold")
    s_subtitle = sty("S",  fontSize=10, textColor=C_CREAM, alignment=TA_LEFT, spaceAfter=2)
    s_section  = sty("Se", fontSize=11, textColor=C_WHITE, alignment=TA_LEFT, fontName="Helvetica-Bold")
    s_total_l  = sty("TL", fontSize=10, textColor=C_CREAM, alignment=TA_CENTER)
    s_total_v  = sty("TV", fontSize=18, textColor=C_WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")
    s_footer   = sty("F",  fontSize=8,  textColor=C_CREAM, alignment=TA_CENTER)
    s_obs      = sty("O",  fontSize=9,  textColor=C_DGRAY, alignment=TA_LEFT, leading=14)

    W = A4[0] - 4*cm

    elems = []

    # Header
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=4.5*cm, height=3.5*cm, kind="proportional")
    else:
        logo_img = Paragraph("<b style='color:white'>RedWood</b>", sty("LH", textColor=C_WHITE, fontSize=16))

    title_content = [
        Paragraph("Relatório de Custos", s_title),
        Paragraph("RedWood Estratégia & Impacto", s_subtitle),
        Paragraph(f"{mes_ref} / {ano_ref}  ·  {nome_consultor}", s_subtitle),
    ]
    if nome_empresa and nome_empresa != "Uso Interno":
        title_content.append(Paragraph(f"Cliente: {nome_empresa}", s_subtitle))

    inner = Table([[logo_img, title_content]], colWidths=[5*cm, W - 5*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_NAVY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (0,-1), 10),
        ("LEFTPADDING", (1,0), (1,-1), 20),
    ]))

    outer = Table([[inner]], colWidths=[W])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_NAVY),
        ("BOX", (0,0), (-1,-1), 2, C_RUST),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [10, 10, 10, 10]),
    ]))
    elems.append(outer)
    elems.append(Spacer(1, 0.4*cm))

    def sec_hdr(text):
        t = Table([[Paragraph(text, s_section)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), C_RUST),
            ("LEFTPADDING", (0,0), (-1,-1), 14),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        return t

    def data_tbl(headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [W / len(headers)] * len(headers)
        data = [headers] + rows
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), C_NAVY),
            ("TEXTCOLOR",    (0,0), (-1,0), C_WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,0), 10),
            ("ALIGN",        (0,0), (-1,0), "CENTER"),
            ("TOPPADDING",   (0,0), (-1,0), 9),
            ("BOTTOMPADDING",(0,0), (-1,0), 9),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_LGRAY, C_WHITE]),
            ("FONTSIZE",     (0,1), (-1,-1), 9),
            ("TEXTCOLOR",    (0,1), (-1,-1), C_DGRAY),
            ("ALIGN",        (-1,1), (-1,-1), "RIGHT"),
            ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
            ("LEFTPADDING",  (0,0), (-1,-1), 10),
            ("RIGHTPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING",   (0,1), (-1,-1), 6),
            ("BOTTOMPADDING",(0,1), (-1,-1), 6),
            ("BOX",          (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC")),
        ]))
        return t

    def highlight_last(tbl, n_rows):
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, n_rows), (-1, n_rows), C_NAVY),
            ("TEXTCOLOR",  (0, n_rows), (-1, n_rows), C_WHITE),
            ("FONTNAME",   (0, n_rows), (-1, n_rows), "Helvetica-Bold"),
        ]))
        return tbl

    # 1. Remuneração
    elems.append(sec_hdr("1. REMUNERAÇÃO"))
    elems.append(Spacer(1, 0.2*cm))
    rem_rows = [[tipo_rem, "Salário / Pro-labore Bruto", fmt_brl(salario_bruto)]]
    if "CLT" in tipo_rem:
        for k, v in encargos_empresa(salario_bruto).items():
            rem_rows.append(["Encargo Patronal", k, fmt_brl(v)])
    rem_rows.append(["TOTAL", "Custo Total com RH", fmt_brl(custo_rem)])
    t = data_tbl(["Tipo", "Descrição", "Valor (R$)"], rem_rows, [4*cm, 9*cm, 4*cm])
    highlight_last(t, len(rem_rows))
    elems.append(t)
    elems.append(Spacer(1, 0.4*cm))

    # 2. Custos Fixos
    elems.append(sec_hdr("2. CUSTOS FIXOS MENSAIS"))
    elems.append(Spacer(1, 0.2*cm))
    fix_rows = [[c["categoria"], c["item"], fmt_brl(c["valor"])] for c in custos_fixos]
    fix_rows.append(["TOTAL", "Custos Fixos", fmt_brl(total_fixos)])
    t2 = data_tbl(["Categoria", "Item", "Valor (R$)"], fix_rows, [4.5*cm, 8.5*cm, 4*cm])
    highlight_last(t2, len(fix_rows))
    elems.append(t2)
    elems.append(Spacer(1, 0.4*cm))

    # 3. Consolidado
    elems.append(sec_hdr("3. CONSOLIDADO MENSAL"))
    elems.append(Spacer(1, 0.2*cm))
    cons_rows = [
        ["Remuneração",             fmt_brl(custo_rem)],
        ["Custos Fixos",            fmt_brl(total_fixos)],
        ["Custo Base",              fmt_brl(custo_base)],
        [f"Margem de Lucro ({margem_pct}%)", fmt_brl(valor_margem)],
    ]
    t3 = data_tbl(["Componente", "Valor (R$)"], cons_rows, [12*cm, 5*cm])
    elems.append(t3)
    elems.append(Spacer(1, 0.3*cm))

    # Total box
    tb_data = [[
        Paragraph("VALOR TOTAL MENSAL NECESSÁRIO", s_total_l),
        Paragraph(fmt_brl(valor_total), s_total_v),
    ]]
    tb = Table(tb_data, colWidths=[W/2, W/2])
    tb.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_RUST),
        ("TOPPADDING",   (0,0), (-1,-1), 16),
        ("BOTTOMPADDING",(0,0), (-1,-1), 16),
        ("LEFTPADDING",  (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    elems.append(tb)
    elems.append(Spacer(1, 0.4*cm))

    # 4. Taxa Horária
    elems.append(sec_hdr("4. REFERÊNCIA DE TAXA HORÁRIA"))
    elems.append(Spacer(1, 0.2*cm))
    be = custo_base / horas_mes if horas_mes else 0
    hora_rows = [
        ["Horas disponíveis / mês",                      f"{horas_mes}h"],
        ["Custo / hora (break-even)",                    fmt_brl(be)],
        [f"Taxa horária sugerida (c/ {margem_pct}% margem)", fmt_brl(custo_hora)],
    ]
    t4 = data_tbl(["Indicador", "Valor"], hora_rows, [11*cm, 6*cm])
    elems.append(t4)
    elems.append(Spacer(1, 0.4*cm))

    # 5. Observações
    if observacoes:
        elems.append(sec_hdr("5. OBSERVAÇÕES"))
        elems.append(Spacer(1, 0.2*cm))
        elems.append(Paragraph(observacoes, s_obs))
        elems.append(Spacer(1, 0.3*cm))

    # Footer
    elems.append(HRFlowable(width=W, thickness=1, color=C_RUST))
    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}  ·  "
        f"RedWood Estratégia & Impacto  ·  Uso confidencial interno",
        s_footer,
    ))

    doc.build(elems)
    buffer.seek(0)
    return buffer.read()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(LOGO_H):
        st.image(LOGO_H, use_container_width=True)
    st.markdown("---")
    st.markdown(
        f"<p style='color:{CREAM};font-size:0.85em;text-align:center;'>Gestão de Custos da Consultoria</p>"
        f"<p style='color:{RUST};font-size:0.8em;text-align:center;'>Estratégia & Impacto</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown(f"<p style='color:{CREAM};font-weight:600;font-size:0.9em;'>PERÍODO DE REFERÊNCIA</p>",
                unsafe_allow_html=True)
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes_ref = st.selectbox("Mês", meses, index=datetime.now().month - 1,
                           label_visibility="collapsed")
    ano_ref = st.number_input("Ano", min_value=2020, max_value=2035,
                               value=datetime.now().year, label_visibility="collapsed")
    st.markdown("---")
    nome_consultor = st.text_input("Nome do Consultor", value="Fernando Richard")
    horas_mes      = st.number_input("Horas disponíveis / mês", min_value=1, max_value=300, value=160)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1 style='color:{WHITE};font-size:2.2em;margin-bottom:4px;'>Gestão de Custos</h1>"
    f"<p style='color:{CREAM};font-size:1em;margin-top:0;'>"
    f"RedWood Estratégia & Impacto — {mes_ref} {ano_ref}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "💼  Salário & Encargos",
    "📋  Custos Fixos",
    "📈  Margem de Lucro",
    "📊  Resumo & PDF",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Salário & Encargos
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='rw-section'>Remuneração</div>", unsafe_allow_html=True)

    tipo_rem = st.radio(
        "Tipo de remuneração",
        ["Pro-labore (Sócio / PJ)", "CLT (Empregado)"],
        horizontal=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        salario_bruto = st.number_input(
            "Salário / Pro-labore Bruto (R$)",
            min_value=0.0, max_value=100_000.0,
            value=8_000.0, step=100.0, format="%.2f",
        )

    if "CLT" in tipo_rem:
        inss_emp = calc_inss_empregado(salario_bruto)
        irrf_emp = calc_irrf(salario_bruto, inss_emp)
        liquido  = salario_bruto - inss_emp - irrf_emp

        with col_b:
            st.markdown(
                f"<div class='rw-card'>"
                f"<p style='color:{CREAM};margin:0 0 8px 0;font-size:0.85em;'>CUSTO AO EMPREGADO</p>"
                f"<p style='color:{WHITE};margin:2px 0;'>INSS: <b>{fmt_brl(inss_emp)}</b></p>"
                f"<p style='color:{WHITE};margin:2px 0;'>IRRF: <b>{fmt_brl(irrf_emp)}</b></p>"
                f"<p style='color:{RUST};margin:6px 0 0 0;font-weight:700;font-size:1.1em;'>"
                f"Líquido: {fmt_brl(liquido)}</p></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='rw-section'>Encargos Patronais</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='rw-info'><p>Custo total que a empresa tem além do salário bruto.</p></div>",
            unsafe_allow_html=True,
        )
        enc = encargos_empresa(salario_bruto)
        total_enc = sum(enc.values())
        cols = st.columns(3)
        for i, (nome_enc, val_enc) in enumerate(enc.items()):
            with cols[i % 3]:
                st.metric(nome_enc, fmt_brl(val_enc))

        custo_rh = salario_bruto + total_enc
        st.markdown(
            f"<div class='rw-card' style='border-color:{RUST}88;'>"
            f"<p style='color:{CREAM};margin:0 0 4px 0;font-size:0.85em;'>CUSTO TOTAL COM RH</p>"
            f"<p style='color:{WHITE};font-size:2em;font-weight:700;margin:0;'>{fmt_brl(custo_rh)}</p>"
            f"<p style='color:{CREAM};font-size:0.85em;margin:4px 0 0 0;'>"
            f"Salário bruto + encargos patronais</p></div>",
            unsafe_allow_html=True,
        )
        custo_remuneracao = custo_rh

    else:  # Pro-labore
        with col_b:
            aliq_pl = st.slider("Alíquota INSS Pro-labore (%)", 0.0, 20.0, 11.0, 0.5)

        inss_pl = min(salario_bruto * (aliq_pl / 100), 908.86)
        irrf_pl = calc_irrf(salario_bruto, inss_pl)
        liquido = salario_bruto - inss_pl - irrf_pl

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("INSS Pro-labore", fmt_brl(inss_pl))
        with c2: st.metric("IRRF Estimado",   fmt_brl(irrf_pl))
        with c3: st.metric("Salário Líquido", fmt_brl(liquido))

        st.markdown(
            f"<div class='rw-info'><p>No pro-labore não há FGTS obrigatório. "
            f"Consulte seu contador para a melhor estratégia tributária.</p></div>",
            unsafe_allow_html=True,
        )
        custo_remuneracao = salario_bruto

    st.session_state["custo_remuneracao"] = custo_remuneracao
    st.session_state["salario_bruto"]     = salario_bruto
    st.session_state["tipo_rem"]          = tipo_rem


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Custos Fixos
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='rw-section'>Custos Fixos Mensais</div>", unsafe_allow_html=True)

    if "custos_fixos" not in st.session_state:
        st.session_state["custos_fixos"] = [
            {"item": "Mensalidade Plataforma", "valor": 250.0, "categoria": "Tecnologia"},
            {"item": "Adobe Creative Cloud",   "valor":  50.0, "categoria": "Software"},
            {"item": "Claude (IA)",             "valor": 120.0, "categoria": "IA / Tecnologia"},
            {"item": "Contador",                "valor": 400.0, "categoria": "Administrativo"},
        ]

    st.markdown(
        f"<div class='rw-info'><p>Edite, remova ou adicione itens conforme necessário.</p></div>",
        unsafe_allow_html=True,
    )

    CATS = ["Tecnologia","Software","IA / Tecnologia","Administrativo",
            "Marketing","Escritório","Transporte","Outros"]

    atualizados = []
    for i, c in enumerate(st.session_state["custos_fixos"]):
        c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 0.5])
        with c1:
            nome_i = st.text_input(f"Item {i+1}", value=c["item"],
                                   key=f"item_{i}", label_visibility="collapsed")
        with c2:
            idx_cat = CATS.index(c["categoria"]) if c["categoria"] in CATS else 0
            cat_i = st.selectbox("Cat", CATS, index=idx_cat,
                                 key=f"cat_{i}", label_visibility="collapsed")
        with c3:
            val_i = st.number_input("R$", min_value=0.0, max_value=50_000.0,
                                    value=float(c["valor"]), step=10.0,
                                    key=f"val_{i}", label_visibility="collapsed", format="%.2f")
        with c4:
            remover = st.button("✕", key=f"del_{i}", help="Remover")
        if not remover:
            atualizados.append({"item": nome_i, "valor": val_i, "categoria": cat_i})

    st.session_state["custos_fixos"] = atualizados

    st.markdown("---")
    st.markdown(f"<p style='color:{CREAM};font-weight:600;'>Adicionar Item</p>", unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns([3, 1.5, 1.5, 0.5])
    with n1: novo_item = st.text_input("Nome", key="n_item", placeholder="Ex: Telefone")
    with n2: nova_cat  = st.selectbox("Categoria", CATS, key="n_cat")
    with n3: novo_val  = st.number_input("Valor (R$)", min_value=0.0, value=0.0,
                                          step=10.0, key="n_val", format="%.2f")
    with n4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("＋", key="add"):
            if novo_item.strip():
                st.session_state["custos_fixos"].append(
                    {"item": novo_item, "valor": novo_val, "categoria": nova_cat}
                )
                st.rerun()

    st.markdown("<div class='rw-section'>Resumo por Categoria</div>", unsafe_allow_html=True)
    if st.session_state["custos_fixos"]:
        df = pd.DataFrame(st.session_state["custos_fixos"])
        total_fixos = df["valor"].sum()
        por_cat = df.groupby("categoria")["valor"].sum().reset_index()
        por_cat.columns = ["Categoria", "Total (R$)"]
        por_cat["Total (R$)"] = por_cat["Total (R$)"].apply(fmt_brl)

        c_tab, c_tot = st.columns([2, 1])
        with c_tab:
            st.dataframe(por_cat, use_container_width=True, hide_index=True)
        with c_tot:
            st.markdown(
                f"<div class='rw-card' style='border-color:{RUST}88;margin-top:8px;'>"
                f"<p style='color:{CREAM};margin:0 0 4px 0;font-size:0.85em;'>TOTAL CUSTOS FIXOS</p>"
                f"<p style='color:{WHITE};font-size:2em;font-weight:700;margin:0;'>{fmt_brl(total_fixos)}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.session_state["total_fixos"] = total_fixos
    else:
        st.session_state["total_fixos"] = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Margem de Lucro
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    custo_rem  = st.session_state.get("custo_remuneracao", 0.0)
    total_fix  = st.session_state.get("total_fixos", 0.0)
    custo_base = custo_rem + total_fix

    st.markdown("<div class='rw-section'>Configuração de Margem</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.metric("Custo Total (sem margem)", fmt_brl(custo_base))
    with c2: st.metric("Horas disponíveis / mês",  f"{horas_mes}h")

    st.markdown("---")
    st.markdown(
        f"<div class='rw-info'><p>A margem garante sustentabilidade, cobre imprevistos "
        f"e gera reserva financeira para o crescimento da empresa.</p></div>",
        unsafe_allow_html=True,
    )

    margem_pct   = st.slider("Margem de Lucro (%)", 0, 100, 30, 5)
    valor_margem = custo_base * (margem_pct / 100)
    valor_total  = custo_base + valor_margem
    custo_hora   = valor_total / horas_mes if horas_mes else 0
    be_hora      = custo_base / horas_mes if horas_mes else 0

    st.markdown("<div class='rw-section'>Resultado</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Custo Base",      fmt_brl(custo_base))
    with m2: st.metric(f"Margem ({margem_pct}%)", fmt_brl(valor_margem))
    with m3: st.metric("Total c/ Margem", fmt_brl(valor_total))
    with m4: st.metric("Custo / hora",    fmt_brl(custo_hora))

    st.markdown(
        f"<div class='rw-total'>"
        f"<p>VALOR TOTAL MENSAL NECESSÁRIO</p>"
        f"<h2>{fmt_brl(valor_total)}</h2>"
        f"<p>Taxa horária mínima: {fmt_brl(custo_hora)}/h  ·  Margem: {fmt_brl(valor_margem)}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='rw-section'>Precificação</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown(
            f"<div class='rw-card'>"
            f"<p style='color:{CREAM};margin:0 0 8px 0;font-size:0.85em;'>TAXA HORÁRIA SUGERIDA</p>"
            f"<p style='color:{WHITE};font-size:2em;font-weight:700;margin:0;'>{fmt_brl(custo_hora)}/h</p>"
            f"<p style='color:{CREAM};font-size:0.85em;margin:4px 0 0 0;'>"
            f"Cobre todos os custos + {margem_pct}% de margem</p></div>",
            unsafe_allow_html=True,
        )
    with cb:
        st.markdown(
            f"<div class='rw-card'>"
            f"<p style='color:{CREAM};margin:0 0 8px 0;font-size:0.85em;'>BREAK-EVEN (SEM MARGEM)</p>"
            f"<p style='color:{WHITE};font-size:2em;font-weight:700;margin:0;'>{fmt_brl(be_hora)}/h</p>"
            f"<p style='color:{CREAM};font-size:0.85em;margin:4px 0 0 0;'>"
            f"Ponto de equilíbrio da operação</p></div>",
            unsafe_allow_html=True,
        )

    st.session_state["margem_pct"]   = margem_pct
    st.session_state["valor_margem"] = valor_margem
    st.session_state["valor_total"]  = valor_total
    st.session_state["custo_hora"]   = custo_hora


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Resumo & PDF
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    custo_rem    = st.session_state.get("custo_remuneracao", 0.0)
    total_fix    = st.session_state.get("total_fixos",      0.0)
    margem_pct   = st.session_state.get("margem_pct",      30)
    valor_margem = st.session_state.get("valor_margem",    0.0)
    valor_total  = st.session_state.get("valor_total",     0.0)
    custo_hora   = st.session_state.get("custo_hora",      0.0)
    custo_base   = custo_rem + total_fix

    st.markdown("<div class='rw-section'>Resumo Consolidado</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Remuneração", fmt_brl(custo_rem),
                  delta=st.session_state.get("tipo_rem", "Pro-labore"))
    with m2:
        st.metric("Custos Fixos", fmt_brl(total_fix),
                  delta=f"{len(st.session_state.get('custos_fixos', []))} itens")
    with m3:
        st.metric("Margem de Lucro", fmt_brl(valor_margem), delta=f"{margem_pct}%")

    st.markdown(
        f"<div class='rw-total'>"
        f"<p>VALOR TOTAL MENSAL NECESSÁRIO</p>"
        f"<h2>{fmt_brl(valor_total)}</h2>"
        f"<p>Custo/hora: {fmt_brl(custo_hora)}/h  ·  {horas_mes}h disponíveis/mês</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='rw-section'>Detalhamento Completo</div>", unsafe_allow_html=True)
    dados = [{"Categoria": "REMUNERAÇÃO",
              "Item": st.session_state.get("tipo_rem", "Pro-labore"),
              "Valor (R$)": custo_rem}]
    for c in st.session_state.get("custos_fixos", []):
        dados.append({"Categoria": c["categoria"], "Item": c["item"], "Valor (R$)": c["valor"]})
    dados.append({"Categoria": "MARGEM DE LUCRO",
                  "Item": f"Margem {margem_pct}%",
                  "Valor (R$)": valor_margem})

    df_res = pd.DataFrame(dados)
    df_res["Valor (R$)"] = df_res["Valor (R$)"].apply(fmt_brl)
    st.dataframe(df_res, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='rw-section'>Gerar Relatório PDF</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nome_empresa = st.text_input("Empresa / Cliente (opcional)", value="Uso Interno")
    with c2:
        observacoes  = st.text_input("Observações (opcional)", value="")

    if st.button("📄  Gerar Relatório PDF"):
        custo_rem_s    = st.session_state.get("custo_remuneracao", 0.0)
        total_fix_s    = st.session_state.get("total_fixos",       0.0)
        custo_base_s   = custo_rem_s + total_fix_s
        valor_total_s  = st.session_state.get("valor_total",       0.0)
        valor_margem_s = st.session_state.get("valor_margem",      0.0)
        custo_hora_s   = st.session_state.get("custo_hora",        0.0)
        margem_pct_s   = st.session_state.get("margem_pct",        30)

        pdf_bytes = gerar_pdf(
            nome_consultor=nome_consultor,
            mes_ref=mes_ref,
            ano_ref=ano_ref,
            tipo_rem=st.session_state.get("tipo_rem", "Pro-labore"),
            salario_bruto=st.session_state.get("salario_bruto", 0.0),
            custo_rem=custo_rem_s,
            custos_fixos=st.session_state.get("custos_fixos", []),
            total_fixos=total_fix_s,
            custo_base=custo_base_s,
            margem_pct=margem_pct_s,
            valor_margem=valor_margem_s,
            valor_total=valor_total_s,
            custo_hora=custo_hora_s,
            horas_mes=horas_mes,
            nome_empresa=nome_empresa,
            observacoes=observacoes,
            logo_path=LOGO_V,
        )

        st.download_button(
            label="⬇️  Baixar PDF",
            data=pdf_bytes,
            file_name=f"RedWood_Custos_{mes_ref}_{ano_ref}.pdf",
            mime="application/pdf",
        )
        st.success("PDF gerado! Clique em 'Baixar PDF' para salvar.")
