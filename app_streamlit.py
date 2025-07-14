# app_streamlit.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from datetime import datetime

# Import modulele create
import config
import api_client
import api_handler
import utils

# --- Începutul Interfeței Utilizator Streamlit ---
st.set_page_config(layout="wide", page_title=config.APP_TITLE)
st.title(config.APP_TITLE)
st.markdown(config.APP_SUBHEADER)

if 'history' not in st.session_state:
    st.session_state.history = []

# --- Configurare Sidebar ---
st.sidebar.header(config.SIDEBAR_HEADER)
selected_scenario = st.sidebar.selectbox("Alegeți scenariul de simulat:", options=config.SCENARIO_OPTIONS, index=0)
selected_hardware_profile_name = st.sidebar.selectbox("Alegeți profilul hardware:", options=list(config.HARDWARE_PROFILES.keys()), index=list(config.HARDWARE_PROFILES.keys()).index(config.DEFAULT_HARDWARE_PROFILE_NAME), help="Profilul hardware influențează factorii de conversie la energie.")
current_hardware_factors = config.HARDWARE_PROFILES[selected_hardware_profile_name]
kwh_cpu_factor_selected = current_hardware_factors["kwh_per_cpu_op"]
kwh_data_factor_selected = current_hardware_factors["kwh_per_data_move"]
st.sidebar.caption(f"Profil Hardware: **{selected_hardware_profile_name}**")
st.sidebar.caption(f"{current_hardware_factors['description']}")
st.sidebar.caption(f"kWh/Op CPU: {kwh_cpu_factor_selected:.2e}, kWh/Mișc.Date: {kwh_data_factor_selected:.2e}")

# --- Logică actualizată pentru sursa CO2 ---
selected_co2_source = st.sidebar.selectbox("Sursa pentru Intensitatea Carbonică (gCO2eq/kWh):", options=config.CO2_ZONE_OPTIONS, index=0)

# Inițializăm valorile
gco2_per_kwh_final = config.GCO2EQ_PER_KWH_DEFAULT
source_description = "Valoare medie estimată pentru Uniunea Europeană."

if selected_co2_source == config.ZONE_ROMANIA_API:
    # Cazul 1: Utilizatorul vrea date live pentru România
    EM_API_KEY_AVAILABLE = bool(os.getenv("EM_API_KEY"))
    if EM_API_KEY_AVAILABLE:
        romania_intensity = api_client.get_romania_carbon_intensity()
        if romania_intensity is not None:
            gco2_per_kwh_final = romania_intensity
            source_description = "Valoare live de la Electricity Maps API."
        else:
            source_description = "Apelul API a eșuat, se folosește valoarea implicită."
    else:
        if 'api_key_warning_main_shown' not in st.session_state:
            st.sidebar.warning(f"Cheia API (EM_API_KEY) lipsește. Se folosește valoarea implicită.")
            st.session_state.api_key_warning_main_shown = True
        source_description = "Cheie API lipsă, se folosește valoarea implicită."

elif selected_co2_source in config.HARDCODED_CO2_ZONES:
    # Cazul 2: Utilizatorul a selectat o țară hardcodată
    zone_data = config.HARDCODED_CO2_ZONES[selected_co2_source]
    gco2_per_kwh_final = zone_data['value']
    source_description = zone_data['description']

# Cazul 3 (else) este implicit: se folosesc valorile pentru Media UE deja setate la început.

st.sidebar.caption(f"Descriere Sursă: *{source_description}*")
st.sidebar.metric(label="Factor CO2 Utilizat", value=f"{gco2_per_kwh_final:.2f} gCO2eq/kWh")

