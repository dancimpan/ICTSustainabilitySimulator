# simulator_v1.py

import math # Pentru calcule cu log2 (logaritm în baza 2)
import matplotlib.pyplot as plt # Importăm matplotlib
import numpy as np # Importăm numpy pentru a ajuta la aranjarea barelor

# --- 1. Definirea Unităților de Cost Abstracte (Acestea sunt valori ilustrative pe care le poți ajusta) ---
# Acestea reprezintă unități abstracte de "muncă" sau "dimensiune".
# Valorile absolute nu contează la fel de mult ca diferențele lor relative
# și modul în care acestea scalează cu N.

COST_PER_COMPARISON_CPU = 1          # "Operație" CPU pentru o comparație
COST_PER_SWAP_FULL_RECORD_CPU = 5    # "Operații" CPU pentru interschimbarea a două înregistrări complete (implică mai mult decât o simplă comparație)
COST_PER_SWAP_KEY_INDEX_CPU = 2      # "Operații" CPU pentru interschimbarea a două perechi mici cheie-index

# Unități de mișcare a datelor (de ex., ar putea fi "octeți" abstracți sau "cuvinte de memorie mutate")
# Pentru simplitate, să spunem că mutarea unei înregistrări costă proporțional cu dimensiunea sa.
# Și mutarea unei perechi cheie-index costă proporțional cu dimensiunea sa mai mică.

# --- 2. Definirea Funcțiilor Model pentru Scenariile de Sortare ---

def model_standard_sort(N, average_record_size_data_units):
    """
    Modelează o sortare standard, mai puțin eficientă (precum Bubble Sort) pe înregistrări complete.
    Estimează operațiile CPU, mișcarea datelor și utilizarea memoriei.
    """
    # Estimări teoretice pentru Bubble Sort (cazul cel mai defavorabil/mediu)
    comparisons = N * (N - 1) / 2  # Aproximativ N^2 / 2
    swaps = N * (N - 1) / 4      # Aproximativ N^2 / 4 în medie (poate fi N^2/2 în cazul cel mai defavorabil)

    cpu_operations = (comparisons * COST_PER_COMPARISON_CPU) + \
                     (swaps * COST_PER_SWAP_FULL_RECORD_CPU)

    # Mișcarea datelor: fiecare interschimbare mută două înregistrări complete.
    # Totuși, pentru a simplifica, să considerăm datele efective mutate prin interschimbări.
    # Dacă o înregistrare are 'average_record_size_data_units', o interschimbare implică mutarea datelor proporțional cu aceasta.
    data_movement = swaps * average_record_size_data_units * 2 # Fiecare interschimbare mută două elemente

    # Utilizarea memoriei: stochează toate cele N înregistrări complete
    memory_usage_data_units = N * average_record_size_data_units

    return {
        "name": "Sortare Standard (tip BubbleSort)",
        "cpu_operations": cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": memory_usage_data_units,
        "complexity_cpu": "O(N^2)",
        "complexity_memory": "O(N)"
    }

def model_efficient_sort(N, average_record_size_data_units):
    """
    Modelează o sortare eficientă (precum Quicksort/MergeSort) pe înregistrări complete.
    Estimează operațiile CPU, mișcarea datelor și utilizarea memoriei.
    """
    if N <= 1: # Cazul de bază pentru recursivitate, sau N foarte mic
        comparisons = N
        swaps = 0
    else:
        # Estimări teoretice pentru Quicksort/MergeSort (cazul mediu)
        comparisons = N * math.log2(N)
        swaps = N * math.log2(N) / 2 # Aproximație, poate varia

    cpu_operations = (comparisons * COST_PER_COMPARISON_CPU) + \
                     (swaps * COST_PER_SWAP_FULL_RECORD_CPU)

    data_movement = swaps * average_record_size_data_units * 2

    # Utilizarea memoriei: stochează N înregistrări complete.
    # Sortările eficiente "in-place" precum Quicksort folosesc spațiu auxiliar pe stivă O(log N).
    # MergeSort folosește spațiu auxiliar O(N). Să modelăm pe baza datelor primare.
    memory_usage_data_units = N * average_record_size_data_units
    aux_memory_logN = math.log2(N) * 1 # Factor mic pentru spațiul pe stivă dacă e tip Quicksort

    return {
        "name": "Sortare Eficientă (tip Quicksort)",
        "cpu_operations": cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": memory_usage_data_units,
        "aux_memory_units (stack)": aux_memory_logN,
        "complexity_cpu": "O(N log N)",
        "complexity_memory": "O(N) + O(log N) aux" # Memorie principală + auxiliară pe stivă
    }

