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
.stTabs [data-baseweb="tab-list"] {{ background-color:{LNAVY}; border-radius:12px; padding:6px; gap:4px; }}
.stTabs [data-baseweb="tab"] {{ color:{CREAM} !important; background-color:transparent; border-radius:8px; font-weight:500; padding:8px 14px; }}
.stTabs [aria-selected="true"] {{ background:linear-gradient(135deg,{RUST},{RUST2}) !important; color:{WHITE} !important; font-weight:600; }}
.stTabs [data-baseweb="tab-panel"] {{ background-color:transparent; padding-top:20px; }}
.stNumberInput input, .stTextInput input, .stTextArea textarea {{
    background-color:{LNAVY} !important; color:{WHITE} !important;
    border:1px solid {RUST}66 !important; border-radius:8px !important;
}}
.stNumberInput label, .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {{
    color:{CREAM} !important; font-weight:500 !important;
}}
div[data-testid="stSelectbox"] > div > div {{
    background-color:{LNAVY} !important; color:{WHITE} !important;
    border:1px solid {RUST}66 !important; border-radius:8px !important;
}}
.stButton > button {{
    background:linear-gradient(135deg,{RUST},{RUST2}) !important;
    color:{WHITE} !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:0.95rem !important;
    padding:10px 20px !important; width:100% !important;
}}
.stButton > button:hover {{ opacity:0.88 !important; }}
[data-testid="metric-container"] {{
    background:linear-gradient(135deg,{CARD},{LNAVY}) !important;
    border:1px solid {RUST}44 !important; border-radius:12px !important; padding:16px !important;
}}
[data-testid="metric-container"] label {{ color:{CREAM} !important; font-size:0.8em !important; text-transform:uppercase; letter-spacing:0.5px; }}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{ color:{WHITE} !important; font-size:1.6em !important; font-weight:700 !important; }}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color:{CREAM} !important; }}
.rw-card {{ background:linear-gradient(135deg,{CARD},{LNAVY}); border:1px solid {RUST}44; border-radius:14px; padding:18px 20px; margin-bottom:10px; }}
.rw-card-green {{ background:linear-gradient(135deg,#0D2B1A,#1A4030); border:1px solid {GREEN}66; border-radius:14px; padding:18px 20px; margin-bottom:10px; }}
.rw-section {{ background:linear-gradient(90deg,{RUST}CC,{RUST}66); color:{WHITE}; padding:10px 20px; border-radius:8px; font-size:1em; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; margin:20px 0 10px 0; }}
.rw-total {{ background:linear-gradient(135deg,{RUST},{RUST2}); border-radius:14px; padding:24px; text-align:center; margin:18px 0; box-shadow:0 8px 32px {RUST}44; }}
.rw-total h2 {{ color:{WHITE}; margin:0; font-size:2.5em; font-weight:700; }}
.rw-total p  {{ color:{CREAM}; margin:6px 0 0 0; font-size:1em; }}
.rw-gain {{ background:linear-gradient(135deg,{GREEN}33,{GREEN}11); border:1px solid {GREEN}66; border-radius:14px; padding:24px; text-align:center; margin:18px 0; }}
.rw-gain h2 {{ color:#5DBA8A; margin:0; font-size:2.3em; font-weight:700; }}
.rw-gain p  {{ color:{CREAM}; margin:6px 0 0 0; }}
.rw-info {{ background:{LNAVY}; border-left:3px solid {RUST}; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; }}
.rw-info p {{ color:{CREAM}; margin:0; font-size:0.9em; }}
.badge {{ display:inline-block; background:{RUST}33; color:{CREAM}; border:1px solid {RUST}66; border-radius:20px; padding:3px 10px; font-size:0.78em; margin:2px; }}
h1, h2, h3 {{ color:{WHITE} !important; }}
p, .stMarkdown p {{ color:{WHITE}; }}
hr {{ border-color:{RUST}44 !important; margin:16px 0 !important; }}
</style>
""", unsafe_allow_html=True)

def fmt(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def fmt_h(h): return f"{h:.1f}h"

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

init_state()

def gerar_pdf_interno(empresa_nome, empresa_email, cliente_nome, projeto_nome,
                      etapas, consultores, custos_fixos,
                      custo_labor, fixos_alocados, valor_margem,
                      valor_total_proj, lucro_liq, margem_pct,
                      total_horas_proj, dados_cons,
                      mes_ref, ano_ref, logo_path):
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

    info = [
        Paragraph(empresa_nome or "RedWood Estratégia & Impacto", s_title),
        Paragraph(empresa_email or "", s_sub),
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

    # 1. Resumo Financeiro com %
    elems.append(sec_hdr("1. COMPOSIÇÃO DE CUSTOS E RECEITA"))
    elems.append(Spacer(1, 0.2*cm))
    custo_base = custo_labor + fixos_alocados
    rows_comp = [
        ["Labor (Consultores)", fmt(custo_labor),   f"{custo_labor/valor_total_proj*100:.1f}%"   if valor_total_proj else "0%"],
        ["Custos Fixos Rateados", fmt(fixos_alocados), f"{fixos_alocados/valor_total_proj*100:.1f}%" if valor_total_proj else "0%"],
        ["Margem de Lucro",     fmt(valor_margem),  f"{valor_margem/valor_total_proj*100:.1f}%"  if valor_total_proj else "0%"],
        ["RECEITA TOTAL",       fmt(valor_total_proj), "100,0%"],
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

    # 4. Resultado final
    elems.append(sec_hdr("4. RESULTADO FINAL DA EMPRESA"))
    elems.append(Spacer(1, 0.2*cm))
    tb = Table([
        [Paragraph("RECEITA TOTAL", s_tl), Paragraph(fmt(valor_total_proj), s_tv)],
        [Paragraph("LUCRO LÍQUIDO DA EMPRESA", sty("TL2", fontSize=10, textColor=colors.HexColor("#5DBA8A"), alignment=TA_CENTER)),
         Paragraph(f"{fmt(lucro_liq)}  ({margem_pct}%)", s_tv2)],
    ], colWidths=[W/2, W/2])
    tb.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(1,0),C_RUST),
        ("BACKGROUND",(0,1),(1,1),colors.HexColor("#0D2B1A")),
        ("TOPPADDING",(0,0),(-1,-1),16), ("BOTTOMPADDING",(0,0),(-1,-1),16),
        ("LEFTPADDING",(0,0),(-1,-1),20), ("RIGHTPADDING",(0,0),(-1,-1),20),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEBELOW",(0,0),(-1,0),1,C_NAVY),
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
                      valor_total, mes_ref, ano_ref, logo_path, observacoes):
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

    info = [
        Paragraph(empresa_nome or "RedWood Estratégia & Impacto", s_title),
        Paragraph(empresa_email or "", s_sub),
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
        st.markdown("<div style='opacity:0.35;margin-top:4px;'>", unsafe_allow_html=True)
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
        st.markdown("<div class='rw-section'>Etapas da Consultoria</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='rw-info'><p>Adicione as etapas e distribua as horas por consultor.</p></div>", unsafe_allow_html=True)

        with st.expander("➕  Nova Etapa", expanded=len(st.session_state["etapas"])==0):
            ne_nome = st.text_input("Nome da etapa", key="ne_nome", placeholder="Ex: Diagnóstico Inicial")
            ne_desc = st.text_input("Descrição (opcional)", key="ne_desc", placeholder="Ex: Levantamento documental")
            st.markdown(f"<p style='color:{CREAM};font-weight:600;margin:8px 0 4px 0;'>Horas por consultor:</p>", unsafe_allow_html=True)
            ne_horas = {}
            for c in st.session_state["consultores"]:
                ne_horas[c["nome"]] = st.number_input(f"{c['nome']} (h)", min_value=0.0, step=1.0, key=f"ne_h_{c['nome']}", format="%.1f")
            if st.button("Adicionar Etapa", key="add_etapa"):
                if ne_nome.strip():
                    st.session_state["etapas"].append({"nome": ne_nome, "descricao": ne_desc, "horas": ne_horas.copy()})
                    st.rerun()

        if st.session_state["etapas"]:
            st.markdown("<br>", unsafe_allow_html=True)
            etapas_manter = []
            for i, e in enumerate(st.session_state["etapas"]):
                horas_e = sum(e["horas"].get(c["nome"],0) for c in st.session_state["consultores"])
                valor_e = sum(e["horas"].get(c["nome"],0)*c["valor_hora"] for c in st.session_state["consultores"])
                ca, cb = st.columns([5,1])
                with ca:
                    badges = "".join([f"<span class='badge'>{c['nome']}: {e['horas'].get(c['nome'],0):.0f}h</span>"
                                      for c in st.session_state["consultores"] if e["horas"].get(c["nome"],0)>0])
                    st.markdown(
                        f"<div class='rw-card'>"
                        f"<p style='color:{WHITE};font-weight:700;margin:0;'>{i+1}. {e['nome']}</p>"
                        f"<p style='color:{CREAM};font-size:0.85em;margin:2px 0 6px 0;'>{e.get('descricao','')}</p>"
                        f"{badges}"
                        f"<p style='color:{CREAM};margin:8px 0 0 0;font-size:0.85em;'>"
                        f"Total: <b style='color:{WHITE};'>{horas_e:.0f}h</b>  ·  "
                        f"Valor: <b style='color:{WHITE};'>{fmt(valor_e)}</b></p>"
                        f"</div>", unsafe_allow_html=True)
                with cb:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if not st.button("Remover", key=f"del_etapa_{i}"):
                        etapas_manter.append(e)
            st.session_state["etapas"] = etapas_manter
        else:
            st.markdown(f"<div class='rw-info'><p>Nenhuma etapa adicionada ainda.</p></div>", unsafe_allow_html=True)

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
    custo_base       = custo_labor + fixos_alocados
    valor_margem     = custo_base * (margem_pct / 100)
    valor_total_proj = custo_base + valor_margem
    st.session_state["valor_total_proj"] = valor_total_proj

    st.markdown("<div class='rw-section'>Resumo do Projeto</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total de Horas",       fmt_h(total_horas_proj))
    with m2: st.metric("Custo de Labor",        fmt(custo_labor))
    with m3: st.metric("Custos Fixos Rateados", fmt(fixos_alocados))
    with m4: st.metric("Margem de Lucro",       fmt(valor_margem), delta=f"{margem_pct}%")

    st.markdown(
        f"<div class='rw-total'>"
        f"<p>VALOR TOTAL PARA O CLIENTE</p>"
        f"<h2>{fmt(valor_total_proj)}</h2>"
        f"<p>Labor {fmt(custo_labor)}  ·  Fixos {fmt(fixos_alocados)}  ·  Margem {fmt(valor_margem)}</p>"
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
    lucro_liq = valor_total_proj - custo_labor - fixos_alocados
    receita_h = valor_total_proj / total_horas_proj if total_horas_proj > 0 else 0
    with ca:
        st.markdown(
            f"<div class='rw-gain'><p>LUCRO LÍQUIDO DA EMPRESA</p>"
            f"<h2>{fmt(lucro_liq)}</h2>"
            f"<p>Margem {margem_pct}% sobre custo base de {fmt(custo_base)}</p>"
            f"</div>", unsafe_allow_html=True)
    with cb:
        st.markdown(
            f"<div class='rw-card' style='border-color:{RUST}88;'>"
            f"<p style='color:{CREAM};margin:0 0 8px 0;font-size:0.85em;'>DETALHAMENTO</p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Receita total: <b>{fmt(valor_total_proj)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Custo de labor: <b>{fmt(custo_labor)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Custos fixos alocados: <b>{fmt(fixos_alocados)}</b></p>"
            f"<p style='color:{WHITE};margin:2px 0;'>Receita por hora: <b>{fmt(receita_h)}/h</b></p>"
            f"<p style='color:#5DBA8A;margin:8px 0 0 0;font-weight:700;font-size:1.1em;'>Lucro: {fmt(lucro_liq)}</p>"
            f"</div>", unsafe_allow_html=True)

    # Percentuais visuais na tela
    st.markdown("<div class='rw-section'>Composição Percentual da Receita</div>", unsafe_allow_html=True)
    if valor_total_proj > 0:
        itens_pct = [
            ("Labor (Consultores)",    custo_labor,    RUST),
            ("Custos Fixos Rateados",  fixos_alocados, LNAVY),
            ("Margem de Lucro",        valor_margem,   GREEN),
        ]
        for label, valor, cor in itens_pct:
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
            )
            nome_arq = f"Proposta_{(st.session_state.get('cli_nome') or 'Cliente').replace(' ','_')}_{mes_ref}_{ano_ref}.pdf"
            st.download_button(
                label="⬇️  Baixar PDF da Proposta",
                data=pdf_bytes,
                file_name=nome_arq,
                mime="application/pdf",
            )
            st.success("PDF gerado! Apenas o valor total é visível para o cliente.")
