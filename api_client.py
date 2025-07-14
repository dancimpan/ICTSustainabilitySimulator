# api_client.py

import streamlit as st
import requests
import os
# Nu mai este nevoie de load_dotenv aici dacă este deja în config.py și config.py este importat devreme în app_streamlit.py
# from dotenv import load_dotenv
# load_dotenv() # Asigură-te că EM_API_KEY este disponibil ca variabilă de mediu

@st.cache_data(ttl=24*3600) # Cache pentru 24 de ore
def get_romania_carbon_intensity():
    """
    Obține intensitatea carbonică pentru România de la API-ul Electricity Maps.
    Folosește cheia API din variabilele de mediu.
    Afișează mesaje de avertizare/succes/eroare în interfața Streamlit.

    Returns:
        float or None: Intensitatea carbonică (gCO2eq/kWh) sau None dacă eșuează.
    """
    api_key = os.getenv("EM_API_KEY")
    zone_code = "RO"

    if not api_key:
        # Acest mesaj va apărea în contextul în care funcția este apelată.
        # Este mai bine ca mesajele specifice UI să fie gestionate în app_streamlit.py
        # dar pentru simplitate și pentru că funcția este @st.cache_data,
        # un warning aici poate fi util.
        if 'api_key_warning_shown_details' not in st.session_state:
            st.warning(f"Cheia API (EM_API_KEY) lipsește pentru Electricity Maps. Se va folosi valoarea implicită pentru CO2.")
            st.session_state.api_key_warning_shown_details = True
        return None

    headers = {'auth-token': api_key}
    try:
        response = requests.get(f'https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_code}', headers=headers)
        response.raise_for_status()  # Va ridica o excepție pentru statusuri HTTP 4xx/5xx
        data = response.json()
        carbon_intensity = data.get('carbonIntensity')

        if carbon_intensity is not None:
            # Similar, gestionarea st.session_state pentru mesaje de succes
            # poate fi mai curat gestionată în app_streamlit.py
            if 'api_call_success_msg_shown' not in st.session_state or \
               not st.session_state.api_call_success_msg_shown.get(zone_code, False):
                st.success(f"Intensitatea CO2 pentru România: {carbon_intensity:.2f} gCO2eq/kWh (Sursa: Electricity Maps). Cache: 24h.")
                if 'api_call_success_msg_shown' not in st.session_state:
                    st.session_state.api_call_success_msg_shown = {}
                st.session_state.api_call_success_msg_shown[zone_code] = True
            return float(carbon_intensity)
        else:
            st.warning(f"Răspuns API invalid pentru România (Electricity Maps). Se folosește valoarea implicită.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Eroare API România (Electricity Maps): {e}. Se folosește valoarea implicită.")
        return None
    except Exception as e: # Captură mai generală pentru alte erori neașteptate
        st.error(f"Eroare neașteptată la preluarea datelor CO2 pentru România: {e}. Se folosește valoarea implicită.")
        return None
