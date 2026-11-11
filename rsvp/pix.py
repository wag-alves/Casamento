"""
Gerador do payload "Pix Copia e Cola", seguindo o padrão EMV do Banco Central.
Esse texto é o que vira o QR Code de pagamento Pix.

Documentação de referência: Manual de Padrões para Iniciação do Pix (BACEN).
"""
import unicodedata


def _normalizar(texto: str) -> str:
    """Remove acentos e caracteres especiais (o padrão Pix exige texto simples)."""
    if not texto:
        return ''
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip()


def _campo(id_campo: str, valor: str) -> str:
    tamanho = f'{len(valor):02d}'
    return f'{id_campo}{tamanho}{valor}'


def _crc16(payload: str) -> str:
    """CRC16-CCITT (poly 0x1021, valor inicial 0xFFFF), exigido no final do payload Pix."""
    poly = 0x1021
    crc = 0xFFFF
    for byte in payload.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return format(crc, '04X')


def gerar_payload_pix(chave: str, nome: str, cidade: str, valor=None, txid: str = '***', descricao: str = None) -> str:
    """
    Monta a string "Pix Copia e Cola" (usada tanto para gerar o QR Code
    quanto para o botão "copiar código").

    - chave: chave Pix do recebedor (CPF, e-mail, telefone ou chave aleatória)
    - nome: nome do recebedor (máx. 25 caracteres, sem acento)
    - cidade: cidade do recebedor (máx. 15 caracteres, sem acento)
    - valor: valor sugerido (Decimal/float), opcional
    - txid: identificador da transação (sem espaços, máx. 25 caracteres)
    - descricao: descrição opcional (ex: nome do presente)
    """
    nome = _normalizar(nome)[:25] or 'NOIVOS'
    cidade = _normalizar(cidade)[:15] or 'CIDADE'
    txid = (_normalizar(txid) or '***').replace(' ', '')[:25]

    info_conta = _campo('00', 'br.gov.bcb.pix') + _campo('01', chave)
    if descricao:
        info_conta += _campo('02', _normalizar(descricao)[:70])

    payload = (
        _campo('00', '01')                 # Payload Format Indicator
        + _campo('01', '11')               # Point of Initiation (11 = QR estático/reutilizável)
        + _campo('26', info_conta)         # Merchant Account Information (Pix)
        + _campo('52', '0000')             # Merchant Category Code
        + _campo('53', '986')              # Moeda: Real (BRL)
    )

    if valor:
        payload += _campo('54', f'{float(valor):.2f}')

    payload += (
        _campo('58', 'BR')                 # País
        + _campo('59', nome)               # Nome do recebedor
        + _campo('60', cidade)             # Cidade do recebedor
        + _campo('62', _campo('05', txid)) # Additional Data (txid)
    )

    payload += '6304'  # Marca o campo do CRC16 (ID 63, tamanho 04)
    crc = _crc16(payload)
    return payload + crc
