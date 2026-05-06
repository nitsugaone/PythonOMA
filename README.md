# Python OMA

Implementación en Python para envío de configuraciones OTA (OMA Client Provisioning) vía SMS WAP Push.

Inspirizado en [SharpSMS](https://github.com/PavelBansky/SharpSMS) de Pavel Bansky.

## Características

- Generación de perfiles APN completos (Internet + MMS)
- Encoding WBXML compatible con OMA CP
- Encapsulado WAP Push (UDH + WSP)
- Soporte SMPP y módem GSM (en progreso)

## Estructura

```
src/
├── core/
│   └── pdu_builder.py     ← punto de entrada principal
├── oma/
│   ├── wbxml.py           ← encoder WBXML (única fuente de verdad)
│   ├── wap_push.py        ← construcción del PDU WAP Push
│   └── wsp_headers.py     ← headers WSP correctos
transport/
│   └── (SMPP / GSM modem — próximamente)
tests/
│   └── test_pdu.py
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

## Tests

```bash
pytest tests/
```

## Estado

Proyecto en desarrollo orientado a pruebas reales en dispositivos Android.

## Advertencia

El comportamiento depende del dispositivo. Versiones modernas de Android pueden requerir confirmación manual o mecanismos adicionales de seguridad.
