from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Cliente(BaseModel):
    cpf_cnpj: str
    nome: str
    razao_social: Optional[str] = ""
    endereco: Optional[str] = ""
    cidade: Optional[str] = ""
    uf: Optional[str] = ""
    cep: Optional[str] = ""
    telefone: Optional[str] = ""

class CotacaoResponse(BaseModel):
    numero_cotacao: str
    data: datetime
    cliente_nome: str
    cliente_documento: str
    destino: str
    tipo: str
    prazo: str
    peso: str
    modalidade: str
    valor_base: float
    seguro: float
    total: float
