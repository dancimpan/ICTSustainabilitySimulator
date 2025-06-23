import os
from dotenv import load_dotenv

# --- Încărcare variabile de mediu din fișierul .env ---
# Este bine să încărcăm variabilele de mediu devreme,
# dar cheia API specifică va fi preluată unde este necesară (ex. în api_client.py)
load_dotenv()

# --- 1. Definirea Unităților de Cost Abstracte ---
COST_PER_COMPARISON_CPU = 1.0
COST_PER_SWAP_FULL_RECORD_CPU = 5.0
COST_PER_SWAP_KEY_INDEX_CPU = 2.0
COST_PER_ARITHMETIC_OP_CPU = 0.5
COST_PER_MEMORY_ACCESS_CPU = 0.1
COST_PER_REGEX_MATCH_CPU = 10.0
COST_PER_STRING_CHECK_CPU = 0.2

# --- Profiluri Hardware ---
HARDWARE_PROFILES = {
    "Laptop Modern Eficient": {"kwh_per_cpu_op": 0.00000000008, "kwh_per_data_move": 0.00000000004, "description": "Consum redus."},
    "Desktop Performant Mediu": {"kwh_per_cpu_op": 0.00000000012, "kwh_per_data_move": 0.00000000006, "description": "Echilibru."},
    "Server Puternic (sau Desktop Gaming)": {"kwh_per_cpu_op": 0.00000000020, "kwh_per_data_move": 0.00000000010, "description": "Performanță maximă."},
    "Dispozitiv IoT/Embeded (Consum Redus)": {"kwh_per_cpu_op": 0.00000000003, "kwh_per_data_move": 0.00000000002, "description": "Consum minim."},
    "Cloud VM (General Purpose)": {"kwh_per_cpu_op": 0.00000000010, "kwh_per_data_move": 0.00000000005, "description": "VM Cloud general."}
}
DEFAULT_HARDWARE_PROFILE_NAME = "Desktop Performant Mediu"

# --- Valori CO2 ---
GCO2EQ_PER_KWH_DEFAULT = 275.0 # Valoare implicită pentru gCO2eq/kWh

# --- Nume Scenarii ---
SCENARIU_SORTARE = "Scenariul 1: Sortarea Datelor Clienților"
SCENARIU_RAPORT_VANZARI = "Scenariul 2: Generarea Raportului de Vânzări"
SCENARIU_FILTRARE_LOGURI = "Scenariul 3: Filtrarea și Analiza Log-urilor"
SCENARIO_OPTIONS = [SCENARIU_SORTARE, SCENARIU_RAPORT_VANZARI, SCENARIU_FILTRARE_LOGURI]

# --- Opțiuni Sursă CO2 ---
ZONE_MEDIA_UE = "Media UE (Implicit)"
ZONE_ROMANIA_API = "România (Live API)"
CO2_ZONE_OPTIONS = [ZONE_MEDIA_UE, ZONE_ROMANIA_API]

# --- Valori Implicite pentru Input-uri Sidebar ---
DEFAULT_INPUT_VALUES = {
    's1_N': 1000, 's1_avg_rec_size': 100, 's1_key_idx_size': 5,
    's2_N_trans': 10000, 's2_avg_items': 3, 's2_trans_header_size': 20, 's2_item_size': 10,
    's3_N_lines': 100000, 's3_avg_line_len': 150, 's3_err_perc': 5, 's3_err_msg_size': 50
}

# --- Mesaje UI (opțional, pentru centralizare) ---
APP_TITLE = "🌍 Simulator de Impact al Practicilor Software Verzi"
APP_SUBHEADER = "O unealtă interactivă pentru a estima și compara impactul asupra resurselor, consumul energetic și emisiile de CO2 asociate diferitelor abordări de procesare a datelor."
SIDEBAR_HEADER = "⚙️ Configurare Simulare"
RUN_BUTTON_TEXT = "🚀 Rulează Simulare"
RUN_BUTTON_TOOLTIP = "Apasă pentru a calcula și afișa rezultatele"
INFO_START_MESSAGE = "⬅️ Alegeți un scenariu, ajustați parametrii din bara laterală și apăsați 'Rulează Simulare' pentru a vedea rezultatele."
DISCLAIMER_TEXT = """
**Notă:** Estimările de energie și CO2 sunt **ILUSTRATIVE** și se bazează pe factori de conversie aproximativi și pe profilul hardware selectat.
Performanța reală și consumul energetic pot varia considerabil.
Scopul principal este de a demonstra diferențele *relative* de impact între diverse abordări.
"""

# --- Texte Explicative pentru Modele ---
# Dicționar care mapează numele modelului la explicația sa detaliată.
# Folosim Markdown pentru formatare.

