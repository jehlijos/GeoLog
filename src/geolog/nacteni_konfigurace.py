import os
import subprocess
import platform

class Nastaveni:
    def __init__(self, conf_cesta) -> None:
        self.conf_cesta = conf_cesta
    
    def otevrit_yaml(self) -> None:
        """Otevře konfigurační soubor ve výchozím textovém editoru."""
        
        if platform.system() == "Windows":
            os.startfile(self.conf_cesta)
        else:  # Linux a další
            subprocess.call(["xdg-open", self.conf_cesta])   