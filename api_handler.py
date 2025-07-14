# api_handler.py

import math
# --- Corecție Importuri ---
import utils  # Am înlocuit 'from . import utils'
import config # Am înlocuit 'from . import config'
# --- Sfârșit Corecție Importuri ---

# == SCENARIUL 1: SORTAREA DATELOR ==
def model_standard_sort(N, average_record_size_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare Standard (tip BubbleSort)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N^2)", "complexity_memory": "O(N)"}
    if N <= 0 or average_record_size_data_units <=0: return default_return
    comparisons = float(N * (N - 1) / 2)
    swaps = float(N * (N - 1) / 4) # Estimare pentru BubbleSort mediu
    cpu_operations = (comparisons * config.COST_PER_COMPARISON_CPU) + \
                     (swaps * config.COST_PER_SWAP_FULL_RECORD_CPU)
    data_movement = swaps * average_record_size_data_units * 2.0 # Fiecare swap mută 2 înregistrări
    memory_usage_data_units = float(N * average_record_size_data_units) # Stocarea listei
    kwh, co2 = utils.calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Sortare Standard (tip BubbleSort)",
        "cpu_operations": cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": memory_usage_data_units,
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(N^2)",
        "complexity_memory": "O(N)"
    }

def model_efficient_sort(N, average_record_size_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare Eficientă (tip Quicksort)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "aux_memory_units (stack)": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) + O(log N) aux"}
    if N <= 0 or average_record_size_data_units <=0: return default_return
    aux_memory_logN = 0.0
    comparisons, swaps = 0.0, 0.0
    if N == 1: # Cazul de bază pentru logN
        comparisons, swaps = 1.0, 0.0 # O comparație, zero swap-uri
    elif N > 1:
        comparisons = float(N * math.log2(N))
        swaps = float(N * math.log2(N) / 2.0) # O estimare, poate varia
        aux_memory_logN = float(math.log2(N) * 1.0) # Estimare spațiu stivă pentru recursivitate (unități abstracte)
    cpu_operations = (comparisons * config.COST_PER_COMPARISON_CPU) + \
                     (swaps * config.COST_PER_SWAP_FULL_RECORD_CPU) # Quicksort face swap-uri pe înregistrări complete
    data_movement = swaps * average_record_size_data_units * 2.0
    memory_usage_data_units = float(N * average_record_size_data_units) # Stocarea listei
    kwh, co2 = utils.calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Sortare Eficientă (tip Quicksort)",
        "cpu_operations": cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": memory_usage_data_units,
        "aux_memory_units (stack)": aux_memory_logN,
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(N log N)",
        "complexity_memory": "O(N) + O(log N) aux"
    }

def model_sort_index(N, average_record_size_data_units, size_of_key_index_pair_data_units, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Sortare-Index (Sortare Eficientă Chei)", "cpu_operations": 0.0, "data_movement_units": 0.0, "peak_memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N log N)", "complexity_memory": "O(N) (original) + O(N) (chei)"}
    if N <= 0 or average_record_size_data_units <=0 or size_of_key_index_pair_data_units <=0: return default_return

    # 1. Creare listă de perechi (cheie, index original)
    cpu_ops_creation = float(N * 1.0) # Estimare: o operație per element pentru a extrage cheia și a stoca indexul
    memory_for_key_index_list = float(N * size_of_key_index_pair_data_units)

    # 2. Sortare listă de perechi (cheie, index) folosind un algoritm eficient (N log N)
    key_comparisons, key_swaps = 0.0, 0.0
    if N == 1:
        key_comparisons, key_swaps = 1.0, 0.0
    elif N > 1 :
        key_comparisons = float(N * math.log2(N))
        key_swaps = float(N * math.log2(N) / 2.0) # Swap-uri pe perechi cheie-index

    cpu_ops_sorting_keys = (key_comparisons * config.COST_PER_COMPARISON_CPU) + \
                           (key_swaps * config.COST_PER_SWAP_KEY_INDEX_CPU) # Cost mai mic pentru swap chei+index
    data_movement_sorting_keys = key_swaps * size_of_key_index_pair_data_units * 2.0

    # 3. (Opțional, dacă se dorește reordonarea listei originale pe loc sau într-o nouă listă)
    # Aici modelăm costul creării unei noi liste sortate pe baza indexului sortat.
    # Dacă s-ar face pe loc, ar fi mai complex de modelat (cicluri de permutare).
    # Presupunem o citire a listei originale și o scriere în noua listă.
    cpu_ops_reordering = float(N * 2.0) # O citire, o scriere per element (acces memorie)
    data_movement_reordering = float(N * average_record_size_data_units) # Mutarea întregii înregistrări o dată

    total_cpu_operations = cpu_ops_creation + cpu_ops_sorting_keys + cpu_ops_reordering
    total_data_movement = data_movement_sorting_keys + data_movement_reordering
    # Memoria de vârf include lista originală și lista de chei-index
    peak_memory_usage_data_units = (N * average_record_size_data_units) + memory_for_key_index_list

    kwh, co2 = utils.calculate_energy_co2(total_cpu_operations, total_data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Sortare-Index (Sortare Eficientă Chei)",
        "cpu_operations": total_cpu_operations,
        "data_movement_units": total_data_movement,
        "peak_memory_usage_data_units": peak_memory_usage_data_units,
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(N log N)", # Dominat de sortarea cheilor
        "complexity_memory": "O(N) (original) + O(N) (chei)"
    }