def model_sort_index(N, average_record_size_data_units, size_of_key_index_pair_data_units):
    """
    Modelează sortarea unei liste de perechi (cheie, index_original), apoi reordonarea.
    Estimează operațiile CPU, mișcarea datelor și utilizarea memoriei.
    """
    # --- Pasul 1: Crearea perechilor cheie-index ---
    # Presupunem că crearea fiecărei perechi are un cost CPU mic
    cpu_ops_creation = N * 1 # de ex., 1 operație per înregistrare pentru a extrage cheia și indexul
    memory_for_key_index_list = N * size_of_key_index_pair_data_units

    # --- Pasul 2: Sortarea perechilor cheie-index (folosind un algoritm eficient) ---
    if N <= 1:
        key_comparisons = N
        key_swaps = 0
    else:
        key_comparisons = N * math.log2(N)
        key_swaps = N * math.log2(N) / 2 # Aproximație

    cpu_ops_sorting_keys = (key_comparisons * COST_PER_COMPARISON_CPU) + \
                           (key_swaps * COST_PER_SWAP_KEY_INDEX_CPU)
    data_movement_sorting_keys = key_swaps * size_of_key_index_pair_data_units * 2

    # --- Pasul 3: Reordonarea înregistrărilor complete pe baza perechilor cheie-index sortate ---
    # Presupunem că accesarea și plasarea fiecărei înregistrări are un cost CPU
    cpu_ops_reordering = N * 2 # de ex., 1 operație pentru a citi originalul, 1 pentru a scrie în noua locație
    # Mișcarea datelor: N înregistrări complete sunt mutate în pozițiile lor finale sortate
    data_movement_reordering = N * average_record_size_data_units

    # --- Totaluri ---
    total_cpu_operations = cpu_ops_creation + cpu_ops_sorting_keys + cpu_ops_reordering
    total_data_movement = data_movement_sorting_keys + data_movement_reordering

    # Utilizarea maximă a memoriei: lista originală + lista cheie-index + potențial noua listă sortată
    # Pentru simplitate, să presupunem că lista originală + lista cheie-index este o parte cheie a vârfului de memorie.
    # Dacă reordonarea se face "in-place" sau într-o listă nouă, acest lucru poate varia.
    # Să modelăm memoria pentru datele originale + lista auxiliară cheie-index.
    peak_memory_usage_data_units = (N * average_record_size_data_units) + memory_for_key_index_list

    return {
        "name": "Sortare-Index (Sortare Eficientă Chei)",
        "cpu_operations": total_cpu_operations,
        "data_movement_units": total_data_movement,
        "peak_memory_usage_data_units": peak_memory_usage_data_units,
        "complexity_cpu": "O(N log N)", # Dominat de sortarea cheilor
        "complexity_memory": "O(N) (original) + O(N) (chei)" # Memorie pentru datele originale + memorie pentru chei
    }


# --- 3. Logica Principală a Simulației ---
if __name__ == "__main__":
    print("--- Simulator de Impact al Practicilor Software Verzi (Scenariu Sortare) ---")

    # --- Definirea Parametrilor de Intrare pentru Scenariu ---
    num_records_N = 1000  # Numărul de înregistrări client
    # Unități abstracte de dimensiune pentru date
    avg_record_size = 100       # de ex., 100 unități de date pentru o înregistrare client completă
    key_index_pair_size = 5     # de ex., 5 unități de date pentru o pereche (dată, index)

    print(f"\nSimulare pentru N = {num_records_N} înregistrări:")
    print(f"Dimensiune Medie Înregistrare: {avg_record_size} unități de date")
    print(f"Dimensiune Pereche Cheie-Index: {key_index_pair_size} unități de date")
    print("--------------------------------------------------------------------")

    # --- Rularea Modelelor ---
    results_standard = model_standard_sort(num_records_N, avg_record_size)
    results_efficient = model_efficient_sort(num_records_N, avg_record_size)
    results_sort_index = model_sort_index(num_records_N, avg_record_size, key_index_pair_size)

    # --- Afișarea Rezultatelor ---
    all_results = [results_standard, results_efficient, results_sort_index]

    for result in all_results:
        print(f"\nModel: {result['name']}")
        print(f"  Complexitate (CPU): {result['complexity_cpu']}")
        print(f"  Operații CPU Estimate: {result['cpu_operations']:,.0f}") # :_ pentru separator mii în funcție de localizare, :.0f pentru 0 zecimale
        print(f"  Unități de Mișcare a Datelor Estimate: {result['data_movement_units']:,.0f}")
        if "memory_usage_data_units" in result:
            print(f"  Utilizare Memorie Estimată (Date Primare): {result['memory_usage_data_units']:,.0f}")
        if "peak_memory_usage_data_units" in result:
             print(f"  Utilizare Maximă Memorie Estimată: {result['peak_memory_usage_data_units']:,.0f}")
        if "aux_memory_units (stack)" in result:
            print(f"  Memorie Auxiliară Estimată (Stivă): {result['aux_memory_units (stack)']:,.2f}") # .2f pentru 2 zecimale
        print("---")

    print("\nNotă: Acestea sunt modele simplificate. Performanța reală depinde de mulți factori.")
    print("Scopul este de a ilustra diferențele relative bazate pe alegerile algoritmice.")


    # ---  Funcție pentru a crea și afișa grafice ---
def plot_results(results_list):
    """
    Generează și afișează diagrame de bare pentru a compara rezultatele modelelor.
    """
    model_names = [res['name'] for res in results_list]
    cpu_ops = [res['cpu_operations'] for res in results_list]
    data_movement = [res['data_movement_units'] for res in results_list]

    # Pentru memorie, trebuie să gestionăm cazurile unde cheile pot diferi
    # (de ex., 'memory_usage_data_units' vs 'peak_memory_usage_data_units')
    # Vom folosi o valoare implicită de 0 dacă o cheie specifică lipsește.
    memory_usage = []
    for res in results_list:
        if 'peak_memory_usage_data_units' in res:
            memory_usage.append(res['peak_memory_usage_data_units'])
        elif 'memory_usage_data_units' in res:
            memory_usage.append(res['memory_usage_data_units'])
        else:
            memory_usage.append(0) # Valoare implicită dacă nu se găsește nicio cheie de memorie

    num_models = len(model_names)
    index = np.arange(num_models) # Pozițiile x pentru grupuri
    bar_width = 0.25 # Lățimea barelor

    fig, ax = plt.subplots(3, 1, figsize=(12, 18)) # 3 sub-grafice, 1 coloană

    # Grafic 1: Operații CPU
    ax[0].bar(index, cpu_ops, bar_width, label='Operații CPU', color='skyblue')
    ax[0].set_ylabel('Operații CPU Estimate')
    ax[0].set_title('Compararea Operațiilor CPU Estimate pe Model')
    ax[0].set_xticks(index)
    ax[0].set_xticklabels(model_names, rotation=15, ha="right") # Rotim etichetele pentru lizibilitate
    ax[0].legend()
    ax[0].grid(True, linestyle='--', alpha=0.7) # Adăugăm un grid

    # Formatarea axei Y pentru lizibilitate (cu separatori de mii)
    ax[0].get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ',')))


    # Grafic 2: Mișcarea Datelor
    ax[1].bar(index, data_movement, bar_width, label='Mișcare Date', color='lightcoral')
    ax[1].set_ylabel('Unități de Mișcare a Datelor Estimate')
    ax[1].set_title('Compararea Mișcării Datelor Estimate pe Model')
    ax[1].set_xticks(index)
    ax[1].set_xticklabels(model_names, rotation=15, ha="right")
    ax[1].legend()
    ax[1].grid(True, linestyle='--', alpha=0.7)
    ax[1].get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Grafic 3: Utilizarea Memoriei
    ax[2].bar(index, memory_usage, bar_width, label='Utilizare Memorie', color='lightgreen')
    ax[2].set_ylabel('Unități de Memorie Estimate')
    ax[2].set_title('Compararea Utilizării Memoriei Estimate pe Model')
    ax[2].set_xticks(index)
    ax[2].set_xticklabels(model_names, rotation=15, ha="right")
    ax[2].legend()
    ax[2].grid(True, linestyle='--', alpha=0.7)
    ax[2].get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    fig.tight_layout() # Ajustează automat sub-graficele pentru a se potrivi în figură
    plt.show() # Afișează graficele


