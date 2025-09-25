# app.py (Frontend - Streamlit)

import streamlit as st
import requests
from datetime import datetime, timedelta
import random
from translations import APP_STRINGS  # Asume que este archivo existe y está en el repositorio.

# La URL de tu API en la nube (la que te dio Render). ¡DEBES CAMBIAR ESTO!
API_URL = "https://nutrigoal-api.onrender.com"

# Set wide layout for the app once at the beginning
st.set_page_config(layout="wide", page_title="NutriGoal")

# Inject custom CSS for centering the tabs
st.markdown("""
<style>
div[data-baseweb="tab-list"] {
    justify-content: center;
    gap: 1rem;
}
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

def get_foods_from_api():
    """Fetches the list of foods from the API based on the selected language."""
    try:
        lang = st.session_state.get('lang', 'es')
        response = requests.get(f"{API_URL}/api/foods?lang={lang}")
        if response.status_code == 200:
            return response.json()
        else:
            # Manejar errores que no son de conexión pero el servidor está activo
            st.error("Error al obtener la lista de alimentos. Código de estado: " + str(response.status_code))
            return []
    except requests.exceptions.ConnectionError:
        st.error("Error al conectar con la API. Asegúrate de que el servidor está funcionando.")
        return []


def get_user_goal_from_api(token):
    """Fetches the user's weekly vegetable goal from the API."""
    headers = {
        "x-access-tokens": token
    }
    try:
        response = requests.get(f"{API_URL}/api/user/goal", headers=headers)
        if response.status_code == 200:
            return response.json().get('weekly_vegetable_goal', 30)
        else:
            return 30
    except requests.exceptions.ConnectionError:
        st.error(
            "Error al conectar con la API para obtener el objetivo. Asegúrate de que el servidor está funcionando.")
        return 30


def add_food_log(food_id, token):
    headers = {
        "x-access-tokens": token
    }
    data = {
        "food_id": food_id
    }
    try:
        response = requests.post(f"{API_URL}/api/user_food_logs", headers=headers, json=data)
        if response.status_code == 201:
            st.success("¡Alimento añadido con éxito!")
            st.rerun()  # Force a refresh to update the history table
        else:
            if response.content:
                error_message = response.json().get('error', 'Error desconocido')
                st.error("Error al añadir el alimento. Mensaje del servidor: " + error_message)
            else:
                st.error("Error al añadir el alimento. El servidor no devolvió una respuesta válida.")

    except requests.exceptions.ConnectionError:
        st.error("Error al conectar con la API. Asegúrate de que el servidor está funcionando.")


def get_food_logs_from_api(token):
    """Fetches the user's food log history from the API."""
    headers = {
        "x-access-tokens": token
    }
    try:
        response = requests.get(f"{API_URL}/api/user_food_logs", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            if response.content:
                error_message = response.json().get('error', 'Error desconocido')
                st.error("Error al obtener el historial. Mensaje del servidor: " + error_message)
            else:
                st.error("Error al obtener el historial. El servidor no devolvió una respuesta válida.")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Error al conectar con la API. Asegúrate de que el servidor está funcionando.")
        return []


def get_suggested_foods_from_api(token):
    """Fetches a list of suggested foods for the user from the API."""
    headers = {
        "x-access-tokens": token
    }
    try:
        response = requests.get(f"{API_URL}/api/suggested_foods", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Error al obtener las sugerencias. Mensaje del servidor: " + response.json().get('error', ''))
            return []
    except requests.exceptions.ConnectionError:
        st.error("Error al conectar con la API para obtener sugerencias.")
        return []


def get_user_progress_from_api(token):
    """Calculates the number of unique vegetables consumed this week."""
    headers = {
        "x-access-tokens": token
    }
    try:
        response = requests.get(f"{API_URL}/api/user_progress", headers=headers)
        if response.status_code == 200:
            return response.json().get('vegetable_count', 0)
        else:
            st.error(
                "Error al obtener el progreso del usuario. Mensaje del servidor: " + response.json().get('error', ''))
            return 0
    except requests.exceptions.ConnectionError:
        st.error("Error al conectar con la API para obtener el progreso.")
        return []


def get_diversity_metrics_from_api(token):
    headers = {"x-access-tokens": token}
    try:
        response = requests.get(f"{API_URL}/api/diversity_metrics", headers=headers)
        if response.status_code == 200:
            return response.json()
        return {"prebiotic_count": 0, "probiotic_count": 0}
    except requests.exceptions.ConnectionError:
        return {"prebiotic_count": 0, "probiotic_count": 0}


def get_user_vegetables_from_api(token):
    """Fetches the list of unique vegetables consumed by the user this week."""
    headers = {
        "x-access-tokens": token
    }
    try:
        response = requests.get(f"{API_URL}/api/user_vegetables", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.exceptions.ConnectionError:
        return []


def get_user_prebiotics_from_api(token):
    """Fetches the list of unique prebiotics consumed by the user this week."""
    headers = {"x-access-tokens": token}
    try:
        response = requests.get(f"{API_URL}/api/user_prebiotics", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        return {"prebiotic_count": 0}


def get_user_probiotics_from_api(token):
    """Fetches the list of unique probiotics consumed by the user this week."""
    headers = {"x-access-tokens": token}
    try:
        response = requests.get(f"{API_URL}/api/user_probiotics", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        return {"probiotic_count": 0}


def delete_food_log_from_api(log_id, token):
    headers = {"x-access-tokens": token}
    try:
        response = requests.delete(f"{API_URL}/api/user_food_logs/{log_id}", headers=headers)
        if response.status_code == 200:
            st.success("¡Alimento eliminado con éxito!")
            st.rerun()  # Force a refresh to update the history table
        else:
            st.error("Error al eliminar el alimento.")
    except requests.exceptions.ConnectionError:
        st.error("Error de conexión al intentar eliminar el alimento.")


# Datos para la Dosis Exprés de Sabiduría Nutricional
NUTRI_WISDOMS = [
    "¿Tu mal humor viene de tu intestino? 🧠El 90% de la serotonina (la hormona del bienestar) se produce en el intestino.",
    "Niebla mental y tu barriga: ¿hay conexión? La inflamación intestinal puede afectar a la función cognitiva a través del nervio vago.",
    "Esas 'mariposas en el estómago' son REALES. Te explico por qué. El sistema nervioso entérico, o 'segundo cerebro', reacciona directamente a nuestras emociones.",
    "¿Antojos de azúcar incontrolables? Culpa a tus bacterias. 🦠Ciertas bacterias intestinales pueden enviar señales al cerebro para que consumas los alimentos que ellas prefieren (azúcar, grasas).",
    "3 formas en las que el estrés te está hinchando (literalmente). El cortisol (hormona del estrés) puede alterar la permeabilidad intestinal y la composición de la microbiota.",
    "¿Ansiedad y problemas digestivos van de la mano? La ciencia dice SÍ. El eje intestino-cerebro es una autovía de comunicación bidireccional. Un intestino irritado puede enviar señales de alerta al cerebro.",
    "Duermes mal y te levantas cansado… ¿Y si la respuesta está en tu cena? Una microbiota desequilibrada puede afectar a la producción de melatonina y alterar los ciclos de sueño.",
    "La intuición es intestinal. Aprende a escuchar a tu 'segundo cerebro'. 🧠El intestino envía muchísima más información al cerebro de la que recibe de él. ¡Escúchalo!",
    "¿Te sientes sin energía? Tu intestino podría estar robándotela. ⚡️Una mala absorción de nutrientes por un intestino dañado significa menos combustible para tu cuerpo y tu mente.",
    "Cómo un intestino feliz te ayuda a gestionar mejor el estrés. Una microbiota sana puede ayudar a regular los niveles de cortisol, la hormona del estrés.",
    "Tienes un ZOO dentro de ti. ¿Lo estás cuidando bien? 🦠Tenemos unos 38 billones de microorganismos en nuestro cuerpo, ¡la mayoría en el intestino!",
    "Hinchazón, gases, cansancio... Podría ser DISBIOSIS. ¿Qué es eso? La disbiosis es el desequilibrio entre las bacterias 'buenas' y 'malas' de tu microbiota.",
    "3 señales de que tus bacterias intestinales piden auxilio. Señales: problemas de piel (acné, eccemas), digestiones pesadas constantes, y antojos de azúcar.",
    "El antibiótico te curó, pero... ¿qué le hizo a tu microbiota? Los antibióticos son como una bomba: arrasan con las bacterias malas, pero también con muchas de las buenas.",
    "¿Tu 'jardín interior' está lleno de malas hierbas? 🌿Analogía visual: un jardín cuidado (microbiota sana) vs. uno descuidado (disbiosis).",
    "No todas las bacterias son malas. ¡Necesitas a las buenas para vivir! Las bacterias beneficiosas ayudan a digerir alimentos, producir vitaminas y protegerte de patógenos.",
    "La causa nº1 de tu hinchazón crónica que no estás mirando. La disbiosis y el sobrecrecimiento bacteriano (SIBO) son causas muy comunes de la hinchazón persistente.",
    "¿Por qué te sientan mal alimentos que antes no lo hacían? Un desequilibrio en la microbiota puede reducir tu capacidad para digerir ciertos alimentos.",
    "El secreto mejor guardado de tu sistema inmune está en tu barriga. Aproximadamente el 70-80% de tu sistema inmunitario reside en tu intestino.",
    "De 0 a 10, ¿cómo de feliz está tu microbiota? (Mini-Test) Preguntas sobre dieta, estrés, sueño y regularidad para que el usuario se autoevalúe.",
    "El plato favorito de tus bacterias buenas. 🌱Los prebióticos son fibras que alimentan a los microorganismos beneficiosos de tu intestino.",
    "¿Probiótico o Prebiótico? La diferencia que cambiará tu salud. Probiótico = la bacteria viva. Prebiótico = el alimento para esa bacteria. ¡Necesitas ambos!",
    "3 superalimentos PREBIÓTICOS que seguro tienes en tu cocina. Ajo, cebolla y plátano (especialmente si no está muy maduro).",
    "¿Por qué la fibra es la superestrella de tu salud intestinal? 🌟La fibra prebiótica es fermentada por tus bacterias, produciendo compuestos antiinflamatorios como el butirato.",
    "El snack de 1€ que alimenta tu felicidad (y a tus microbios). Un plátano, una manzana o un puñado de almendras. Fáciles y llenos de fibra.",
    "No solo tú tienes hambre... ¡Tus bacterias también! Explicación sencilla y visual de cómo los prebióticos viajan por el intestino para alimentar a la microbiota.",
    "La receta más fácil para empezar a darle prebióticos a tu cuerpo. Ejemplo: Tostada con aguacate y un poco de cebolla roja picada por encima.",
    "¿Sabías que las patatas enfriadas son un manjar para tu intestino? Al enfriar la patata cocida, parte de su almidón se convierte en almidón resistente, un potente prebiótico.",
    "Añade ESTO a tus ensaladas para un boost de salud intestinal. Legumbres como lentejas o garbanzos, o semillas como las de chía o lino.",
    "El desayuno que prepara tu intestino para un gran día. ⚡️Porridge de avena con frutos rojos y semillas. La avena es rica en beta-glucanos, un tipo de fibra prebiótica.",
    "MITO: 'Para deshincharte, bebe zumos detox'. Realidad: Tu hígado y riñones son los verdaderos detox. Los zumos sin fibra pueden ser bombas de azúcar.",
    "MITO: 'Quitar el gluten es la solución para todos'. Realidad: Solo un pequeño % tiene celiaquía. El problema puede ser otro (FODMAPs, disbiosis...).",
    "MITO: 'Comer sin grasa es más sano'. Realidad: Las grasas saludables (aguacate, aceite de oliva, frutos secos) son esenciales para reducir la inflamación y absorber vitaminas.",
    "MITO: 'Hay que hacer 5 comidas al día para estar sano'. Realidad: No hay una regla universal. Escuchar a tu cuerpo y sus señales de hambre/saciedad es más importante.",
    "MITO: 'Los carbohidratos por la noche engordan y sientan mal'. Realidad: Un carbohidrato complejo de calidad (boniato, quinoa) puede ayudar a la producción de serotonina y a dormir mejor.",
    "MITO: 'Si tienes gases, elimina las legumbres'. Realidad: Los gases pueden ser señal de que estás alimentando a tus bacterias. ¡Es bueno! Empieza con poca cantidad y ponlas en remojo.",
    "MITO: 'Los alimentos 'light' son mejores para ti'. Realidad: A menudo contienen edulcorantes artificiales que pueden dañar tu microbiota y más aditivos.",
    "MITO: 'Necesitas un suplemento probiótico carísimo para estar bien'. Realidad: La base siempre es la comida. La diversidad alimentaria es el probiótico más potente y barato.",
    "¿El pan hincha? Desmontando el mito más famoso. Depende del tipo de pan (masa madre vs. industrial), de tu microbiota y de con qué lo acompañas.",
    "'Bebe 2 litros de agua al día'. ¿Es esto cierto para todos? Realidad: Las necesidades de agua varían por persona, clima y actividad. ¡Aprende a escuchar tu sed!",
    "¿Comes siempre lo mismo? Tu intestino se aburre 😴. Una dieta monótona conduce a una microbiota pobre y menos resiliente.",
    "El reto de los 30 vegetales por semana. ¿Te atreves? Explica el concepto: contar diferentes tipos de plantas (frutas, verduras, legumbres, granos, frutos secos, semillas, hierbas, especias).",
    "¿Por qué contar PLANTAS y no CALORÍAS? 🥦Cambia el foco de la restricción a la abundancia y la nutrición de tu microbiota.",
    "Cómo hacer tu compra más diversa (y feliz para tu intestino). Tips: compra una verdura nueva cada semana, elige mixes de ensalada, compra legumbres variadas.",
    "Dale un arcoíris a tu plato. ¡Tus bacterias te lo agradecerán! 🌈Cada color en frutas y verduras representa diferentes fitonutrientes y fibras que alimentan a distintos tipos de bacterias.",
    "Tu intestino NO quiere que hagas dietas súper restrictivas. Las dietas muy limitadas matan de hambre a tus bacterias buenas, reduciendo su diversidad y tu salud a largo plazo.",
    "3 especias antiinflamatorias para potenciar tus platos y tu salud. Cúrcuma, jengibre y canela. Cuentan para el reto de las 30 plantas.",
    "El poder de las hierbas aromáticas: no son solo para decorar. 🌱Perejil, cilantro, menta, albahaca... son ricas en polifenoles y fáciles de añadir a todo.",
    "¿Tu café cuenta como planta? ¡SÍ! (Y otros trucos para sumar diversidad). El café, el té, el cacao puro y las especias suman a la diversidad de plantas.",
    "Un plato diverso no tiene por qué ser complicado. Mira esto. Muestra un plato sencillo pero diverso (ej: lentejas con arroz, espinacas y un toque de cúrcuma) y pregunta cuántas plantas diferentes ven."
]


# --- Page Content Functions ---

def render_home_content():
    strings = APP_STRINGS[st.session_state.lang]

    # Header and greeting
    st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>NutriGoal</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Tu guía hacia una microbiota saludable</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Progress Ring and Diversity Metrics
    col_progress_main, col_diversity_main, col_add_button = st.columns([1, 2, 0.5])

    with col_progress_main:
        user_goal = get_user_goal_from_api(st.session_state.token)
        vegetable_count = get_user_progress_from_api(st.session_state.token)

        # Simulate a progress ring with a large metric
        st.markdown(
            f"<h1 style='text-align: center; font-size: 4em; color: #4CAF50;'>{vegetable_count}</h1>"
            f"<p style='text-align: center; font-size: 1.5em;'>/{user_goal}</p>",
            unsafe_allow_html=True
        )
        # Progress bar to simulate the ring
        st.progress(vegetable_count / user_goal)

        with st.expander("Vegetales únicos esta semana"):
            vegetables_consumed = get_user_vegetables_from_api(st.session_state.token)
            if vegetables_consumed:
                for veg in vegetables_consumed:
                    st.write(f"- {veg}")
            else:
                st.write(strings['no_food_added'])

    with col_diversity_main:
        st.markdown("<h3 style='color: #4CAF50;'>Diversidad Semanal</h3>", unsafe_allow_html=True)
        diversity_metrics = get_diversity_metrics_from_api(st.session_state.token)
        prebiotic_count = diversity_metrics['prebiotic_count']
        probiotic_count = diversity_metrics['probiotic_count']

        with st.expander(f"🌱 Prebióticos: {prebiotic_count}/5"):
            prebiotics_consumed = get_user_prebiotics_from_api(st.session_state.token)
            if prebiotics_consumed:
                for pre in prebiotics_consumed:
                    st.write(f"- {pre}")
            else:
                st.write("No has añadido prebióticos esta semana.")

        with st.expander(f"🦠 Probióticos: {probiotic_count}/3"):
            probiotics_consumed = get_user_probiotics_from_api(st.session_state.token)
            if probiotics_consumed:
                for pro in probiotics_consumed:
                    st.write(f"- {pro}")
            else:
                st.write("No has añadido probióticos esta semana.")

    # Add food button
    with col_add_button:
        # Initialize session state for expander if it doesn't exist
        if 'add_food_expander' not in st.session_state:
            st.session_state.add_food_expander = False

        if st.button("➕", key="add_food_btn", help="Añadir alimento"):
            # Toggle the expander state
            st.session_state.add_food_expander = not st.session_state.add_food_expander
            st.rerun()

    st.markdown("---")

    # Add food form (now inside an expander)
    # The expander is controlled by the state of the session variable
    with st.expander("Añadir Alimento", expanded=st.session_state.add_food_expander):
        foods = get_foods_from_api()
        food_names = [f['name'] for f in foods]
        food_dict = {f['name']: f['id'] for f in foods}

        food_selection = st.selectbox(strings['select_food'], food_names, key='food_select')
        selected_food_id = food_dict.get(food_selection)

        add_food_col = st.columns([1, 2, 1])[1]  # Centered button
        with add_food_col:
            if st.button(strings['add_button'], key='add_button_float', use_container_width=True):
                if selected_food_id:
                    add_food_log(selected_food_id, st.session_state.token)

    # Suggestions
    st.markdown(f"<h3 style='text-align: center;'>💡 {strings['suggestions_title']}</h3>", unsafe_allow_html=True)
    suggested_foods = get_suggested_foods_from_api(st.session_state.token)

    if suggested_foods:
        # Display up to 3 suggestions
        suggested_foods_limited = suggested_foods[:3]
        suggestion_cols = st.columns(len(suggested_foods_limited))
        for i, food in enumerate(suggested_foods_limited):
            with suggestion_cols[i]:
                st.button(food['name'], key=f"suggested_food_{food['id']}", use_container_width=True)
    else:
        st.write(f"<p style='text-align: center;'>{strings['congratulations_all_eaten']}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # Wisdom Tip
    st.markdown(f"<h3 style='text-align: center;'>Aquí Tienes Tu Dosis Exprés de Sabiduría Nutricional ⚡</h3>",
                unsafe_allow_html=True)
    with st.container(border=True):  # Use border for a card-like effect
        st.markdown(f"**{random.choice(NUTRI_WISDOMS)}**")


def render_history_content():
    strings = APP_STRINGS[st.session_state.lang]
    st.title(strings['history_button'])
    st.markdown("---")

    logs = get_food_logs_from_api(st.session_state.token)

    if logs:
        st.write(strings['last_foods_added'])
        # Simplified table for history
        for log in logs:
            col_food, col_date, col_action = st.columns([2, 1.5, 1])
            with col_food:
                st.write(log['food_name'])
            with col_date:
                st.write(log['date_consumed'])
            with col_action:
                if st.button("🗑️", key=f"delete_{log['log_id']}", help=strings['delete_button']):
                    delete_food_log_from_api(log['log_id'], st.session_state.token)
            st.markdown("---")  # Separator for each log item
    else:
        st.write(strings['no_food_added'])


def render_achievements_content():
    strings = APP_STRINGS[st.session_state.lang]
    st.title(strings['achievements_button'])
    st.markdown("---")
    st.write("Esta es la página de logros. Aquí se mostrarán los logros que has desbloqueado.")
    st.info("¡Pronto habrá más logros para desbloquear!")


def render_profile_content():
    strings = APP_STRINGS[st.session_state.lang]
    st.title(strings['profile_button'])
    st.markdown("---")
    st.write(f"**{strings['username_input']}:** {st.session_state.username}")
    st.write(f"**{strings['full_name_input']}:** {st.session_state.full_name}")

    st.markdown("---")
    st.header(strings['update_goal_title'])
    user_goal = get_user_goal_from_api(st.session_state.token)
    with st.form("goal_form"):
        new_goal = st.number_input(strings['new_goal_input'], min_value=1, value=user_goal, key="new_goal")
        submitted = st.form_submit_button(strings['save_goal_button'])
        if submitted:
            headers = {"x-access-tokens": st.session_state.token}
            response = requests.put(f"{API_URL}/api/user/goal", headers=headers, json={"goal": new_goal})
            if response.status_code == 200:
                st.success(strings['goal_success'])
                st.rerun()
            else:
                st.error(strings['goal_error'])

    st.markdown("---")
    if st.button(strings['logout_button'], type="secondary"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.page = "login"
        st.rerun()


def render_guide_content():
    """Renders the content for the 'Guide' page with the combined text."""
    st.title("Guía de la Nutrición de la Microbiota")
    st.markdown("---")
    st.write("""
        ### ¿Qué es la Microbiota Intestinal?
        La microbiota intestinal es una comunidad de trillones de microorganismos (bacterias, virus, hongos) que viven en nuestro intestino. Estos pequeños "huéspedes" no solo nos ayudan a digerir los alimentos, sino que también juegan un papel fundamental en nuestra salud general, desde el sistema inmunológico hasta el estado de ánimo.

        ---

        ### La Regla de Oro: La Diversidad
        Para mantener una microbiota sana y diversa, la clave es una dieta variada. La regla de los **30 vegetales a la semana** no es un número mágico, sino un objetivo para animarte a probar diferentes tipos de plantas. Cada planta contiene fibras y nutrientes únicos que alimentan a distintos tipos de bacterias, promoviendo así un ecosistema más robusto y resiliente.

        ---

        ### Alimentos para una Microbiota Feliz
        * **Vegetales:** Alimentos como el brócoli, las espinacas, las zanahorias y los pimientos son ricos en fibra y vitaminas.
        * **Frutas:** Las manzanas, plátanos, bayas y cítricos son excelentes fuentes de fibra.
        * **Legumbres:** Lentejas, garbanzos, frijoles... ¡son superalimentos para tu microbiota!
        * **Cereales Integrales:** Avena, quinoa, arroz integral.
        * **Prebióticos:** Estos son alimentos que nutren a las bacterias beneficiosas. Se encuentran en el ajo, la cebolla, los espárragos y las alcachofas.
        * **Probióticos:** Alimentos que contienen bacterias vivas beneficiosas, como el yogur, el kéfir y el chucrut.

        ---

        ### ¿Por qué es importante?
        Una microbiota diversa se ha relacionado con beneficios como una mejor digestión, un sistema inmune más fuerte, menor riesgo de enfermedades crónicas y una mejor salud mental. NutriGoal te ayuda a seguir el camino hacia una microbiota más feliz.
    """)

    st.markdown("---")
    st.markdown("### El Eje Intestino-Cerebro: Tu Segundo Cerebro 🧠")
    st.write("""
        ¿Sabías que tu intestino y tu cerebro están constantemente hablando entre sí? Esta comunicación bidireccional se conoce como el **eje intestino-cerebro**.

        * **El 90% de la serotonina** (la hormona del bienestar) se produce en tu intestino. Una microbiota sana es clave para un buen humor.
        * **Las 'mariposas en el estómago' son REALES.** El sistema nervioso entérico, o 'segundo cerebro', reacciona directamente a tus emociones.
        * **Niebla mental y tu barriga:** La inflamación intestinal puede afectar a la función cognitiva.
        * **¿Antojos de azúcar incontrolables?** Culpa a tus bacterias. Algunas pueden enviar señales al cerebro para que consumas los alimentos que ellas prefieren.
    """)
    st.markdown("---")
    st.markdown("### Disbiosis: El Desequilibrio en tu Jardín Interior 🦠")
    st.write("""
        Tu microbiota es como un jardín. Si la cuidas, florece. Si no, se llena de "malas hierbas". La **disbiosis** es el desequilibrio entre las bacterias "buenas" y "malas".
        * **Síntomas de disbiosis:** Hinchazón, gases, cansancio, problemas de piel (acné, eccemas) y antojos de azúcar.
        * **Los antibióticos** son como una bomba: eliminan bacterias malas, pero también muchas de las buenas. Es importante reconstruir tu microbiota después.
        * **La causa nº1 de tu hinchazón crónica:** A menudo es la disbiosis o el sobrecrecimiento bacteriano (SIBO).
        * **El secreto de tu sistema inmune:** Aproximadamente el 70-80% de tu sistema inmunitario reside en tu intestino.
    """)
    st.markdown("---")
    st.markdown("### Prebióticos y Probióticos: El Dúo Dinámico 💪")
    st.write("""
        Para cultivar una microbiota feliz, necesitas los ingredientes correctos:
        * **Probióticos:** Son las bacterias vivas beneficiosas que encuentras en alimentos como el yogur, el kéfir o el chucrut.
        * **Prebióticos:** Son el alimento para esas bacterias. Piensa en ellos como el fertilizante para tu jardín. Se encuentran en alimentos ricos en fibra como el ajo, la cebolla, los plátanos (poco maduros) y las patatas enfriadas.
        * **La fibra** es la superestrella de tu salud intestinal. Al fermentar la fibra prebiótica, tus bacterias producen compuestos antiinflamatorios como el butirato.
        * **La regla de los 30 vegetales:** El objetivo es consumir 30 tipos diferentes de plantas (frutas, verduras, legumbres, granos, frutos secos, semillas, hierbas, especias) por semana para asegurar la máxima diversidad para tu microbiota.
    """)
    st.markdown("---")
    st.markdown("### Mitos sobre la Salud Intestinal 🤯")
    st.write("""
        * **Mito: 'Para deshincharte, bebe zumos detox'.** Realidad: Tu hígado y riñones son los verdaderos detox. Los zumos sin fibra pueden ser bombas de azúcar.
        * **Mito: 'Quitar el gluten es la solución para todos'.** Realidad: Solo un pequeño % tiene celiaquía. El problema puede ser otro.
        * **Mito: 'Comer sin grasa es más sano'.** Realidad: Las grasas saludables son esenciales para la absorción de vitaminas y para reducir la inflamación.
    """)


def render_login_page():
    strings = APP_STRINGS[st.session_state.lang]

    # Centrar el contenido de login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title(strings['login_title'])
        st.markdown("---")

        username = st.text_input(strings['username_input'])
        full_name = st.text_input(strings['full_name_input'])
        password = st.text_input(strings['password_input'], type="password")

        login_button = st.button(strings['login_button'], use_container_width=True)
        register_button = st.button(strings['register_button'], use_container_width=True)

        if login_button:
            login_data = {
                "username": username,
                "password": password
            }
            try:
                # Conexión a la API de Render
                response = requests.post(f"{API_URL}/api/login", json=login_data)
                if response.status_code == 200:
                    st.success("¡Inicio de sesión exitoso!")
                    st.session_state.logged_in = True
                    st.session_state.token = response.json().get("token")
                    st.session_state.full_name = response.json().get("full_name")
                    st.session_state.username = username
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error(strings['invalid_credentials'])
            except requests.exceptions.ConnectionError:
                st.error(strings['connection_error'])

        if register_button:
            registration_data = {
                "username": username,
                "password": password,
                "full_name": full_name
            }
            try:
                # Conexión a la API de Render
                response = requests.post(f"{API_URL}/api/register", json=registration_data)
                if response.status_code == 201:
                    st.success(strings['registration_success'])
                else:
                    if response.content:
                        # Se maneja el JSON que viene del backend
                        error_message = response.json().get('error', 'Error desconocido')
                        st.error(f"{strings['registration_error']} Mensaje del servidor: {error_message}")
                    else:
                        st.error(f"{strings['registration_error']} El servidor no devolvió una respuesta válida.")

            except requests.exceptions.ConnectionError:
                st.error(strings['connection_error'])


def render_welcome_page():
    strings = APP_STRINGS[st.session_state.lang]

    # Centrar el contenido de la página de bienvenida
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Bienvenido a NutriGoal, el coach de la microbiota saludable")
        st.markdown("---")

        st.header("La regla de oro: ¡30 plantas distintas por semana!")
        st.write("""
            En un mundo lleno de dietas complejas, a menudo nos olvidamos de la clave de nuestra salud: la diversidad en nuestra alimentación.
            El "Reto 30" se basa en la evidencia científica de que **consumir 30 tipos de vegetales distintos a la semana** es fundamental para nutrir una microbiota intestinal sana y diversa. Una microbiota sana es la base de un sistema inmunológico fuerte, una buena digestión y una mejor salud mental.
        """)
        st.markdown(f"**¿Cómo funciona NutriGoal?**")
        st.write(
            "NutriGoal te ayuda a llevar un registro fácil de los vegetales que consumes, te muestra tu progreso y te da sugerencias para que tu dieta sea más variada.")

        if st.button("Comenzar el Reto", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


# --- Main Application Logic ---

# Inicialización de la sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'full_name' not in st.session_state:
    st.session_state.full_name = ""
if 'lang' not in st.session_state:
    st.session_state.lang = "es"
if 'page' not in st.session_state:
    st.session_state.page = "welcome"  # Initial page

if st.session_state.logged_in:
    strings = APP_STRINGS[st.session_state.lang]

    # Use st.tabs for navigation
    tab_home, tab_history, tab_achievements, tab_profile, tab_guide = st.tabs([
        f"🌿 {strings['home_button']}",
        f"📝 {strings['history_button']}",
        f"⭐ {strings['achievements_button']}",
        f"🧑‍🌾 {strings['profile_button']}",
        f"🧭 Guía"
    ])

    with tab_home:
        # Centrar el contenido de la página de inicio dentro de la pestaña
        col_main_left, col_main_center, col_main_right = st.columns([1, 4, 1])
        with col_main_center:
            render_home_content()
    with tab_history:
        col_main_left, col_main_center, col_main_right = st.columns([1, 4, 1])
        with col_main_center:
            render_history_content()
    with tab_achievements:
        col_main_left, col_main_center, col_main_right = st.columns([1, 4, 1])
        with col_main_center:
            render_achievements_content()
    with tab_profile:
        col_main_left, col_main_center, col_main_right = st.columns([1, 4, 1])
        with col_main_center:
            render_profile_content()
    with tab_guide:
        col_main_left, col_main_center, col_main_right = st.columns([1, 4, 1])
        with col_main_center:
            render_guide_content()
else:
    if st.session_state.page == "welcome":
        render_welcome_page()
    else:
        render_login_page()