# == SCENARIUL 2: GENERAREA RAPORTULUI DE VÂNZĂRI ==
def model_standard_sales_report(num_transactions, avg_items_per_transaction, avg_record_size_transaction_header, avg_record_size_item, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Raport Vânzări Standard (Multi-Pass)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M + N)"}
    if num_transactions <= 0 or avg_items_per_transaction <=0 or avg_record_size_transaction_header <=0 or avg_record_size_item <=0: return default_return

    N = float(num_transactions) # Nr. tranzacții
    M = float(avg_items_per_transaction) # Nr. mediu itemi/tranzacție

    # Pass 1: Procesare itemi și stocare sume intermediare per tranzacție
    cpu_ops_item_processing = N * M * 3.0 * config.COST_PER_ARITHMETIC_OP_CPU # Ex: citire preț, cantitate, calcul total item
    cpu_ops_storing_intermediate = N * 2.0 * config.COST_PER_MEMORY_ACCESS_CPU # Stocare sumă/contor per tranzacție

    # Pass 2: Agregare finală a sumelor intermediare
    cpu_ops_final_aggregation = N * 2.0 * config.COST_PER_ARITHMETIC_OP_CPU # Adunare sume tranzacții

    total_cpu_operations = cpu_ops_item_processing + cpu_ops_storing_intermediate + cpu_ops_final_aggregation

    # Memorie: stocare toate datele tranzacțiilor și itemilor, plus liste intermediare
    memory_all_transactions_headers = N * avg_record_size_transaction_header
    memory_all_items_data = N * M * avg_record_size_item
    memory_intermediate_lists = N * 2.0 # Ex: o listă de sume per tranzacție (float) și poate una de ID-uri

    total_memory_usage = memory_all_transactions_headers + memory_all_items_data + memory_intermediate_lists

    # Mișcare date: citire toate datele, scriere/citire liste intermediare
    # Factorul de 1.5 pentru citirea datelor inițiale poate fi o simplificare
    data_movement = (memory_all_transactions_headers + memory_all_items_data) * 1.5 + \
                    (memory_intermediate_lists * 2.0) # Citire și scriere liste intermediare

    kwh, co2 = utils.calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Raport Vânzări Standard (Multi-Pass)",
        "cpu_operations": total_cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": total_memory_usage,
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(N*M)", # Procesare fiecare item
        "complexity_memory": "O(N*M + N)" # Stocare toate datele + intermediare
    }

def model_green_sales_report(num_transactions, avg_items_per_transaction, avg_record_size_transaction_header, avg_record_size_item, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Raport Vânzări Verde (Single-Pass)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(N*M)", "complexity_memory": "O(N*M) sau O(M) pt streaming"}
    if num_transactions <= 0 or avg_items_per_transaction <=0 or avg_record_size_transaction_header <=0 or avg_record_size_item <=0: return default_return

    N = float(num_transactions)
    M = float(avg_items_per_transaction)

    # Single-Pass: Procesare itemi și agregare directă
    total_cpu_operations = N * M * 3.0 * config.COST_PER_ARITHMETIC_OP_CPU # Similar cu standard, dar fără stocare intermediară extinsă

    # Memorie:
    # Dacă datele sunt încărcate complet:
    memory_all_transactions_headers = N * avg_record_size_transaction_header
    memory_all_items_data = N * M * avg_record_size_item
    # Dacă se face streaming real, memoria pentru datele brute ar fi mult mai mică (ex: O(M) pentru itemii unei tranzacții)
    # Aici modelăm cazul în care datele sunt disponibile, dar procesate eficient.
    memory_aggregates = 2.0 * 1.0 # Ex: total vânzări, total itemi (câteva variabile)

    total_memory_usage = memory_all_transactions_headers + memory_all_items_data + memory_aggregates
    # Pentru un streaming "adevărat", total_memory_usage ar fi mai aproape de (M * avg_record_size_item) + memory_aggregates la un moment dat.
    # Modelul actual presupune că datele sunt în memorie, dar algoritmul este single-pass.

    # Mișcare date: citire toate datele o singură dată
    data_movement = memory_all_transactions_headers + memory_all_items_data

    kwh, co2 = utils.calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Raport Vânzări Verde (Single-Pass)",
        "cpu_operations": total_cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": total_memory_usage, # Reflectă datele încărcate; pentru streaming real ar fi mai mic
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(N*M)",
        "complexity_memory": "O(N*M) (date) / O(M) (streaming real)" # Clarificare
    }