# --- 3. Logica Principală a Simulației ---
if __name__ == "__main__":
    print("--- Simulator de Impact al Practicilor Software Verzi (Scenariu Sortare) ---")

    # --- Definirea Parametrilor de Intrare pentru Scenariu ---
    num_records_N = 1000
    avg_record_size = 100
    key_index_pair_size = 5

    print(f"\nSimulare pentru N = {num_records_N} înregistrări:")
    print(f"Dimensiune Medie Înregistrare: {avg_record_size} unități de date")
    print(f"Dimensiune Pereche Cheie-Index: {key_index_pair_size} unități de date")
    print("--------------------------------------------------------------------")

    results_standard = model_standard_sort(num_records_N, avg_record_size)
    results_efficient = model_efficient_sort(num_records_N, avg_record_size)
    results_sort_index = model_sort_index(num_records_N, avg_record_size, key_index_pair_size)

    all_results = [results_standard, results_efficient, results_sort_index]

    for result in all_results:
        print(f"\nModel: {result['name']}")
        print(f"  Complexitate (CPU): {result['complexity_cpu']}")
        print(f"  Operații CPU Estimate: {result['cpu_operations']:,.0f}")
        print(f"  Unități de Mișcare a Datelor Estimate: {result['data_movement_units']:,.0f}")
        if "memory_usage_data_units" in result:
            print(f"  Utilizare Memorie Estimată (Date Primare): {result['memory_usage_data_units']:,.0f}")
        if "peak_memory_usage_data_units" in result:
             print(f"  Utilizare Maximă Memorie Estimată: {result['peak_memory_usage_data_units']:,.0f}")
        if "aux_memory_units (stack)" in result:
            print(f"  Memorie Auxiliară Estimată (Stivă): {result['aux_memory_units (stack)']:,.2f}")
        print("---")

    print("\nNotă: Acestea sunt modele simplificate. Performanța reală depinde de mulți factori.")
    print("Scopul este de a ilustra diferențele relative bazate pe alegerile algoritmice.")

    # --- NOU: Apelarea funcției de plotare ---
    plot_results(all_results)


    ########################################################## De aici in jos ultima versiune functionala a codului nescindat ###############################

    # app_streamlit.py

import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
import requests
import os
from datetime import datetime, timedelta
import pandas as pd # Adăugat pentru tabelul de reduceri
import plotly.express as px

# --- Încărcare variabile de mediu din fișierul .env ---
from dotenv import load_dotenv
load_dotenv()
EM_API_KEY = os.getenv("EM_API_KEY")

# --- 1. Definirea Unităților de Cost Abstracte și Profiluri Hardware ---
COST_PER_COMPARISON_CPU = 1.0
COST_PER_SWAP_FULL_RECORD_CPU = 5.0
COST_PER_SWAP_KEY_INDEX_CPU = 2.0
COST_PER_ARITHMETIC_OP_CPU = 0.5
COST_PER_MEMORY_ACCESS_CPU = 0.1
COST_PER_REGEX_MATCH_CPU = 10.0
COST_PER_STRING_CHECK_CPU = 0.2

HARDWARE_PROFILES = {
    "Laptop Modern Eficient": {"kwh_per_cpu_op": 0.00000000008, "kwh_per_data_move": 0.00000000004, "description": "Consum redus."},
    "Desktop Performant Mediu": {"kwh_per_cpu_op": 0.00000000012, "kwh_per_data_move": 0.00000000006, "description": "Echilibru."},
    "Server Puternic (sau Desktop Gaming)": {"kwh_per_cpu_op": 0.00000000020, "kwh_per_data_move": 0.00000000010, "description": "Performanță maximă."},
    "Dispozitiv IoT/Embeded (Consum Redus)": {"kwh_per_cpu_op": 0.00000000003, "kwh_per_data_move": 0.00000000002, "description": "Consum minim."},
    "Cloud VM (General Purpose)": {"kwh_per_cpu_op": 0.00000000010, "kwh_per_data_move": 0.00000000005, "description": "VM Cloud general."}
}
DEFAULT_HARDWARE_PROFILE_NAME = "Desktop Performant Mediu"
GCO2EQ_PER_KWH_DEFAULT = 275.0