MODEL_EXPLANATIONS = {
    "Sortare Standard (tip BubbleSort)": """
    **Analiză:** Acest model simulează un algoritm ineficient, cu complexitate **O(N²)**. Pentru fiecare element, parcurge aproape întreaga listă, ducând la un număr foarte mare de comparații și interschimbări (swap-uri).
    
    **Problemă:** Fiecare interschimbare implică mutarea în memorie a întregii înregistrări, ceea ce este foarte costisitor energetic, mai ales pentru înregistrări de mari dimensiuni.
    
    **Recomandare:** Evitați algoritmii cu complexitate pătratică sau mai mare pentru seturi de date care pot crește în dimensiune.
    """,
    
    "Sortare Eficientă (tip Quicksort)": """
    **Analiză:** Acest model folosește un algoritm eficient cu complexitate medie **O(N log N)**. Numărul de operații CPU crește mult mai lent decât la modelul standard.
    
    **Problemă:** Deși este eficient din punct de vedere al CPU, acest algoritm încă mută înregistrările complete în memorie în timpul procesului de sortare, ceea ce poate fi un punct de ineficiență.
    
    **Recomandare:** Folosiți algoritmi cu complexitate `N log N` ca standard. Pentru un plus de eficiență, analizați dacă mișcarea datelor poate fi redusă.
    """,
    
    "Sortare-Index (Sortare Eficientă Chei)": """
    **Analiză:** Acesta este un model **foarte eficient energetic**. Principiul este **reducerea mișcării datelor (data movement)**.
    
    1.  Se creează o structură auxiliară ușoară (doar cheia de sortare și un index/pointer la înregistrarea originală).
    2.  Se sortează eficient **doar această listă mică**. Mutarea unor perechi (cheie, index) este mult mai ieftină energetic decât mutarea unor înregistrări mari.
    3.  La final, datele originale pot fi reordonate o singură dată, dacă este necesar.
    
    **Recomandare:** Când sortați obiecte mari, sortați o listă de indecși sau pointeri, nu obiectele în sine. Este un compromis excelent între un consum suplimentar de memorie și o reducere masivă a mișcării datelor.
    """,
    
    "Raport Vânzări Standard (Multi-Pass)": """
    **Analiză:** Acest model încarcă toate datele în memorie și le parcurge de mai multe ori (multi-pass) pentru a calcula diverse agregate. Creează structuri de date intermediare care ocupă memorie suplimentară.
    
    **Problemă:** Accesarea repetată a memoriei și stocarea de date intermediare cresc atât consumul de energie, cât și amprenta de memorie a aplicației.
    
    **Recomandare:** Proiectați algoritmii pentru a procesa datele într-o singură trecere (single-pass) ori de câte ori este posibil.
    """,
    
    "Raport Vânzări Verde (Single-Pass)": """
    **Analiză:** Acest model aplică principiul **procesării în flux (streaming)**. Datele sunt citite o singură dată, iar calculele sunt efectuate "din mers".
    
    **Eficiență:** Se elimină necesitatea stocării datelor intermediare și se reduce drastic mișcarea datelor, deoarece fiecare element este "atins" o singură dată. Amprenta de memorie este minimă (doar variabilele pentru agregate).
    
    **Recomandare:** Pentru operațiuni de agregare, adoptați o abordare de tip streaming. Acest lucru este esențial în procesarea de date la scară mare (Big Data).
    """,
    
    "Filtrare Log Standard (Full Load, Regex All)": """
    **Analiză:** O abordare directă, dar ineficientă:
    1.  **Încărcare completă:** Tot fișierul de log este citit integral în memorie, ceea ce poate fi problematic pentru fișiere mari.
    2.  **Operație costisitoare pe tot setul de date:** O expresie regulată (Regex), care este costisitoare pentru CPU, este aplicată pe **fiecare linie** din fișier.
    
    **Recomandare:** Evitați încărcarea fișierelor mari în memorie. Nu aplicați operații costisitoare pe date care pot fi filtrate în prealabil printr-o metodă mai ieftină.
    """,
    
    "Filtrare Log Verde (Stream, Target Regex)": """
    **Analiză:** Acest model combină două principii "verzi":
    1.  **Procesare în flux (Streaming):** Se citește o singură linie în memorie la un moment dat, menținând o amprentă de memorie constantă și mică **O(1)**.
    2.  **Filtrare timpurie (Rate, Shape, and Shift Left):** Se aplică mai întâi o verificare foarte ieftină (ex: `if "ERROR" in line`). Doar pentru liniile care trec de acest filtru rapid se aplică operația costisitoare (Regex).
    
    **Recomandare:** "Mutați logica la stânga" - efectuați operațiunile ieftine și de filtrare cât mai devreme posibil pentru a reduce volumul de date pe care trebuie să-l procesați cu operațiuni scumpe.
    """
}