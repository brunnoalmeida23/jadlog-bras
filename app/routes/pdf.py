from __future__ import annotations

import io
import os
import re
from datetime import datetime

from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
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

    return valor


def formatar_moeda(valor: float) -> str:
    texto = f"{float(valor):,.2f}"

    texto = texto.replace(",", "#")
    texto = texto.replace(".", ",")
    texto = texto.replace("#", ".")

    return f"R$ {texto}"


@router.post("/cotacao")
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
):
    memoria = io.BytesIO()

    documento = SimpleDocTemplate(
        memoria,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"Cotação {numero_cotacao}",
        author="Jadlog Brás",
    )

    estilos = getSampleStyleSheet()

    estilo_centralizado = ParagraphStyle(
        "Centralizado",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilo_centralizado,
        fontSize=19,
        leading=22,
        textColor=colors.HexColor("#E31E24"),
        spaceAfter=4,
    )

    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilo_centralizado,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#212529"),
        spaceAfter=12,
    )

    elementos = []

    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "static",
        "logo-jadlog.png",
    )

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=48 * mm,
            height=18 * mm,
        )

        logo.hAlign = "CENTER"
        elementos.append(logo)
        elementos.append(Spacer(1, 4 * mm))

    elementos.append(
        Paragraph(
            "JADLOG BRÁS",
            estilo_titulo,
        )
    )

    elementos.append(
        Paragraph(
            "COTAÇÃO DE FRETE",
            estilo_subtitulo,
        )
    )

    emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

    dados_cotacao = [
        [
            Paragraph("<b>NÚMERO</b>", estilos["Normal"]),
            Paragraph("<b>EMISSÃO</b>", estilos["Normal"]),
        ],
        [
            numero_cotacao,
            emissao,
        ],
        [
            Paragraph("<b>CLIENTE</b>", estilos["Normal"]),
            Paragraph("<b>CPF/CNPJ</b>", estilos["Normal"]),
        ],
        [
            cliente_nome,
            formatar_documento(cliente_documento),
        ],
        [
            Paragraph("<b>DESTINO</b>", estilos["Normal"]),
            Paragraph("<b>CEP</b>", estilos["Normal"]),
        ],
        [
            destino,
            formatar_cep(cep),
        ],
        [
            Paragraph("<b>PESO</b>", estilos["Normal"]),
            Paragraph("<b>VOLUMES</b>", estilos["Normal"]),
        ],
        [
            f"{peso:,.3f} kg".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            str(volumes),
        ],
        [
            Paragraph("<b>VALOR DA NF</b>", estilos["Normal"]),
            Paragraph("<b>PRAZO</b>", estilos["Normal"]),
        ],
        [
            formatar_moeda(valor_nf),
            prazo,
        ],
    ]

    tabela_dados = Table(
        dados_cotacao,
        colWidths=[
            84 * mm,
            84 * mm,
        ],
    )

    tabela_dados.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D8D8D8"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#F1F1F1"),
                ),
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, 2),
                    colors.HexColor("#F1F1F1"),
                ),
                (
                    "BACKGROUND",
                    (0, 4),
                    (-1, 4),
                    colors.HexColor("#F1F1F1"),
                ),
                (
                    "BACKGROUND",
                    (0, 6),
                    (-1, 6),
                    colors.HexColor("#F1F1F1"),
                ),
                (
                    "BACKGROUND",
                    (0, 8),
                    (-1, 8),
                    colors.HexColor("#F1F1F1"),
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
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elementos.append(tabela_dados)
    elementos.append(Spacer(1, 8 * mm))

    tabela_valores = Table(
        [
            [
                Paragraph(
                    "<b>PACKAGE</b>",
                    estilos["Heading3"],
                ),
                Paragraph(
                    f"<b>{formatar_moeda(package)}</b>",
                    estilos["Heading3"],
                ),
            ],
            [
                Paragraph(
                    "<b>.COM</b>",
                    estilos["Heading3"],
                ),
                Paragraph(
                    f"<b>{formatar_moeda(com)}</b>",
                    estilos["Heading3"],
                ),
            ],
        ],
        colWidths=[
            84 * mm,
            84 * mm,
        ],
    )

    tabela_valores.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, 0),
                    1.5,
                    colors.HexColor("#198754"),
                ),
                (
                    "BOX",
                    (0, 1),
                    (-1, 1),
                    1.5,
                    colors.HexColor("#E31E24"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#198754"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, 1),
                    colors.HexColor("#E31E24"),
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
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
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    14,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    14,
                ),
            ]
        )
    )

    elementos.append(tabela_valores)
    elementos.append(Spacer(1, 11 * mm))

    elementos.append(
        Paragraph(
            "<b>VALORES EXCLUSIVOS DA UNIDADE JADLOG BRÁS</b>",
            estilo_centralizado,
        )
    )

    elementos.append(
        Paragraph(
            "AV. VAUTIER, 455 - BRÁS - SÃO PAULO/SP",
            estilo_centralizado,
        )
    )

    elementos.append(
        Paragraph(
            "Cotação sujeita à conferência no atendimento.",
            estilo_centralizado,
        )
    )

    documento.build(elementos)

    memoria.seek(0)

    nome_arquivo = f"cotacao_{numero_cotacao}.pdf"

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