# == SCENARIUL 3: FILTRAREA ȘI ANALIZA LOG-URILOR ==
def model_standard_log_filter(num_log_lines, avg_line_length, error_line_percentage, avg_error_message_size, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Filtrare Log Standard (Full Load, Regex All)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(L * C_regex)", "complexity_memory": "O(L)"}
    if num_log_lines <= 0 or avg_line_length <=0 or error_line_percentage <=0 or avg_error_message_size <=0: return default_return

    L = float(num_log_lines) # Nr. linii log
    num_error_lines = L * (error_line_percentage / 100.0)

    # CPU: Aplicare regex pe fiecare linie
    cpu_operations = L * config.COST_PER_REGEX_MATCH_CPU

    # Memorie: Stocare toate liniile + mesajele de eroare extrase
    memory_all_lines = L * avg_line_length
    memory_extracted_errors = num_error_lines * avg_error_message_size # Presupunem că extragem mesajul
    total_memory_usage = memory_all_lines + memory_extracted_errors

    # Mișcare date: Citire toate liniile, scriere/stocare mesaje de eroare
    data_movement = (L * avg_line_length) + (num_error_lines * avg_error_message_size) # Citire linii + stocare erori

    kwh, co2 = utils.calculate_energy_co2(cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Filtrare Log Standard (Full Load, Regex All)",
        "cpu_operations": cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": total_memory_usage,
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(L * C_regex)", # L linii * Cost Regex
        "complexity_memory": "O(L + E*S_msg)" # Linii + Erori * Dimensiune Mesaj
    }

def model_green_log_filter(num_log_lines, avg_line_length, error_line_percentage, avg_error_message_size, kwh_cpu, kwh_data, gco2_factor):
    default_return = {"name": "Filtrare Log Verde (Stream, Target Regex)", "cpu_operations": 0.0, "data_movement_units": 0.0, "memory_usage_data_units": 0.0, "estimated_kwh": 0.0, "estimated_co2_g": 0.0, "complexity_cpu": "O(L + E*C_regex)", "complexity_memory": "O(linie + E*S_msg)"}
    if num_log_lines <= 0 or avg_line_length <=0 or error_line_percentage <=0 or avg_error_message_size <=0: return default_return

    L = float(num_log_lines)
    num_error_lines = L * (error_line_percentage / 100.0)

    # CPU: Verificare string simplă pe fiecare linie, apoi regex doar pe liniile candidate
    cpu_ops_string_checks = L * config.COST_PER_STRING_CHECK_CPU # Ex: `if "ERROR" in line:`
    cpu_ops_regex_on_errors = num_error_lines * config.COST_PER_REGEX_MATCH_CPU # Regex doar pe liniile care probabil sunt erori
    total_cpu_operations = cpu_ops_string_checks + cpu_ops_regex_on_errors

    # Memorie: Stocare o singură linie la un moment dat (streaming) + mesajele de eroare extrase
    # Factorul de 1.5 pentru buffer-ul liniei curente este o estimare
    memory_one_line_buffer = float(avg_line_length * 1.5)
    memory_extracted_errors = num_error_lines * avg_error_message_size
    total_memory_usage = memory_one_line_buffer + memory_extracted_errors # Memorie peak

    # Mișcare date: Citire toate liniile (chiar și în stream, datele trec prin sistem)
    # Nu stocăm toate liniile simultan, dar le citim pe toate.
    data_movement = L * avg_line_length # Datele sunt citite de pe disc/rețea

    kwh, co2 = utils.calculate_energy_co2(total_cpu_operations, data_movement, kwh_cpu, kwh_data, gco2_factor)
    return {
        "name": "Filtrare Log Verde (Stream, Target Regex)",
        "cpu_operations": total_cpu_operations,
        "data_movement_units": data_movement,
        "memory_usage_data_units": total_memory_usage, # Reflectă memoria de vârf, nu totalul datelor stocate pe termen lung
        "estimated_kwh": kwh,
        "estimated_co2_g": co2,
        "complexity_cpu": "O(L + E*C_regex)", # L verificări string + Erori * Cost Regex
        "complexity_memory": "O(linie + E*S_msg)" # O linie în buffer + Erori * Dimensiune Mesaj
    }