# Stocarea valorilor default în session_state
for key, value in config.DEFAULT_INPUT_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Inputuri specifice scenariului ---
st.sidebar.markdown("---")
run_scalability_analysis = st.sidebar.checkbox("📈 Rulează Analiză de Scalabilitate", help="Bifează pentru a simula scenariul pe un interval de valori și a vizualiza cum scalează impactul.")
st.sidebar.markdown("---")
scaling_param_details = {
    config.SCENARIU_SORTARE: {"name": "Nr. înregistrări (N)", "key": "s1_N"},
    config.SCENARIU_RAPORT_VANZARI: {"name": "Nr. tranzacții (N)", "key": "s2_N_trans"},
    config.SCENARIU_FILTRARE_LOGURI: {"name": "Nr. linii log (L)", "key": "s3_N_lines"}
}
current_scaling_param = scaling_param_details[selected_scenario]
if run_scalability_analysis:
    st.sidebar.subheader("Parametri Scalabilitate")
    if 'scalability_start' not in st.session_state: st.session_state.scalability_start = 100
    if 'scalability_end' not in st.session_state: st.session_state.scalability_end = 10000
    if 'scalability_steps' not in st.session_state: st.session_state.scalability_steps = 10
    st.session_state.scalability_start = st.sidebar.number_input(f"Valoare Start ({current_scaling_param['name']}):", 1, 5000000, st.session_state.scalability_start)
    st.session_state.scalability_end = st.sidebar.number_input(f"Valoare Stop ({current_scaling_param['name']}):", st.session_state.scalability_start + 1, 5000000, st.session_state.scalability_end)
    st.session_state.scalability_steps = st.sidebar.number_input("Număr Pași:", 2, 100, st.session_state.scalability_steps)
    st.sidebar.info(f"Se vor rula {st.session_state.scalability_steps} simulări de la {st.session_state.scalability_start} la {st.session_state.scalability_end}.")
if selected_scenario == config.SCENARIU_SORTARE:
    if not run_scalability_analysis:
        st.header(config.SCENARIU_SORTARE)
        st.markdown("Acest scenariu compară trei metode de sortare a unui set de înregistrări de clienți.")
        st.session_state.s1_N = st.sidebar.number_input("Nr. înregistrări (N):", 1, 1000000, st.session_state.s1_N, 100, key="s1_N_widget")
    st.session_state.s1_avg_rec_size = st.sidebar.number_input("Dim. înregistrare (u):", 1, 10000, st.session_state.s1_avg_rec_size, 10, key="s1_avg_rec_size_widget")
    st.session_state.s1_key_idx_size = st.sidebar.number_input("Dim. cheie-index (u):", 1, 1000, st.session_state.s1_key_idx_size, 1, key="s1_key_idx_size_widget")
elif selected_scenario == config.SCENARIU_RAPORT_VANZARI:
    if not run_scalability_analysis:
        st.header(config.SCENARIU_RAPORT_VANZARI)
        st.markdown("Acest scenariu compară două abordări pentru generarea unui raport sumar de vânzări.")
        st.session_state.s2_N_trans = st.sidebar.number_input("Nr. tranzacții (N):", 1, 1000000, st.session_state.s2_N_trans, 100, key="s2_N_trans_widget")
    st.session_state.s2_avg_items = st.sidebar.number_input("Nr. mediu itemi/tranz. (M):", 1, 1000, st.session_state.s2_avg_items, 1, key="s2_avg_items_widget")
    st.session_state.s2_trans_header_size = st.sidebar.number_input("Dim. header tranz. (u):", 1, 1000, st.session_state.s2_trans_header_size, 1, key="s2_trans_header_size_widget")
    st.session_state.s2_item_size = st.sidebar.number_input("Dim. item tranz. (u):", 1, 1000, st.session_state.s2_item_size, 1, key="s2_item_size_widget")
