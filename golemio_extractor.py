import requests
import json
import pandas as pd
from datetime import datetime
import os
import logging
from typing import Dict, List, Optional
import schedule
import time

class GolemioLibraryExtractor:
    """
    Generický extraktor pre dáta o mestských knižniciach z Golemio API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.golemio.cz/v2"
        self.api_key = api_key or os.environ.get('GOLEMIO_API_KEY')
        print(f"DEBUG: Using API key: {self.api_key}")  # Add this line
        self.headers = {
            'X-Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }

        # Nastavenie logovania
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def extract_libraries(self) -> pd.DataFrame:
        """
        Extrahuje dáta o knižniciach z API
        """
        endpoint = f"{self.base_url}/municipallibraries"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            libraries = data.get('features', [])
            
            # Transformácia dát
            extracted_data = []
            for library in libraries:
                properties = library.get('properties', {})
                geometry = library.get('geometry', {})
                coordinates = geometry.get('coordinates', [None, None])
                
                # Spracovanie otváracích hodín
                opening_hours = self._parse_opening_hours(properties.get('opening_hours', {}))
                
                extracted_data.append({
                    'id_kniznice': properties.get('id'),
                    'nazov_kniznice': properties.get('name'),
                    'ulica': properties.get('address', {}).get('street_address'),
                    'psc': properties.get('address', {}).get('postal_code'),
                    'mesto': properties.get('address', {}).get('locality', 'Praha'),
                    'kraj': properties.get('address', {}).get('region', 'Hlavní město Praha'),
                    'krajina': properties.get('address', {}).get('country', 'Česká republika'),
                    'zemepisna_sirka': coordinates[1],
                    'zemepisna_dlzka': coordinates[0],
                    'cas_otvorenia': opening_hours
                })
                
            df = pd.DataFrame(extracted_data)
            self.logger.info(f"Úspešne extrahovaných {len(df)} knižníc")
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Chyba pri volaní API: {e}")
            raise
            
    def _parse_opening_hours(self, hours_data: Dict) -> str:
        """
        Parsuje otváracie hodiny do čitateľného formátu
        """
        if not hours_data:
            return "Neuvedené"
            
        days_sk = {
            'monday': 'Pondelok',
            'tuesday': 'Utorok',
            'wednesday': 'Streda',
            'thursday': 'Štvrtok',
            'friday': 'Piatok',
            'saturday': 'Sobota',
            'sunday': 'Nedeľa'
        }
        
        hours_list = []
        for day_en, day_sk in days_sk.items():
            if day_en in hours_data:
                hours = hours_data[day_en]
                if hours:
                    hours_list.append(f"{day_sk}: {hours}")
                    
        return "; ".join(hours_list) if hours_list else "Neuvedené"
        
    def save_to_csv(self, df: pd.DataFrame, filename: str = None):
        """
        Uloží dáta do CSV súboru
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"kniznice_{timestamp}.csv"
            
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        self.logger.info(f"Dáta uložené do {filename}")
        
    def run_extraction(self):
        """
        Spustí kompletný proces extrakcie
        """
        self.logger.info("Začínam extrakciu dát o knižniciach")
        
        try:
            df = self.extract_libraries()
            self.save_to_csv(df)
            
            # Pre Keboolu by sme tu pridali upload do storage
            # self.upload_to_keboola(df)
            
        except Exception as e:
            self.logger.error(f"Extrakcia zlyhala: {e}")
            raise

def scheduled_extraction():
    """
    Funkcia pre naplánovanú extrakciu
    """
    extractor = GolemioLibraryExtractor(api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzczMCwiaWF0IjoxNzUwOTA0OTMwLCJleHAiOjExNzUwOTA0OTMwLCJpc3MiOiJnb2xlbWlvIiwianRpIjoiYjQyZDYxOTYtZmM1My00ZWYwLTk0YWItOGU2MmUyOGQzNzQwIn0.3zIID-HEsLrSWLUfgv6RYkUEK2n_CIcLMb-mBm-7OKc')
    extractor.run_extraction()

if __name__ == "__main__":
    # Nastavenie dennej extrakcie o 7:00 pražského času
    schedule.every().day.at("07:00").do(scheduled_extraction)
    
    # Pre testovanie - spustí extrakciu ihneď
    extractor = GolemioLibraryExtractor(api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzczMCwiaWF0IjoxNzUwOTA0OTMwLCJleHAiOjExNzUwOTA0OTMwLCJpc3MiOiJnb2xlbWlvIiwianRpIjoiYjQyZDYxOTYtZmM1My00ZWYwLTk0YWItOGU2MmUyOGQzNzQwIn0.3zIID-HEsLrSWLUfgv6RYkUEK2n_CIcLMb-mBm-7OKc')
    extractor.run_extraction()
    
    # Uncomment pre produkciu
    #while True:
         #schedule.run_pending()
         #time.sleep(60)

