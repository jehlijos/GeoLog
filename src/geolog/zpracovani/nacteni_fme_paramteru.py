import yaml
from pathlib import Path

class NacteniFmeParametru:
    def __init__(self, nazev_FME_souboru):
        """Třída pro načítání parametrů z FME_config.yaml na základě názvu FME souboru."""
        self.nazev_FME_souboru = nazev_FME_souboru  

    def nacti_parametry(self, fme_config_path=None):
        if fme_config_path is None:
            # Výchozí cesta: root pluginu / config / FME_config.yaml
            fme_config_path = Path(__file__).resolve().parent.parent.joinpath(
                "config", "FME_config.yaml"
            )

        # ověří že FME_config.yaml existuje
        if not Path(fme_config_path).exists():
            raise FileNotFoundError(f"Konfigurační soubor '{fme_config_path}' nebyl nalezen.")

        # ověří že v FME_config.yaml v sekici FME_soubory existuje záznam pro název FME souboru
        with open(fme_config_path, "r", encoding="utf-8") as f:
            fme_config = yaml.safe_load(f)
            soubor_config = None
            for soubor in fme_config.get("FME_soubory", []):
                if soubor.get("FME_nazev_souboru") == self.nazev_FME_souboru:
                    soubor_config = soubor
                    break
        
        if soubor_config is None:
            raise ValueError(f"Záznam pro FME soubor '{self.nazev_FME_souboru}' nebyl nalezen v '{fme_config_path}'.")
        
        format_vystupu = soubor_config.get("format_vystupu") or "gpkg"
        je_lokalni = soubor_config.get("je_lokalni") or True
        volitelne_parametry = {}
        for param in soubor_config.get("volitelne_parametry", []):
            nazev_parametru = param.get("nazev_parametru")
            hodnota_parametru = param.get("hodnota_parametru")
            if nazev_parametru and hodnota_parametru:
                # vytvoř slovník volitelných parametrů pro další použití
                volitelne_parametry[nazev_parametru] = hodnota_parametru

        # Název vystupního souboru přebírá část názvu FME souboru.            
        nazev_vystup = "vystup_" + self.nazev_FME_souboru.replace(".fmw", "")

        return volitelne_parametry, format_vystupu, je_lokalni, nazev_vystup