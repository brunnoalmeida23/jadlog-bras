# app/services/tabela_acima_30.py
# Mantido para compatibilidade — mas agora os valores ficam em
# tabela_cliente_final.py (CAPITAL_ACIMA_30 e INTERIOR_ACIMA_30)

from .tabela_cliente_final import (
    CAPITAL_ACIMA_30,
    INTERIOR_ACIMA_30,
)

# Aliases para não quebrar imports antigos
GLM_ACIMA_30 = CAPITAL_ACIMA_30
LUCRO_ACIMA_30 = INTERIOR_ACIMA_30