# Golemio Library Extractor

Generický extraktor pre získavanie dát o mestských knižniciach z Golemio API.

## Požiadavky

- Python 3.8+
- pip package manager

## Inštalácia

1. Naklonujte repozitár:
```bash
git clone https://github.com/your-username/golemio-library-extractor.git
cd golemio-library-extractor
```

2. Vytvorte virtuálne prostredie:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# alebo
venv\Scripts\activate  # Windows
```

3. Nainštalujte závislosti:
```bash
pip install -r requirements.txt
```

## Konfigurácia

1. Získajte API kľúč z [Golemio Developer Portal](https://api.golemio.cz/docs)

2. Nastavte environment variable:
```bash
export GOLEMIO_API_KEY="váš-api-kľúč"
```

Alebo vytvorte `.env` súbor:
```
GOLEMIO_API_KEY=váš-api-kľúč
```

## Použitie

### Jednorazová extrakcia
```bash
python golemio_extractor.py
```

### Naplánovaná extrakcia (denne o 7:00)
```bash
python scheduler.py
```

### Použitie ako modul
```python
from golemio_extractor import GolemioLibraryExtractor

extractor = GolemioLibraryExtractor(api_key="váš-api-kľúč")
df = extractor.extract_libraries()
extractor.save_to_csv(df, "kniznice.csv")
```

## Výstupné dáta

Extraktor produkuje CSV súbor s nasledovnými stĺpcami:
- `id_kniznice` - Unikátny identifikátor knižnice
- `nazov_kniznice` - Názov knižnice
- `ulica` - Adresa ulice
- `psc` - Poštové smerovacie číslo
- `mesto` - Mesto (predvolené: Praha)
- `kraj` - Kraj (predvolené: Hlavní město Praha)
- `krajina` - Krajina (predvolené: Česká republika)
- `zemepisna_sirka` - GPS súradnica - šírka
- `zemepisna_dlzka` - GPS súradnica - dĺžka
- `cas_otvorenia` - Otváracie hodiny

## Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scheduler.py"]
```

### AWS Lambda
Pre deployment na AWS Lambda použite priložený `lambda_handler.py`:
```python
import json
from golemio_extractor import GolemioLibraryExtractor

def lambda_handler(event, context):
    extractor = GolemioLibraryExtractor()
    extractor.run_extraction()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Extraction completed successfully')
    }
```

### Keboola
Pre integráciu s Keboola použite Generic Extractor konfiguráciu v súbore `keboola-config.json`.

## Monitoring

Aplikácia loguje všetky dôležité udalosti. Pre produkčné nasadenie odporúčame:
- Centralizované logovanie (ELK stack, CloudWatch)
- Metriky (Prometheus, Grafana)
- Alerting pri zlyhaní extrakcie

## Licencia

MIT License

## Podpora

Pre otázky a podporu kontaktujte: your-email@example.com