# --- Funcții Utilitare și Model ---
@st.cache_data(ttl=24*3600)
def get_romania_carbon_intensity(api_key):
    zone_code = "RO"
    if not api_key:
        if 'api_key_warning_shown_details' not in st.session_state:
            st.warning(f"Cheia API (EM_API_KEY) lipsește. Se va folosi valoarea implicită pentru CO2.")
            st.session_state.api_key_warning_shown_details = True
        return None
    headers = {'auth-token': api_key}
    try:
        response = requests.get(f'https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_code}', headers=headers)
        response.raise_for_status(); data = response.json(); carbon_intensity = data.get('carbonIntensity')
        if carbon_intensity is not None:
            if 'api_call_success_msg_shown' not in st.session_state or not st.session_state.api_call_success_msg_shown.get(zone_code, False):
                st.success(f"Intensitatea CO2 pentru România: {carbon_intensity:.2f} gCO2eq/kWh (Sursa: Electricity Maps). Cache: 24h.")
                if 'api_call_success_msg_shown' not in st.session_state: st.session_state.api_call_success_msg_shown = {}
                st.session_state.api_call_success_msg_shown[zone_code] = True
            return float(carbon_intensity)
        else: st.warning(f"Răspuns API invalid pentru România. Se folosește valoarea implicită."); return None
    except Exception as e: st.error(f"Eroare API România: {e}. Se folosește valoarea implicită."); return None

def calculate_energy_co2(cpu_ops, data_movement, kwh_cpu_factor, kwh_data_factor, gco2eq_per_kwh_factor):
    estimated_kwh = (cpu_ops * kwh_cpu_factor) + (data_movement * kwh_data_factor)
    estimated_co2_g = estimated_kwh * gco2eq_per_kwh_factor
    return estimated_kwh, estimated_co2_g

# == SCENARIUL 1: SORTAREA DATELOR ==
def model_standard_sort(N, average_record_size_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare Standard (tip BubbleSort)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N^2)", "complexity_memory": "O(N)"}
    if N <= 0 or average_record_size_data_units <=0: return default_return
    comparisons = float(N * (N - 1) / 2); swaps = float(N * (N - 1) / 4)
    cpu_operations = (comparisons * COST_PER_COMPARISON_CPU) + (swaps * COST_PER_SWAP_FULL_RECORD_CPU)
    data_movement = swaps * average_record_size_data_units * 2.0
    memory_usage_data_units = float(N * average_record_size_data_units)
    kwh, co2 = calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Sortare Standard (tip BubbleSort)", "cpu_operations": cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": memory_usage_data_units, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(N^2)", "complexity_memory": "O(N)"}

def model_efficient_sort(N, average_record_size_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare Eficientă (tip Quicksort)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "aux_memory_units (stack)": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) + O(log N) aux"}
    if N <= 0 or average_record_size_data_units <=0: return default_return
    aux_memory_logN = 0.0; comparisons, swaps = 0.0, 0.0
    if N == 1: comparisons, swaps = 1.0, 0.0
    elif N > 1: comparisons = float(N * math.log2(N)); swaps = float(N * math.log2(N) / 2.0); aux_memory_logN = float(math.log2(N) * 1.0)
    cpu_operations = (comparisons * COST_PER_COMPARISON_CPU) + (swaps * COST_PER_SWAP_FULL_RECORD_CPU)
    data_movement = swaps * average_record_size_data_units * 2.0
    memory_usage_data_units = float(N * average_record_size_data_units)
    kwh, co2 = calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Sortare Eficientă (tip Quicksort)", "cpu_operations": cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": memory_usage_data_units, "aux_memory_units (stack)": aux_memory_logN, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) + O(log N) aux"}

def model_sort_index(N, average_record_size_data_units, size_of_key_index_pair_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare-Index (Sortare Eficientă Chei)", "cpu_operations": 0.0, "data_movement_units": 0.0, "peak_memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) (original) + O(N) (chei)"}
    if N <= 0 or average_record_size_data_units <=0 or size_of_key_index_pair_data_units <=0: return default_return
    cpu_ops_creation = float(N * 1.0); memory_for_key_index_list = float(N * size_of_key_index_pair_data_units)
    key_comparisons, key_swaps = 0.0, 0.0
    if N == 1: key_comparisons, key_swaps = 1.0, 0.0
    elif N > 1 : key_comparisons = float(N * math.log2(N)); key_swaps = float(N * math.log2(N) / 2.0)
    cpu_ops_sorting_keys = (key_comparisons * COST_PER_COMPARISON_CPU) + (key_swaps * COST_PER_SWAP_KEY_INDEX_CPU)
    data_movement_sorting_keys = key_swaps * size_of_key_index_pair_data_units * 2.0
    cpu_ops_reordering = float(N * 2.0); data_movement_reordering = float(N * average_record_size_data_units)
    total_cpu_operations = cpu_ops_creation + cpu_ops_sorting_keys + cpu_ops_reordering
    total_data_movement = data_movement_sorting_keys + data_movement_reordering
    peak_memory_usage_data_units = (N * average_record_size_data_units) + memory_for_key_index_list
    kwh, co2 = calculate_energy_co2(total_cpu_operations, total_data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Sortare-Index (Sortare Eficientă Chei)", "cpu_operations": total_cpu_operations, "data_movement_units": total_data_movement, "peak_memory_usage_data_units": peak_memory_usage_data_units, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) (original) + O(N) (chei)"}

