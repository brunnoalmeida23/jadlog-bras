from __future__ import annotations

import io
import os
import re
from datetime import datetime

from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse

from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


router = APIRouter(
    prefix="/pdf",
    tags=["PDF"],
)


LARGURA_RECIBO = 58 * mm


def formatar_documento(valor: str) -> str:
    numeros = re.sub(r"\D", "", str(valor or ""))

    if len(numeros) == 11:
        return (
            f"{numeros[:3]}.{numeros[3:6]}."
            f"{numeros[6:9]}-{numeros[9:]}"
        )

    if len(numeros) == 14:
        return (
            f"{numeros[:2]}.{numeros[2:5]}."
            f"{numeros[5:8]}/{numeros[8:12]}-"
            f"{numeros[12:]}"
        )

    return valor or "Não informado"


def formatar_cep(valor: str) -> str:
    numeros = re.sub(r"\D", "", str(valor or ""))

    if len(numeros) == 8:
        return f"{numeros[:5]}-{numeros[5:]}"

    return valor or "Não informado"


def formatar_moeda(valor: float) -> str:
    texto = f"{float(valor):,.2f}"
    texto = texto.replace(",", "#")
    texto = texto.replace(".", ",")
    texto = texto.replace("#", ".")
    return f"R$ {texto}"


def formatar_peso(valor: float) -> str:
    texto = (
        f"{float(valor):,.3f}"
        .replace(",", "#")
        .replace(".", ",")
        .replace("#", ".")
    )

    return f"{texto} kg"


def formatar_prazo(valor: str) -> str:
    texto = str(valor or "").strip()

    if not texto:
        return "Não informado"

    if texto.isdigit():
        return f"{texto} dias úteis"

    return texto


