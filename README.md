# Python OMA

Implementación en Python para envío de configuraciones OTA (OMA Client Provisioning) vía SMS WAP Push.

> ⚠️ **Este proyecto fue desarrollado exclusivamente para [iMowi](https://imowi.ar).**
> Su propósito es la provisión automática de configuraciones APN/MMS para los usuarios de la red iMowi.

---

## Aviso legal / Disclaimer

Este repositorio está diseñado y mantenido para uso interno de **iMowi**.

Si alguien desea adaptar este código para otro operador o caso de uso:

- Puede hacerlo bajo su **propia responsabilidad**.
- El autor **no se hace responsable** por modificaciones, usos derivados, ni por el comportamiento del código en redes o dispositivos de terceros.
- Cada operador tiene su propio sistema OTA, sus propias políticas de seguridad y sus propios requisitos de compatibilidad.
- El uso indebido de mensajes WAP Push puede violar términos de servicio de operadores y legislación local.

---

## Características

- Generación de perfiles APN completos (Internet + MMS)
- Encoding WBXML compatible con OMA CP
- Encapsulado WAP Push (UDH + WSP)
- Firma HMAC-MD5 (NETWPIN / USERPIN / USERNETWPIN)
- Herramientas de debug, diff y parsing de PDUs reales
- Soporte SMPP y módem GSM (en progreso)

## Estructura

```
src/
├── core/
│   └── pdu_builder.py         ← punto de entrada principal
├── oma/
│   ├── wbxml.py               ← encoder WBXML (única fuente de verdad)
│   ├── wap_push.py            ← construcción del PDU WAP Push
│   ├── wsp_headers.py         ← headers WSP + MAC opcional
│   └── hmac_signer.py         ← firma HMAC-MD5 (nivel operador)
├── debug/
│   ├── pdu_debug.py           ← inspección visual de PDU por capas
│   ├── pdu_diff.py            ← diff byte a byte entre PDUs
│   ├── pdu_parser.py          ← parser inverso: hex → estructura
│   └── matrix_logger.py       ← registro CSV de resultados por dispositivo
transport/                     ← (SMPP / GSM modem — próximamente)
tests/
├── test_pdu.py
├── test_hmac.py
├── test_diff.py
└── test_parser.py
tools/
├── generate_pdu.py            ← genera + inspecciona PDU por CLI
├── compare_pdus.py            ← diff entre PDU generado y captura real
└── parse_pdu.py               ← parsea PDU crudo (AT+CMGR / bin file)
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```python
from core.pdu_builder import PDUBuilder

pdu = PDUBuilder.build_full(
    apn="apn1.catel.org.ar",
    user="imowi",
    mmsc="http://mmsc.imowi.ar",
    proxy_ip="10.10.10.10",
    proxy_port=8080
)

print(pdu.hex())
```

### Generar PDU por CLI

```bash
python tools/generate_pdu.py \
    --apn apn1.catel.org.ar \
    --user imowi \
    --mmsc http://mmsc.imowi.ar \
    --proxy 10.10.10.10 \
    --port 8080 \
    --out pdu.bin
```

### Parsear un PDU capturado (AT+CMGR)

```bash
python tools/parse_pdu.py --hex 060504 0b84 23f0 ...
```

### Comparar contra PDU real de operador

```bash
python tools/compare_pdus.py --gen pdu.bin --ref real_operator.bin
```

## Tests

```bash
pytest tests/ -v
```

## Estado

Proyecto en desarrollo activo, orientado a pruebas reales en dispositivos Android con red iMowi.

## Advertencia técnica

El comportamiento depende del dispositivo y la versión de Android.
Versiones modernas pueden requerir confirmación manual o firma HMAC.
No existe un payload universal — la compatibilidad se valida por dispositivo.