# == SCENARIUL 2: GENERAREA RAPORTULUI DE VÂNZĂRI ==
def model_standard_sales_report(num_transactions, avg_items_per_transaction, avg_record_size_transaction_header, avg_record_size_item, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Raport Vânzări Standard (Multi-Pass)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M + N)"}
    if num_transactions <= 0 or avg_items_per_transaction <=0 or avg_record_size_transaction_header <=0 or avg_record_size_item <=0: return default_return
    N = float(num_transactions); M = float(avg_items_per_transaction)
    cpu_ops_item_processing = N * M * 3.0 * COST_PER_ARITHMETIC_OP_CPU; cpu_ops_storing_intermediate = N * 2.0 * COST_PER_MEMORY_ACCESS_CPU; cpu_ops_final_aggregation = N * 2.0 * COST_PER_ARITHMETIC_OP_CPU
    total_cpu_operations = cpu_ops_item_processing + cpu_ops_storing_intermediate + cpu_ops_final_aggregation
    memory_all_transactions_headers = N * avg_record_size_transaction_header; memory_all_items_data = N * M * avg_record_size_item; memory_intermediate_lists = N * 2.0
    total_memory_usage = memory_all_transactions_headers + memory_all_items_data + memory_intermediate_lists
    data_movement = (memory_all_transactions_headers + memory_all_items_data) * 1.5 + (memory_intermediate_lists * 2.0)
    kwh, co2 = calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Raport Vânzări Standard (Multi-Pass)", "cpu_operations": total_cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": total_memory_usage, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M + N)"}

def model_green_sales_report(num_transactions, avg_items_per_transaction, avg_record_size_transaction_header, avg_record_size_item, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Raport Vânzări Verde (Single-Pass)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M) sau O(M) pt streaming"}
    if num_transactions <= 0 or avg_items_per_transaction <=0 or avg_record_size_transaction_header <=0 or avg_record_size_item <=0: return default_return
    N = float(num_transactions); M = float(avg_items_per_transaction)
    total_cpu_operations = N * M * 3.0 * COST_PER_ARITHMETIC_OP_CPU
    memory_all_transactions_headers = N * avg_record_size_transaction_header; memory_all_items_data = N * M * avg_record_size_item; memory_aggregates = 2.0 * 1.0
    total_memory_usage = memory_all_transactions_headers + memory_all_items_data + memory_aggregates
    data_movement = memory_all_transactions_headers + memory_all_items_data
    kwh, co2 = calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Raport Vânzări Verde (Single-Pass)", "cpu_operations": total_cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": total_memory_usage, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M) (date) / O(M) (streaming real)"}