elif selected_scenario == config.SCENARIU_FILTRARE_LOGURI:
    if not run_scalability_analysis:
        st.header(config.SCENARIU_FILTRARE_LOGURI)
        st.markdown("Acest scenariu analizează impactul diferitelor strategii de filtrare a log-urilor.")
        st.session_state.s3_N_lines = st.sidebar.number_input("Nr. linii log (L):", 100, 5000000, st.session_state.s3_N_lines, 1000, key="s3_N_lines_widget")
    st.session_state.s3_avg_line_len = st.sidebar.number_input("Lung. medie linie (u):", 10, 1000, st.session_state.s3_avg_line_len, 10, key="s3_avg_line_len_widget")
    st.session_state.s3_err_perc = st.sidebar.slider("Procentaj linii eroare (%):", 1, 100, st.session_state.s3_err_perc, 1, key="s3_err_perc_widget")
    st.session_state.s3_err_msg_size = st.sidebar.number_input("Dim. medie mesaj eroare (u):", 1, 1000, st.session_state.s3_err_msg_size, 5, key="s3_err_msg_size_widget")

run_button = st.sidebar.button(config.RUN_BUTTON_TEXT, help=config.RUN_BUTTON_TOOLTIP)
if 'simulation_has_run' not in st.session_state: st.session_state.simulation_has_run = False
if run_button: st.session_state.simulation_has_run = True