def escapar_html(valor: str) -> str:
    texto = str(valor or "")

    return (
        texto
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def criar_qrcode(valor: str) -> Drawing:
    qr = QrCodeWidget(valor)

    tamanho = 19 * mm

    desenho = Drawing(
        tamanho,
        tamanho,
    )

    qr.barWidth = tamanho
    qr.barHeight = tamanho

    desenho.add(qr)

    return desenho


def criar_codigo_barras(valor: str) -> Drawing:
    codigo = code128.Code128(
        str(valor or ""),
        barHeight=9 * mm,
        barWidth=0.36 * mm,
    )

    largura = min(codigo.width + 4 * mm, 46 * mm)

    desenho = Drawing(
        largura,
        11 * mm,
    )

    codigo.x = 2 * mm
    codigo.y = 1 * mm

    desenho.add(codigo)

    return desenho


@router.post("/cotacao")
async def gerar_pdf_cotacao(
    numero_cotacao: str = Form(...),
    cliente_nome: str = Form("Cliente não informado"),
    cliente_documento: str = Form(""),
    destino: str = Form(...),
    cep: str = Form(...),
    peso: float = Form(...),
    volumes: int = Form(...),
    valor_nf: float = Form(...),
    prazo: str = Form(...),
    package: float = Form(...),
    com: float = Form(...),
    modalidade: str = Form(""),
    cte: str = Form(""),
    nf: str = Form(""),
    destinatario: str = Form(""),
    observacoes: str = Form(""),
):
    memoria = io.BytesIO()

    documento = SimpleDocTemplate(
        memoria,
        pagesize=(LARGURA_RECIBO, 170 * mm),
        rightMargin=5 * mm,
        leftMargin=5 * mm,
        topMargin=3 * mm,
        bottomMargin=3 * mm,
        title=f"Recibo {numero_cotacao}",
        author="Jadlog Brás",
    )

    estilos = getSampleStyleSheet()

    estilo_centralizado = ParagraphStyle(
        "Centralizado",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=7,
        leading=8,
        textColor=colors.black,
        spaceAfter=0,
        spaceBefore=0,
    )

    estilo_centralizado_negrito = ParagraphStyle(
        "CentralizadoNegrito",
        parent=estilo_centralizado,
        fontName="Helvetica-Bold",
    )

    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilo_centralizado_negrito,
        fontSize=10,
        leading=11,
    )

    estilo_rotulo = ParagraphStyle(
        "Rotulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6,
        leading=7,
        textColor=colors.HexColor("#555555"),
        alignment=TA_LEFT,
        spaceAfter=0,
        spaceBefore=0,
    )

    estilo_valor = ParagraphStyle(
        "Valor",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=8.5,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=0,
        spaceBefore=0,
    )

    estilo_valor_menor = ParagraphStyle(
        "ValorMenor",
        parent=estilo_valor,
        fontSize=7,
        leading=8,
    )

    estilo_total = ParagraphStyle(
        "Total",
        parent=estilo_centralizado_negrito,
        fontSize=15,
        leading=16,
    )

    elementos = []

    # ============================================================
    # LOGO
    # ============================================================

    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "static",
        "img",
        "logo-jadlog.png",
    )

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=32 * mm,
            height=10 * mm,
        )

        logo.hAlign = "CENTER"

        elementos.append(logo)
        elementos.append(Spacer(1, 0.8 * mm))

    elementos.append(
        Paragraph(
            "RECIBO DE FRETE",
            estilo_titulo,
        )
    )

    elementos.append(
        Spacer(1, 1.5 * mm)
    )

    # ============================================================
    # COTAÇÃO / DATA
    # ============================================================

    elementos.append(
        Table(
            [
                [
                    Paragraph("COTAÇÃO", estilo_rotulo),
                    Paragraph("DATA", estilo_rotulo),
                ],
                [
                    Paragraph(
                        escapar_html(numero_cotacao),
                        estilo_valor,
                    ),
                    Paragraph(
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        estilo_valor_menor,
                    ),
                ],
            ],
            colWidths=[
                27 * mm,
                21 * mm,
            ],
            style=TableStyle(
                [
                    (
                        "LINEABOVE",
                        (0, 0),
                        (-1, 0),
                        0.4,
                        colors.black,
                    ),
                    (
                        "LINEBELOW",
                        (0, 1),
                        (-1, 1),
                        0.4,
                        colors.black,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0.7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0.7,
                    ),
                ]
            ),
        )
    )

    elementos.append(
        Spacer(1, 1.5 * mm)
    )

    # ============================================================
    # CAMPOS
    # ============================================================

    def campo(rotulo: str, valor: str):
        elementos.append(
            Paragraph(
                rotulo.upper(),
                estilo_rotulo,
            )
        )

        elementos.append(
            Paragraph(
                escapar_html(valor) or "Não informado",
                estilo_valor_menor,
            )
        )

        elementos.append(
            Spacer(1, 0.8 * mm)
        )

    campo(
        "Cliente",
        cliente_nome or "Cliente não informado",
    )

    if cliente_documento:
        campo(
            "CPF/CNPJ",
            formatar_documento(cliente_documento),
        )

    campo(
        "Destinatário",
        destinatario or "Não informado",
    )

    campo(
        "Rastreio / CT-e",
        cte or "Não informado",
    )

    campo(
        "Nota Fiscal",
        nf or "Não informado",
    )

    campo(
        "Destino",
        destino,
    )

    # ============================================================
    # CEP / PESO / VOLUMES
    # ============================================================

    elementos.append(
        Table(
            [
                [
                    Paragraph("CEP", estilo_rotulo),
                    Paragraph("PESO", estilo_rotulo),
                    Paragraph("VOLUMES", estilo_rotulo),
                ],
                [
                    Paragraph(
                        formatar_cep(cep),
                        estilo_valor_menor,
                    ),
                    Paragraph(
                        formatar_peso(peso),
                        estilo_valor_menor,
                    ),
                    Paragraph(
                        str(volumes),
                        estilo_valor_menor,
                    ),
                ],
            ],
            colWidths=[
                17 * mm,
                19 * mm,
                12 * mm,
            ],
            style=TableStyle(
                [
                    (
                        "LINEABOVE",
                        (0, 0),
                        (-1, 0),
                        0.4,
                        colors.black,
                    ),
                    (
                        "LINEBELOW",
                        (0, 1),
                        (-1, 1),
                        0.4,
                        colors.black,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0.7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0.7,
                    ),
                ]
            ),
        )
    )

    elementos.append(
        Spacer(1, 1.5 * mm)
    )

    # ============================================================
    # MODALIDADE / PRAZO
    # ============================================================

    modalidade_formatada = (
        modalidade.strip()
        if modalidade
        else "Não informado"
    )

    if modalidade_formatada.upper() == "PACKAGE":
        valor_final = package
    else:
        valor_final = com

    elementos.append(
        Table(
            [
                [
                    Paragraph(
                        "MODALIDADE",
                        estilo_rotulo,
                    ),
                    Paragraph(
                        "PRAZO",
                        estilo_rotulo,
                    ),
                ],
                [
                    Paragraph(
                        escapar_html(modalidade_formatada),
                        estilo_valor,
                    ),
                    Paragraph(
                        escapar_html(
                            formatar_prazo(prazo)
                        ),
                        estilo_valor_menor,
                    ),
                ],
            ],
            colWidths=[
                24 * mm,
                24 * mm,
            ],
            style=TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.black,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        1.5,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        1.5,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                ]
            ),
        )
    )

    elementos.append(
        Spacer(1, 1.5 * mm)
    )

    # ============================================================
    # VALOR FINAL
    # ============================================================

    elementos.append(
        Table(
            [
                [
                    Paragraph(
                        "VALOR FINAL",
                        estilo_centralizado_negrito,
                    )
                ],
                [
                    Paragraph(
                        formatar_moeda(valor_final),
                        estilo_total,
                    )
                ],
            ],
            colWidths=[48 * mm],
            style=TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1.3,
                        colors.black,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        1,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        1.5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        1.5,
                    ),
                ]
            ),
        )
    )

    # ============================================================
    # OBSERVAÇÕES
    # ============================================================

    if observacoes:
        elementos.append(
            Spacer(1, 1.5 * mm)
        )

        elementos.append(
            Paragraph(
                "OBSERVAÇÕES",
                estilo_rotulo,
            )
        )

        elementos.append(
            Paragraph(
                escapar_html(observacoes),
                estilo_valor_menor,
            )
        )

    # ============================================================
    # QR CODE
    # ============================================================

    elementos.append(
        Spacer(1, 2 * mm)
    )

    elementos.append(
        Paragraph(
            "CONSULTE ESTA COTAÇÃO",
            estilo_centralizado_negrito,
        )
    )

    url_consulta = (
        "https://jadlogbras.vercel.app/consulta/"
        f"?numero={numero_cotacao}"
    )

    elementos.append(
        Spacer(1, 0.8 * mm)
    )

    qr = criar_qrcode(url_consulta)
    qr.hAlign = "CENTER"
    elementos.append(qr)

    elementos.append(
        Spacer(1, 0.6 * mm)
    )

    elementos.append(
        Paragraph(
            escapar_html(numero_cotacao),
            estilo_centralizado_negrito,
        )
    )

    # ============================================================
    # CÓDIGO DE BARRAS
    # ============================================================

    elementos.append(
        Spacer(1, 1 * mm)
    )

    codigo = criar_codigo_barras(numero_cotacao)
    codigo.hAlign = "CENTER"
    elementos.append(codigo)

    elementos.append(
        Spacer(1, 1.5 * mm)
    )

    # ============================================================
    # RODAPÉ
    # ============================================================

    elementos.append(
        Paragraph(
            "<b>JADLOG BRÁS</b>",
            estilo_centralizado_negrito,
        )
    )

    elementos.append(
        Paragraph(
            "Av. Vautier, 455 - Brás - São Paulo/SP",
            estilo_centralizado,
        )
    )

    elementos.append(
        Paragraph(
            "Obrigado por escolher a Jadlog Brás.",
            estilo_centralizado,
        )
    )

    elementos.append(
        Paragraph(
            "Recibo válido exclusivamente para atendimento "
            "na unidade Jadlog Brás.",
            estilo_centralizado,
        )
    )

    # ============================================================
    # GERAÇÃO
    # ============================================================

    documento.build(elementos)

    memoria.seek(0)

    nome_arquivo = f"recibo_{numero_cotacao}.pdf"

    return StreamingResponse(
        memoria,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{nome_arquivo}"'
            ),
            "Cache-Control": "no-store",
        },
    )