# == SCENARIUL 3: FILTRAREA ȘI ANALIZA LOG-URILOR ==
def model_standard_log_filter(num_log_lines, avg_line_length, error_line_percentage, avg_error_message_size, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Filtrare Log Standard (Full Load, Regex All)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(L * C_regex)", "complexity_memory": "O(L)"}
    if num_log_lines <= 0 or avg_line_length <=0 or error_line_percentage <=0 or avg_error_message_size <=0: return default_return
    L = float(num_log_lines); num_error_lines = L * (error_line_percentage / 100.0)
    cpu_operations = L * COST_PER_REGEX_MATCH_CPU
    memory_all_lines = L * avg_line_length; memory_extracted_errors = num_error_lines * avg_error_message_size
    total_memory_usage = memory_all_lines + memory_extracted_errors
    data_movement = (L * avg_line_length) + (num_error_lines * avg_error_message_size)
    kwh, co2 = calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Filtrare Log Standard (Full Load, Regex All)", "cpu_operations": cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": total_memory_usage, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(L * C_regex)", "complexity_memory": "O(L + E*S_msg)"}

def model_green_log_filter(num_log_lines, avg_line_length, error_line_percentage, avg_error_message_size, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Filtrare Log Verde (Stream, Target Regex)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(L + E*C_regex)", "complexity_memory": "O(linie + E*S_msg)"}
    if num_log_lines <= 0 or avg_line_length <=0 or error_line_percentage <=0 or avg_error_message_size <=0: return default_return
    L = float(num_log_lines); num_error_lines = L * (error_line_percentage / 100.0)
    cpu_ops_string_checks = L * COST_PER_STRING_CHECK_CPU; cpu_ops_regex_on_errors = num_error_lines * COST_PER_REGEX_MATCH_CPU
    total_cpu_operations = cpu_ops_string_checks + cpu_ops_regex_on_errors
    memory_one_line = float(avg_line_length * 1.5); memory_extracted_errors = num_error_lines * avg_error_message_size
    total_memory_usage = memory_one_line + memory_extracted_errors
    data_movement = L * avg_line_length
    kwh, co2 = calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {"name": "Filtrare Log Verde (Stream, Target Regex)", "cpu_operations": total_cpu_operations, "data_movement_units": data_movement, "memory_usage_data_units": total_memory_usage, "estimated_kwh": kwh, "estimated_co2_g": co2, "complexity_cpu": "O(L + E*C_regex)", "complexity_memory": "O(linie + E*S_msg)"}


# --- Începutul Interfeței Utilizator Streamlit ---
st.set_page_config(layout="wide", page_title="Simulator Impact Software Verde")
st.title("🌍 Simulator de Impact al Practicilor Software Verzi")
st.markdown("O unealtă interactivă pentru a estima și compara impactul asupra resurselor, consumul energetic și emisiile de CO2 asociate diferitelor abordări de procesare a datelor.")

SCENARIU_SORTARE = "Scenariul 1: Sortarea Datelor Clienților"
SCENARIU_RAPORT_VANZARI = "Scenariul 2: Generarea Raportului de Vânzări"
SCENARIU_FILTRARE_LOGURI = "Scenariul 3: Filtrarea și Analiza Log-urilor"
scenario_options = [SCENARIU_SORTARE, SCENARIU_RAPORT_VANZARI, SCENARIU_FILTRARE_LOGURI]

ZONE_MEDIA_UE = "Media UE (Implicit)"
ZONE_ROMANIA_API = "România (Live API)"
co2_zone_options = [ZONE_MEDIA_UE, ZONE_ROMANIA_API]

st.sidebar.header("⚙️ Configurare Simulare")
selected_scenario = st.sidebar.selectbox("Alegeți scenariul de simulat:", scenario_options, index=0)

selected_hardware_profile_name = st.sidebar.selectbox(
    "Alegeți profilul hardware:", options=list(HARDWARE_PROFILES.keys()),
    index=list(HARDWARE_PROFILES.keys()).index(DEFAULT_HARDWARE_PROFILE_NAME),
    help="Profilul hardware influențează factorii de conversie la energie."
)
current_hardware_factors = HARDWARE_PROFILES[selected_hardware_profile_name]
kwh_cpu_factor_selected = current_hardware_factors["kwh_per_cpu_op"]
kwh_data_factor_selected = current_hardware_factors["kwh_per_data_move"]
st.sidebar.caption(f"Profil Hardware: **{selected_hardware_profile_name}**")
st.sidebar.caption(f"{current_hardware_factors['description']}")
st.sidebar.caption(f"kWh/Op CPU: {kwh_cpu_factor_selected:.2e}, kWh/Mișc.Date: {kwh_data_factor_selected:.2e}")

selected_co2_source = st.sidebar.selectbox("Sursa pentru Intensitatea Carbonică (gCO2eq/kWh):", co2_zone_options, index=0)
gco2_per_kwh_final = GCO2EQ_PER_KWH_DEFAULT
if selected_co2_source == ZONE_ROMANIA_API:
    if EM_API_KEY:
        romania_intensity = get_romania_carbon_intensity(EM_API_KEY)
        if romania_intensity is not None: gco2_per_kwh_final = romania_intensity
    else:
        if 'api_key_warning_main_shown' not in st.session_state:
            st.sidebar.warning(f"Cheia API (EM_API_KEY) lipsește. Se folosește valoarea implicită pentru '{ZONE_ROMANIA_API}'.")
            st.session_state.api_key_warning_main_shown = True
st.sidebar.caption(f"Factor CO2 utilizat: {gco2_per_kwh_final:.2f} gCO2eq/kWh.")

default_values = {
    's1_N': 1000, 's1_avg_rec_size': 100, 's1_key_idx_size': 5,
    's2_N_trans': 10000, 's2_avg_items': 3, 's2_trans_header_size': 20, 's2_item_size': 10,
    's3_N_lines': 100000, 's3_avg_line_len': 150, 's3_err_perc': 5, 's3_err_msg_size': 50
}
for key, value in default_values.items():
    if key not in st.session_state: st.session_state[key] = value

if selected_scenario == SCENARIU_SORTARE:
    st.header(SCENARIU_SORTARE); st.markdown("Acest scenariu compară trei metode de sortare...")
    st.session_state.s1_N = st.sidebar.number_input("Nr. înregistrări (N):", 1, 1000000, st.session_state.s1_N, 100, key="s1_N_widget")
    st.session_state.s1_avg_rec_size = st.sidebar.number_input("Dim. înregistrare (u):", 1, 10000, st.session_state.s1_avg_rec_size, 10, key="s1_avg_rec_size_widget")
    st.session_state.s1_key_idx_size = st.sidebar.number_input("Dim. cheie-index (u):", 1, 1000, st.session_state.s1_key_idx_size, 1, key="s1_key_idx_size_widget")
elif selected_scenario == SCENARIU_RAPORT_VANZARI:
    st.header(SCENARIU_RAPORT_VANZARI); st.markdown("Acest scenariu compară metode de generare a rapoartelor...")
    st.session_state.s2_N_trans = st.sidebar.number_input("Nr. tranzacții (N):", 1, 1000000, st.session_state.s2_N_trans, 100, key="s2_N_trans_widget")
    st.session_state.s2_avg_items = st.sidebar.number_input("Nr. mediu itemi/tranz. (M):", 1, 1000, st.session_state.s2_avg_items, 1, key="s2_avg_items_widget")
    st.session_state.s2_trans_header_size = st.sidebar.number_input("Dim. header tranz. (u):", 1, 1000, st.session_state.s2_trans_header_size, 1, key="s2_trans_header_size_widget")
    st.session_state.s2_item_size = st.sidebar.number_input("Dim. item tranz. (u):", 1, 1000, st.session_state.s2_item_size, 1, key="s2_item_size_widget")
elif selected_scenario == SCENARIU_FILTRARE_LOGURI:
    st.header(SCENARIU_FILTRARE_LOGURI); st.markdown("Acest scenariu analizează strategii de filtrare a log-urilor...")
    st.session_state.s3_N_lines = st.sidebar.number_input("Nr. linii log (L):", 100, 5000000, st.session_state.s3_N_lines, 1000, key="s3_N_lines_widget")
    st.session_state.s3_avg_line_len = st.sidebar.number_input("Lung. medie linie (u):", 10, 1000, st.session_state.s3_avg_line_len, 10, key="s3_avg_line_len_widget")
    st.session_state.s3_err_perc = st.sidebar.slider("Procentaj linii eroare (%):", 1, 100, st.session_state.s3_err_perc, 1, key="s3_err_perc_widget")
    st.session_state.s3_err_msg_size = st.sidebar.number_input("Dim. medie mesaj eroare (u):", 1, 1000, st.session_state.s3_err_msg_size, 5, key="s3_err_msg_size_widget")

run_button = st.sidebar.button("🚀 Rulează Simulare", help="Apasă pentru a calcula și afișa rezultatele")

if 'simulation_has_run' not in st.session_state: st.session_state.simulation_has_run = False
if run_button: st.session_state.simulation_has_run = True

if st.session_state.simulation_has_run:
    all_results = []; current_N_display = ""; valid_inputs = False
    kwh_cpu = kwh_cpu_factor_selected
    kwh_data = kwh_data_factor_selected

    if selected_scenario == SCENARIU_SORTARE:
        s1_N, s1_avg_rec_size, s1_key_idx_size = st.session_state.s1_N, st.session_state.s1_avg_rec_size, st.session_state.s1_key_idx_size
        if s1_N > 0 and s1_avg_rec_size > 0 and s1_key_idx_size > 0:
            all_results = [model_standard_sort(s1_N, s1_avg_rec_size, kwh_cpu, kwh_data, gco2_per_kwh_final),
                           model_efficient_sort(s1_N, s1_avg_rec_size, kwh_cpu, kwh_data, gco2_per_kwh_final),
                           model_sort_index(s1_N, s1_avg_rec_size, s1_key_idx_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
            current_N_display = f"N = {s1_N:,.0f} înregistrări"; valid_inputs = True
        else: st.error(f"EROARE: Parametrii pentru '{SCENARIU_SORTARE}' trebuie să fie mai mari ca zero.")
    elif selected_scenario == SCENARIU_RAPORT_VANZARI:
        s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size = st.session_state.s2_N_trans, st.session_state.s2_avg_items, st.session_state.s2_trans_header_size, st.session_state.s2_item_size
        if s2_N_trans > 0 and s2_avg_items > 0 and s2_trans_header_size > 0 and s2_item_size > 0:
            all_results = [model_standard_sales_report(s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size, kwh_cpu, kwh_data, gco2_per_kwh_final),
                           model_green_sales_report(s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
            current_N_display = f"N = {s2_N_trans:,.0f} tranz., M = {s2_avg_items} itemi/tr."; valid_inputs = True
        else: st.error(f"EROARE: Parametrii pentru '{SCENARIU_RAPORT_VANZARI}' trebuie să fie mai mari ca zero.")
    elif selected_scenario == SCENARIU_FILTRARE_LOGURI:
        s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size = st.session_state.s3_N_lines, st.session_state.s3_avg_line_len, st.session_state.s3_err_perc, st.session_state.s3_err_msg_size
        if s3_N_lines > 0 and s3_avg_line_len > 0 and s3_err_perc > 0 and s3_err_msg_size > 0:
            all_results = [model_standard_log_filter(s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size, kwh_cpu, kwh_data, gco2_per_kwh_final),
                           model_green_log_filter(s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
            current_N_display = f"L = {s3_N_lines:,.0f} linii, {s3_err_perc}% erori"; valid_inputs = True
        else: st.error(f"EROARE: Parametrii pentru '{SCENARIU_FILTRARE_LOGURI}' trebuie să fie mai mari ca zero.")

 
  # --- Afișarea Rezultatelor ---
    if valid_inputs and all_results:
        st.header(f"📊 Rezultate pentru {selected_scenario.split(':')[1].strip()} ({current_N_display})")
        st.markdown(f"Profil Hardware Selectat: **{selected_hardware_profile_name}**")
        st.markdown("---")

        tab_rezumat, tab_grafice_costuri, tab_grafice_impact = st.tabs(["📝 Rezumat & Reduceri", "📈 Grafice Costuri Abstracte (Plotly)", "🌍 Grafice Impact Ambiental (Plotly)"])

        with tab_rezumat:
            # ... (codul pentru afișarea metricilor textuale și tabelul de reduceri rămâne la fel) ...
            st.subheader("Estimări Costuri & Impact Ambiental (Valori Absolute)")
            standard_model_results = all_results[0] if all_results else None
            reduction_data = []

            for i, result in enumerate(all_results):
                st.markdown(f"#### Model: {result.get('name', 'N/A')}")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1: st.metric("💻 Op. CPU", f"{result.get('cpu_operations', 0.0):,.0f}", delta_color="off")
                with col2: st.metric("💾 Mișc. Date", f"{result.get('data_movement_units', 0.0):,.0f}", delta_color="off")
                with col3:
                    mem_usage = result.get('peak_memory_usage_data_units', result.get('memory_usage_data_units', 0.0))
                    st.metric("🧠 Memorie", f"{mem_usage:,.0f}", delta_color="off")
                    if 'aux_memory_units (stack)' in result: st.caption(f"Aux: {result.get('aux_memory_units (stack)', 0.0):,.2f}")
                with col4: st.metric("⚡ Energie (kWh)", f"{result.get('estimated_kwh', 0.0):.6f}", delta_color="off")
                with col5: st.metric("💨 CO2 (g)", f"{result.get('estimated_co2_g', 0.0):,.2f}", delta_color="off")
                st.caption(f"Complexitate CPU: {result.get('complexity_cpu', 'N/A')} | Complexitate Memorie: {result.get('complexity_memory', 'N/A')}")

                if i > 0 and standard_model_results:
                    row_reduction = {"Model Verde": result.get('name', 'N/A')}
                    for metric_key, metric_name_ro_short in [
                        ("cpu_operations", "CPU"), ("data_movement_units", "Mișc.Date"),
                        ("memory_usage_data_units", "Memorie"),
                        ("estimated_kwh", "Energie"), ("estimated_co2_g", "CO2")]:
                        current_val = result.get(metric_key, 0.0)
                        standard_val_key_to_use = metric_key
                        if metric_key == "memory_usage_data_units":
                            current_val = result.get('peak_memory_usage_data_units', result.get('memory_usage_data_units', 0.0))
                            standard_val_key_to_use = 'peak_memory_usage_data_units' if 'peak_memory_usage_data_units' in standard_model_results else 'memory_usage_data_units'
                        standard_val = standard_model_results.get(standard_val_key_to_use, 0.0)
                        if standard_val > 0.00000001:
                            reduction_percent = ((standard_val - current_val) / standard_val) * 100
                            row_reduction[f"Reducere {metric_name_ro_short} (%)"] = f"{reduction_percent:.1f}%"
                        else: row_reduction[f"Reducere {metric_name_ro_short} (%)"] = "N/A" if standard_val == 0 else "∞"
                    reduction_data.append(row_reduction)
                st.markdown("---")
            if reduction_data:
                st.subheader("📊 Tabel Reduceri Procentuale vs. Modelul Standard")
                df_reductions = pd.DataFrame(reduction_data)
                st.dataframe(df_reductions.set_index("Model Verde")) # Setăm indexul pentru o afișare mai bună
                st.markdown("---")


        with tab_grafice_costuri:
            st.subheader("Grafice Comparative: Costuri Abstracte (Interactive)")
            if all_results: # Asigură-te că avem date
                # Pregătim datele pentru Plotly (Pandas DataFrame este ideal)
                plot_data_abstract = []
                for res in all_results:
                    plot_data_abstract.append({
                        "Model": res.get('name', 'N/A'),
                        "Operații CPU": res.get('cpu_operations', 0.0),
                        "Mișcare Date (unități)": res.get('data_movement_units', 0.0),
                        "Memorie Utilizată (unități)": res.get('peak_memory_usage_data_units', res.get('memory_usage_data_units', 0.0))
                    })
                df_abstract = pd.DataFrame(plot_data_abstract)

                if not df_abstract.empty:
                    fig_cpu_plotly = px.bar(df_abstract, x="Model", y="Operații CPU",
                                            color="Model", title="Comparare Operații CPU Estimate",
                                            labels={"Operații CPU": "Op. CPU Estimate"},
                                            text_auto=True) # Adaugă valorile pe bare
                    fig_cpu_plotly.update_layout(xaxis_tickangle=-30, title_x=0.5)
                    fig_cpu_plotly.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig_cpu_plotly, use_container_width=True)

                    fig_data_plotly = px.bar(df_abstract, x="Model", y="Mișcare Date (unități)",
                                             color="Model", title="Comparare Mișcare Date Estimate",
                                             labels={"Mișcare Date (unități)": "Mișc. Date Estimate (unități)"},
                                             text_auto=True)
                    fig_data_plotly.update_layout(xaxis_tickangle=-30, title_x=0.5)
                    fig_data_plotly.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig_data_plotly, use_container_width=True)

                    fig_mem_plotly = px.bar(df_abstract, x="Model", y="Memorie Utilizată (unități)",
                                            color="Model", title="Comparare Memorie Utilizată Estimată",
                                            labels={"Memorie Utilizată (unități)": "Memorie Estimate (unități)"},
                                            text_auto=True)
                    fig_mem_plotly.update_layout(xaxis_tickangle=-30, title_x=0.5)
                    fig_mem_plotly.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig_mem_plotly, use_container_width=True)
                else:
                    st.warning("Nu sunt date disponibile pentru graficele de costuri abstracte.")
            else:
                st.warning("Nu s-au putut genera graficele de costuri abstracte (lipsesc rezultatele).")


        with tab_grafice_impact:
            st.subheader("Grafice Comparative: Impact Energetic și CO2 (Interactive)")
            if all_results:
                plot_data_impact = []
                for res in all_results:
                    plot_data_impact.append({
                        "Model": res.get('name', 'N/A'),
                        "Energie (kWh)": res.get('estimated_kwh', 0.0),
                        "Emisii CO2 (g)": res.get('estimated_co2_g', 0.0)
                    })
                df_impact = pd.DataFrame(plot_data_impact)

                if not df_impact.empty:
                    fig_kwh_plotly = px.bar(df_impact, x="Model", y="Energie (kWh)",
                                            color="Model", title="Comparare Energie Consumată Estimată",
                                            labels={"Energie (kWh)": "Energie Estimată (kWh)"},
                                            text_auto=True)
                    fig_kwh_plotly.update_layout(xaxis_tickangle=-30, title_x=0.5)
                    fig_kwh_plotly.update_traces(texttemplate='%{y:.6f}', textposition='outside') # Format pentru kWh
                    st.plotly_chart(fig_kwh_plotly, use_container_width=True)

                    fig_co2_plotly = px.bar(df_impact, x="Model", y="Emisii CO2 (g)",
                                            color="Model", title="Comparare Emisii CO2 Estimate",
                                            labels={"Emisii CO2 (g)": "Emisii CO2 Estimate (g)"},
                                            text_auto=True)
                    fig_co2_plotly.update_layout(xaxis_tickangle=-30, title_x=0.5)
                    fig_co2_plotly.update_traces(texttemplate='%{y:,.2f}', textposition='outside') # Format pentru CO2
                    st.plotly_chart(fig_co2_plotly, use_container_width=True)
                else:
                    st.warning("Nu sunt date disponibile pentru graficele de impact ambiental.")
            else:
                st.warning("Nu s-au putut genera graficele de impact ambiental (lipsesc rezultatele).")

        st.markdown("---")
        st.info("""
        **Notă:** Estimările de energie și CO2 sunt **ILUSTRATIVE** și se bazează pe factori de conversie aproximativi și pe profilul hardware selectat.
        Performanța reală și consumul energetic pot varia considerabil.
        Scopul principal este de a demonstra diferențele *relative* de impact între diverse abordări.
        """)
    elif st.session_state.simulation_has_run and not valid_inputs:
        st.warning("Simularea nu a putut fi rulată din cauza parametrilor de intrare invalizi pentru scenariul selectat.")
elif not st.session_state.simulation_has_run :
    st.info("⬅️ Alegeți un scenariu, ajustați parametrii din bara laterală și apăsați 'Rulează Simulare' pentru a vedea rezultatele.")

# Comentarii despre cum se rulează aplicația (le poți păstra la sfârșit pentru referință)
# Pentru a rula această aplicație:
# 1. Salvați codul ca app_streamlit.py (sau orice nume .py)
# 2. Deschideți un terminal în directorul proiectului.
# 3. Activați mediul virtual (de ex., pe macOS/Linux: source venv/bin/activate; pe Windows: venv\Scripts\activate).
# 4. Rulați comanda: streamlit run app_streamlit.py 




#################################################################################################################