# --- Logică Simulare și Afișare Rezultate ---
if st.session_state.simulation_has_run:
    if run_scalability_analysis:
        st.header(f"📈 Analiză de Scalabilitate pentru {selected_scenario.split(':')[1].strip()}")
        st.info(f"Se simulează impactul pentru diferite dimensiuni ale setului de date (de la {st.session_state.scalability_start} la {st.session_state.scalability_end} pentru '{current_scaling_param['name']}').")

        scalability_results = []
        param_key_to_scale = current_scaling_param['key']
        scale_range = np.linspace(st.session_state.scalability_start, st.session_state.scalability_end, st.session_state.scalability_steps, dtype=int)

        with st.spinner("Se execută analiza de scalabilitate..."):
            for val in scale_range:
                params = {k: st.session_state[k] for k in config.DEFAULT_INPUT_VALUES.keys()}
                params[param_key_to_scale] = val
                
                models = []
                kwh_cpu, kwh_data = kwh_cpu_factor_selected, kwh_data_factor_selected
                
                if selected_scenario == config.SCENARIU_SORTARE:
                    models = [
                        api_handler.model_standard_sort(params['s1_N'], params['s1_avg_rec_size'], kwh_cpu, kwh_data, gco2_per_kwh_final),
                        api_handler.model_efficient_sort(params['s1_N'], params['s1_avg_rec_size'], kwh_cpu, kwh_data, gco2_per_kwh_final),
                        api_handler.model_sort_index(params['s1_N'], params['s1_avg_rec_size'], params['s1_key_idx_size'], kwh_cpu, kwh_data, gco2_per_kwh_final)
                    ]
                elif selected_scenario == config.SCENARIU_RAPORT_VANZARI:
                    models = [
                        api_handler.model_standard_sales_report(params['s2_N_trans'], params['s2_avg_items'], params['s2_trans_header_size'], params['s2_item_size'], kwh_cpu, kwh_data, gco2_per_kwh_final),
                        api_handler.model_green_sales_report(params['s2_N_trans'], params['s2_avg_items'], params['s2_trans_header_size'], params['s2_item_size'], kwh_cpu, kwh_data, gco2_per_kwh_final)
                    ]
                elif selected_scenario == config.SCENARIU_FILTRARE_LOGURI:
                    models = [
                        api_handler.model_standard_log_filter(params['s3_N_lines'], params['s3_avg_line_len'], params['s3_err_perc'], params['s3_err_msg_size'], kwh_cpu, kwh_data, gco2_per_kwh_final),
                        api_handler.model_green_log_filter(params['s3_N_lines'], params['s3_avg_line_len'], params['s3_err_perc'], params['s3_err_msg_size'], kwh_cpu, kwh_data, gco2_per_kwh_final)
                    ]

                for res in models:
                    res[current_scaling_param['name']] = val
                    scalability_results.append(res)
        
        if scalability_results:
            df_scaling = pd.DataFrame(scalability_results)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Scalabilitate CO2")
                fig_co2_scaling = px.line(df_scaling, x=current_scaling_param['name'], y="estimated_co2_g", color="name", title="Impactul CO2 în funcție de mărimea datelor", labels={"estimated_co2_g": "Emisii CO2 (g)", "name": "Model"}, markers=True)
                st.plotly_chart(fig_co2_scaling, use_container_width=True)
            with col2:
                st.subheader("Scalabilitate Operații CPU")
                fig_cpu_scaling = px.line(df_scaling, x=current_scaling_param['name'], y="cpu_operations", color="name", title="Operații CPU în funcție de mărimea datelor", labels={"cpu_operations": "Operații CPU (unități abstracte)", "name": "Model"}, markers=True)
                st.plotly_chart(fig_cpu_scaling, use_container_width=True)
            with st.expander("Vezi datele brute de scalabilitate"):
                st.dataframe(df_scaling)
        else:
            st.warning("Nu s-au putut genera rezultate pentru analiza de scalabilitate.")
    
    else: # Ramura pentru o singură rulare
        all_results, valid_inputs = [], False
        kwh_cpu, kwh_data = kwh_cpu_factor_selected, kwh_data_factor_selected
        if selected_scenario == config.SCENARIU_SORTARE:
            s1_N, s1_avg_rec_size, s1_key_idx_size = st.session_state.s1_N, st.session_state.s1_avg_rec_size, st.session_state.s1_key_idx_size
            if s1_N > 0 and s1_avg_rec_size > 0 and s1_key_idx_size > 0:
                all_results = [api_handler.model_standard_sort(s1_N, s1_avg_rec_size, kwh_cpu, kwh_data, gco2_per_kwh_final), api_handler.model_efficient_sort(s1_N, s1_avg_rec_size, kwh_cpu, kwh_data, gco2_per_kwh_final), api_handler.model_sort_index(s1_N, s1_avg_rec_size, s1_key_idx_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
                valid_inputs = True
        elif selected_scenario == config.SCENARIU_RAPORT_VANZARI:
            s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size = st.session_state.s2_N_trans, st.session_state.s2_avg_items, st.session_state.s2_trans_header_size, st.session_state.s2_item_size
            if s2_N_trans > 0 and s2_avg_items > 0 and s2_trans_header_size > 0 and s2_item_size > 0:
                all_results = [api_handler.model_standard_sales_report(s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size, kwh_cpu, kwh_data, gco2_per_kwh_final), api_handler.model_green_sales_report(s2_N_trans, s2_avg_items, s2_trans_header_size, s2_item_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
                valid_inputs = True
        elif selected_scenario == config.SCENARIU_FILTRARE_LOGURI:
            s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size = st.session_state.s3_N_lines, st.session_state.s3_avg_line_len, st.session_state.s3_err_perc, st.session_state.s3_err_msg_size
            if s3_N_lines > 0 and s3_avg_line_len > 0 and s3_err_perc > 0 and s3_err_msg_size > 0:
                all_results = [api_handler.model_standard_log_filter(s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size, kwh_cpu, kwh_data, gco2_per_kwh_final), api_handler.model_green_log_filter(s3_N_lines, s3_avg_line_len, s3_err_perc, s3_err_msg_size, kwh_cpu, kwh_data, gco2_per_kwh_final)]
                valid_inputs = True
        
        if not valid_inputs:
            st.error(f"EROARE: Parametrii pentru '{selected_scenario.split(':')[1].strip()}' trebuie să fie mai mari ca zero.")
        
        if valid_inputs and all_results:
            st.header(f"📊 Rezultate pentru {selected_scenario.split(':')[1].strip()}")
            st.markdown(f"Profil Hardware Selectat: **{selected_hardware_profile_name}**")
            
            if st.button("💾 Salvează în Istoric"):
                run_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                base_info = {"ID Rulare": run_id, "Scenariu": selected_scenario.split(':')[1].strip(), "Hardware": selected_hardware_profile_name, "Sursă CO2": selected_co2_source, "Factor CO2": gco2_per_kwh_final}
                if selected_scenario == config.SCENARIU_SORTARE:
                    base_info.update({"N": st.session_state.s1_N, "Dim. Înreg.": st.session_state.s1_avg_rec_size, "Dim. Cheie": st.session_state.s1_key_idx_size})
                elif selected_scenario == config.SCENARIU_RAPORT_VANZARI:
                    base_info.update({"N": st.session_state.s2_N_trans, "M": st.session_state.s2_avg_items, "Dim. Header": st.session_state.s2_trans_header_size, "Dim. Item": st.session_state.s2_item_size})
                elif selected_scenario == config.SCENARIU_FILTRARE_LOGURI:
                    base_info.update({"L": st.session_state.s3_N_lines, "Lung. Linie": st.session_state.s3_avg_line_len, "% Erori": st.session_state.s3_err_perc})
                for res in all_results:
                    history_entry = base_info.copy()
                    history_entry.update({"Model": res['name'], "Op. CPU": res['cpu_operations'], "Mișc. Date": res['data_movement_units'], "Memorie (u)": res.get('peak_memory_usage_data_units', res.get('memory_usage_data_units', 0.0)), "Energie (kWh)": res['estimated_kwh'], "CO2 (g)": res['estimated_co2_g']})
                    st.session_state.history.append(history_entry)
                st.success(f"Rezultatele pentru rularea {run_id} au fost salvate în istoric!")
            
            standard_model_results = all_results[0]
            reduction_data = []
            for i, result in enumerate(all_results):
                if i > 0:
                    row_reduction = {"Model Verde": result.get('name', 'N/A')}
                    for metric_key, metric_name_ro_short in [("cpu_operations", "CPU"), ("data_movement_units", "Mișc.Date"), ("memory_usage_data_units", "Memorie"), ("estimated_kwh", "Energie"), ("estimated_co2_g", "CO2")]:
                        current_val = result.get('peak_memory_usage_data_units', result.get(metric_key, 0.0))
                        standard_val = standard_model_results.get('peak_memory_usage_data_units', standard_model_results.get(metric_key, 0.0))
                        if standard_val > 1e-9:
                            reduction_percent = ((standard_val - current_val) / standard_val) * 100
                            row_reduction[f"Reducere {metric_name_ro_short} (%)"] = f"{reduction_percent:.1f}%"
                        else:
                            row_reduction[f"Reducere {metric_name_ro_short} (%)"] = "N/A" if current_val == standard_val else "∞"
                    reduction_data.append(row_reduction)
            df_reductions = pd.DataFrame(reduction_data)

            plot_data_abstract = [{"Model": res.get('name', 'N/A'), "Operații CPU": res.get('cpu_operations', 0.0), "Mișcare Date (unități)": res.get('data_movement_units', 0.0), "Memorie Utilizată (unități)": res.get('peak_memory_usage_data_units', res.get('memory_usage_data_units', 0.0))} for res in all_results]
            df_abstract = pd.DataFrame(plot_data_abstract)
            fig_cpu = px.bar(df_abstract, x="Model", y="Operații CPU", color="Model", title="Comparare Operații CPU Estimate", text_auto=True)
            fig_data = px.bar(df_abstract, x="Model", y="Mișcare Date (unități)", color="Model", title="Comparare Mișcare Date Estimate", text_auto=True)
            fig_mem = px.bar(df_abstract, x="Model", y="Memorie Utilizată (unități)", color="Model", title="Comparare Memorie Utilizată Estimată", text_auto=True)
            figs_cost = {"CPU": fig_cpu, "Data Movement": fig_data, "Memory": fig_mem}

            plot_data_impact = [{"Model": res.get('name', 'N/A'), "Energie (kWh)": res.get('estimated_kwh', 0.0), "Emisii CO2 (g)": res.get('estimated_co2_g', 0.0)} for res in all_results]
            df_impact = pd.DataFrame(plot_data_impact)
            fig_kwh = px.bar(df_impact, x="Model", y="Energie (kWh)", color="Model", title="Comparare Energie Consumată Estimată", text_auto=True)
            fig_co2 = px.bar(df_impact, x="Model", y="Emisii CO2 (g)", color="Model", title="Comparare Emisii CO2 Estimate", text_auto=True)
            figs_impact = {"Energy": fig_kwh, "CO2": fig_co2}

            df_history_full = pd.DataFrame(st.session_state.history)
            excel_data = utils.create_excel_export(all_results, df_reductions, df_history_full, figs_cost, figs_impact)
            st.download_button(
                label="📥 Descarcă Raport Excel",
                data=excel_data,
                file_name=f"raport_simulare_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown("---")

            tab_rezumat, tab_grafice_costuri, tab_grafice_impact, tab_istoric, tab_what_if = st.tabs([
                "📝 Rezumat & Reduceri", "📈 Grafice Costuri", "🌍 Grafice Impact", "📜 Istoric Comparații", "🔬 Analiză 'What-If'"
            ])
            
            with tab_rezumat:
                st.subheader("Estimări Costuri & Impact Ambiental (Valori Absolute)")
                for i, result in enumerate(all_results):
                    st.markdown(f"#### Model: {result.get('name', 'N/A')}")
                    
                    real_world_eq = utils.get_real_world_equivalents(result.get('estimated_co2_g', 0.0), gco2_per_kwh_final)
                    eq_text = ""
                    if real_world_eq:
                        km_ev = real_world_eq.get("km parcurși cu o mașină electrică", 0)
                        tree_hours = real_world_eq.get("ore necesare unui copac pentru a absorbi", 0)
                        if km_ev > 0.01:
                            eq_text += f"🚗 **{km_ev:.2f} km** cu o mașină electrică"
                        if tree_hours > 0.1:
                            if eq_text: eq_text += " sau "
                            eq_text += f"🌳 **{tree_hours:.1f} ore** de absorbție de către un copac."
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1: st.metric("💻 Op. CPU", f"{result.get('cpu_operations', 0.0):,.0f}")
                    with col2: st.metric("💾 Mișc. Date", f"{result.get('data_movement_units', 0.0):,.0f}")
                    with col3:
                        mem_usage = result.get('peak_memory_usage_data_units', result.get('memory_usage_data_units', 0.0))
                        st.metric("🧠 Memorie", f"{mem_usage:,.0f}")
                    with col4: st.metric("⚡ Energie (kWh)", f"{result.get('estimated_kwh', 0.0):.6f}")
                    with col5: st.metric("💨 CO2 (g)", f"{result.get('estimated_co2_g', 0.0):,.2f}", help=eq_text if eq_text else "Nu există echivalent semnificativ")
                    
                    st.caption(f"Complexitate CPU: {result.get('complexity_cpu', 'N/A')} | Complexitate Memorie: {result.get('complexity_memory', 'N/A')}")
                    model_name = result.get('name')
                    if model_name and model_name in config.MODEL_EXPLANATIONS:
                        with st.expander("💡 Analiză și Recomandări"):
                            st.markdown(config.MODEL_EXPLANATIONS[model_name], unsafe_allow_html=True)
                    st.markdown("---")
                if not df_reductions.empty:
                    st.subheader("📊 Tabel Reduceri Procentuale vs. Modelul Standard")
                    st.dataframe(df_reductions.set_index("Model Verde"))

            with tab_grafice_costuri:
                st.subheader("Grafice Comparative: Costuri Abstracte (Interactive)")
                for fig in figs_cost.values():
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab_grafice_impact:
                st.subheader("Grafice Comparative: Impact Energetic și CO2 (Interactive)")
                for fig in figs_impact.values():
                    st.plotly_chart(fig, use_container_width=True)

            with tab_istoric:
                st.subheader("📜 Istoric Detaliat al Comparațiilor")
                if not df_history_full.empty:
                    st.dataframe(df_history_full, use_container_width=True, column_config={"Op. CPU": st.column_config.NumberColumn(format="%.0f"), "Mișc. Date": st.column_config.NumberColumn(format="%.0f"), "Memorie (u)": st.column_config.NumberColumn(format="%.0f"), "Energie (kWh)": st.column_config.NumberColumn(format="%.6f"), "CO2 (g)": st.column_config.NumberColumn(format="%.3f"), "Factor CO2": st.column_config.NumberColumn(format="%.2f")}, hide_index=True)
                    if st.button("🗑️ Golește Istoricul", key="clear_history_in_tab"):
                        st.session_state.history = []
                        st.rerun()
                    st.markdown("---")
                    st.subheader("📊 Grafice Comparative din Istoric")
                    run_ids = df_history_full["ID Rulare"].unique().tolist()
                    selected_runs = st.multiselect("Alege rulările de comparat (după ID):", options=run_ids, default=run_ids[-2:] if len(run_ids) >= 2 else run_ids)
                    metric_options = ["CO2 (g)", "Energie (kWh)", "Op. CPU", "Mișc. Date", "Memorie (u)"]
                    selected_metric = st.selectbox("Alege metrica de vizualizat:", options=metric_options)
                    if selected_runs and len(selected_runs) >= 1:
                        df_filtered = df_history_full[df_history_full["ID Rulare"].isin(selected_runs)]
                        fig_history = px.bar(df_filtered, x="Model", y=selected_metric, color="ID Rulare", barmode="group", title=f"Comparație pentru metrica: {selected_metric}", labels={"ID Rulare": "ID Rulare", selected_metric: f"Valoare {selected_metric}"})
                        fig_history.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_history, use_container_width=True)
                    else:
                        st.info("Selectează cel puțin o rulare din lista de mai sus pentru a genera un grafic.")
                else:
                    st.info("Niciun rezultat salvat în această sesiune.")

            with tab_what_if:
                st.subheader("🔬 Analiză de Sensibilitate 'What-If'")
                st.info("Explorați cum se modifică impactul dacă variați un singur parametru secundar, menținând restul constanți.")
                what_if_params = {
                    config.SCENARIU_SORTARE: {"Dim. înregistrare (u)": "s1_avg_rec_size"},
                    config.SCENARIU_RAPORT_VANZARI: {"Nr. mediu itemi/tranz. (M)": "s2_avg_items", "Dim. item tranz. (u)": "s2_item_size"},
                    config.SCENARIU_FILTRARE_LOGURI: {"Procentaj linii eroare (%)": "s3_err_perc", "Lung. medie linie (u)": "s3_avg_line_len"}
                }
                param_to_vary_name = st.selectbox("Alege parametrul de variat:", options=list(what_if_params[selected_scenario].keys()), key="what_if_param_select")
                
                if param_to_vary_name:
                    param_key = what_if_params[selected_scenario][param_to_vary_name]
                    current_value = st.session_state[param_key]
                    min_val = max(1, int(current_value * 0.2))
                    max_val = int(current_value * 2.0)
                    varied_range = st.slider(f"Alege un interval pentru '{param_to_vary_name}':", min_value=min_val, max_value=max_val, value=(min_val, max_val), key="what_if_slider")
                    what_if_results = []
                    for val in np.linspace(varied_range[0], varied_range[1], 15, dtype=int):
                        models = []
                        if selected_scenario == config.SCENARIU_SORTARE:
                            # Variabilele 's1_N', etc., nu sunt definite în acest scope. Trebuie să le luăm din st.session_state
                            s1_N_local, s1_key_idx_size_local = st.session_state.s1_N, st.session_state.s1_key_idx_size
                            args_std = (s1_N_local, val, kwh_cpu, kwh_data, gco2_per_kwh_final)
                            args_eff = (s1_N_local, val, kwh_cpu, kwh_data, gco2_per_kwh_final)
                            args_idx = (s1_N_local, val, s1_key_idx_size_local, kwh_cpu, kwh_data, gco2_per_kwh_final)
                            models = [api_handler.model_standard_sort(*args_std), api_handler.model_efficient_sort(*args_eff), api_handler.model_sort_index(*args_idx)]
                        elif selected_scenario == config.SCENARIU_RAPORT_VANZARI:
                            base_args = {"num_transactions": st.session_state.s2_N_trans, "avg_items_per_transaction": st.session_state.s2_avg_items, "avg_record_size_transaction_header": st.session_state.s2_trans_header_size, "avg_record_size_item": st.session_state.s2_item_size, "kwh_cpu": kwh_cpu, "kwh_data": kwh_data, "gco2_factor": gco2_per_kwh_final}
                            if param_key == "s2_avg_items": base_args["avg_items_per_transaction"] = val
                            if param_key == "s2_item_size": base_args["avg_record_size_item"] = val
                            models = [api_handler.model_standard_sales_report(**base_args), api_handler.model_green_sales_report(**base_args)]
                        elif selected_scenario == config.SCENARIU_FILTRARE_LOGURI:
                            base_args = {"num_log_lines": st.session_state.s3_N_lines, "avg_line_length": st.session_state.s3_avg_line_len, "error_line_percentage": st.session_state.s3_err_perc, "avg_error_message_size": st.session_state.s3_err_msg_size, "kwh_cpu": kwh_cpu, "kwh_data": kwh_data, "gco2_factor": gco2_per_kwh_final}
                            if param_key == "s3_err_perc": base_args["error_line_percentage"] = val
                            if param_key == "s3_avg_line_len": base_args["avg_line_length"] = val
                            models = [api_handler.model_standard_log_filter(**base_args), api_handler.model_green_log_filter(**base_args)]
                        for res in models:
                            res[param_to_vary_name] = val
                            what_if_results.append(res)
                    df_what_if = pd.DataFrame(what_if_results)
                    fig_what_if = px.line(df_what_if, x=param_to_vary_name, y="estimated_co2_g", color="name", title=f"Sensibilitatea emisiilor de CO2 la '{param_to_vary_name}'", labels={"estimated_co2_g": "Emisii CO2 (g)", "name": "Model"}, markers=True)
                    st.plotly_chart(fig_what_if, use_container_width=True)

            st.markdown("---")
            st.info(config.DISCLAIMER_TEXT)

elif not st.session_state.simulation_has_run:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.header("Bun venit la Simulatorul de Impact Software!")
        st.markdown(config.INFO_START_MESSAGE)
        st.info("Aplicația demonstrează cum alegerile algoritmice și de design pot influența consumul de resurse și emisiile de CO2.")
        st.warning("**Toate valorile sunt estimări ilustrative.** Scopul este de a compara impactul *relativ* între diferite abordări.")
    with col2:
        st.markdown("### Cum funcționează?")
        st.markdown("""
        1.  **Alegeți un Scenariu:** Selectați un caz de utilizare comun (sortare, raportare, etc.).
        2.  **Configurați Parametrii:** Ajustați dimensiunea datelor și alți factori relevanți.
        3.  **Selectați Hardware și Sursă CO2:** Alegeți un profil hardware și sursa pentru calculul emisiilor.
        4.  **Rulați Simularea:** Apăsați butonul pentru a vedea o comparație detaliată între o abordare standard și una optimizată ("verde").
        """)
