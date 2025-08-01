import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import random
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Fútbol Conectado", layout="centered")

# --- SECCIÓN 1: Consulta ganadores de cada mundial ---
st.title("🏆 Fútbol Conectado")
st.markdown("Explora datos históricos del fútbol usando Linked Open Data.")

# Diccionario de Mundiales y sus QIDs
mundiales = {
    "1982": "Q46934",
    "1986": "Q46938", 
    "1990": "Q132529",
    "1994": "Q101751",
    "1998": "Q101730",
    "2002": "Q47735",
    "2006": "Q37285",
    "2010": "Q176883",
    "2014": "Q79859",
    "2018": "Q170645"
}

# Configuración de SPARQL
wikidata_endpoint = "https://query.wikidata.org/sparql"
dbpedia_endpoint = "https://dbpedia.org/sparql"
dbpedia_es_endpoint = "https://es.dbpedia.org/sparql"
def run_query(query, endpoint):
    """Ejecuta una consulta SPARQL y devuelve los resultados"""
    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addCustomHttpHeader("User-Agent", "FutbolConectadoApp/1.0 (mailto:daniel@example.com)")
        results = sparql.query().convert()
        return results
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {str(e)}")
        return None

def obtener_campeon(q_id):
    """Obtiene el campeón de un Mundial específico"""
    query = f"""
    SELECT ?winner ?winnerLabel WHERE {{
        wd:{q_id} wdt:P1346 ?winner .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
    }}
    """
    return run_query(query, wikidata_endpoint)

def obtener_respuestas_incorrectas(q_id_excluido):
    """Obtiene campeones de otros mundiales para usar como respuestas incorrectas"""
    other_qids = [qid for year, qid in mundiales.items() if qid != q_id_excluido]
    values_clause = " ".join([f"wd:{qid}" for qid in other_qids])
    
    query = f"""
    SELECT DISTINCT ?winnerLabel WHERE {{
        VALUES ?mundial {{ {values_clause} }}
        ?mundial wdt:P1346 ?winner .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
    }}
    """
    return run_query(query, wikidata_endpoint)

# --- SECCIÓN 1: Consulta de Campeón por Año ---
st.subheader("📅 Selecciona un Mundial")

selected_year = st.selectbox("Año del Mundial", list(mundiales.keys()))
q_id = mundiales[selected_year]

if st.button("Consultar Campeón", key="consultar_campeon"):
    with st.spinner("Consultando datos..."):
        result_info = obtener_campeon(q_id)
        
        if result_info and result_info["results"]["bindings"]:
            for r in result_info["results"]["bindings"]:
                st.success(f"🏆 El campeón del Mundial {selected_year} fue: **{r['winnerLabel']['value']}**")
                st.info(f"🔗 URI: {r['winner']['value']}")
        else:
            st.error("No se pudo obtener información del campeón.")

st.divider()

# --- SECCIÓN 2: Quiz Dinámico de Mundiales ---
st.subheader("⚽ Quiz: ¿Quién ganó el Mundial?")

# Inicializar estado del quiz
if 'quiz_opciones' not in st.session_state:
    st.session_state.quiz_opciones = []
    st.session_state.quiz_respuesta_correcta = ""
    st.session_state.quiz_year = ""
    st.session_state.quiz_generado = False
    st.session_state.pregunta_respondida = False
    st.session_state.respuesta_usuario = None
    st.session_state.respuesta_correcta_final = False

def generar_nueva_pregunta():
    """Genera una nueva pregunta de quiz con un año aleatorio"""
    # Seleccionar un año aleatorio
    quiz_year = random.choice(list(mundiales.keys()))
    quiz_q_id = mundiales[quiz_year]
    
    # Obtener respuesta correcta
    correct_result = obtener_campeon(quiz_q_id)
    
    if correct_result and correct_result["results"]["bindings"]:
        correct_answer = correct_result["results"]["bindings"][0]["winnerLabel"]["value"]
        
        # Obtener respuestas incorrectas
        incorrect_result = obtener_respuestas_incorrectas(quiz_q_id)
        
        if incorrect_result and incorrect_result["results"]["bindings"]:
            # Filtrar respuestas incorrectas que no sean la correcta
            incorrect_options = [
                r["winnerLabel"]["value"] 
                for r in incorrect_result["results"]["bindings"] 
                if r["winnerLabel"]["value"] != correct_answer
            ]
            
            # Seleccionar 3 respuestas incorrectas aleatorias
            num_opciones = min(3, len(incorrect_options))
            if num_opciones > 0:
                random_incorrect = random.sample(incorrect_options, num_opciones)
                
                # Combinar opciones y barajar
                all_options = random_incorrect + [correct_answer]
                random.shuffle(all_options)
                
                # Guardar en session state
                st.session_state.quiz_opciones = all_options
                st.session_state.quiz_respuesta_correcta = correct_answer
                st.session_state.quiz_year = quiz_year
                st.session_state.quiz_generado = True
                st.session_state.pregunta_respondida = False
                st.session_state.respuesta_usuario = None
                st.session_state.respuesta_correcta_final = False
                
                return True
    return False

# Botón para generar nueva pregunta
if st.button("🎲 Generar Nueva Pregunta", key="generar_quiz"):
    with st.spinner("Generando pregunta..."):
        if generar_nueva_pregunta():
            st.success("¡Nueva pregunta generada!")
        else:
            st.error("No se pudo generar la pregunta. Inténtalo de nuevo.")

# Generar primera pregunta automáticamente si no existe
if not st.session_state.quiz_generado:
    with st.spinner("Cargando primera pregunta..."):
        generar_nueva_pregunta()

# Mostrar quiz si está generado
if st.session_state.quiz_generado and st.session_state.quiz_opciones:
    st.write(f"**¿Quién ganó la Copa Mundial de la FIFA en {st.session_state.quiz_year}?**")
    
    # Mostrar opciones solo si no se ha respondido correctamente
    if not st.session_state.respuesta_correcta_final:
        respuesta_usuario = st.radio(
            "Elige una opción:",
            st.session_state.quiz_opciones,
            key=f"quiz_respuesta_{st.session_state.quiz_year}"
        )
        
        # Botón para responder
        if st.button("✅ Responder", key="responder_quiz"):
            st.session_state.respuesta_usuario = respuesta_usuario
            st.session_state.pregunta_respondida = True
            
            # Verificar si la respuesta es correcta
            if respuesta_usuario == st.session_state.quiz_respuesta_correcta:
                st.session_state.respuesta_correcta_final = True
            
            st.rerun()
    
    # Mostrar resultado si ya se respondió
    if st.session_state.pregunta_respondida and st.session_state.respuesta_usuario:
        
        if st.session_state.respuesta_correcta_final:
            st.success(f"🎉 ¡Correcto! **{st.session_state.quiz_respuesta_correcta}** fue el campeón en {st.session_state.quiz_year}.")
            st.info("💡 Genera una nueva pregunta para seguir jugando.")
        else:
            st.error("❌ Respuesta incorrecta. ¡Inténtalo de nuevo!")
            
            # Botón para reintentar
            if st.button("🔄 Reintentar", key="reintentar_quiz"):
                st.session_state.pregunta_respondida = False
                st.session_state.respuesta_usuario = None
                st.rerun()

# Información adicional
if st.session_state.quiz_generado:
    with st.expander("📊 Información de la pregunta actual"):
        st.write(f"**Año:** {st.session_state.quiz_year}")
        st.write(f"**Respuesta correcta:** {st.session_state.quiz_respuesta_correcta}")
        st.write(f"**Opciones disponibles:** {len(st.session_state.quiz_opciones)}")

st.divider()
# --- SECCIÓN 3: Quiz de Jugadores ---
st.subheader("🔄 ¿Quién jugó en ambos equipos?")
# Diccionario con equipos y sus URIs de Wikidata
equipos_wikidata = {
    "FC Barcelona": {
        "uri": "wd:Q7156",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/Barcelona-Logo.png"
    },
    "AC Milan": {
        "uri": "wd:Q1543", 
        "logo": "https://logos-world.net/wp-content/uploads/2020/11/Milan-Logo.png"
    },
    "Real Madrid": {
        "uri": "wd:Q8682",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/Real-Madrid-Logo.png"
    },
    "Inter Milan": {
        "uri": "wd:Q631",
        "logo": "https://logos-world.net/wp-content/uploads/2021/04/FC-Internazionale-Milano-Logo.png"
    },
    "Manchester United": {
        "uri": "wd:Q18656",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/Manchester-United-logo.png"
    },
    "Juventus FC": {
        "uri": "wd:Q1422",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/Juventus-Logo.png"
    },
    "Bayern Munich": {
        "uri": "wd:Q15789",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/FC-Bayern-Munchen-Logo.png"
    },
    "Arsenal FC": {
        "uri": "wd:Q9617",
        "logo": "https://logos-world.net/wp-content/uploads/2020/05/Arsenal-Logo.png"
    },
    "Chelsea FC": {
        "uri": "wd:Q9616",
        "logo": "https://logos-world.net/wp-content/uploads/2020/05/Chelsea-Logo.png"
    },
    "Atletico de Madrid": {
        "uri": "wd:Q8701",
        "logo": "https://logos-world.net/wp-content/uploads/2020/06/atletico-madrid-Logo.png"
    },
    "Borussia Dortmund":{
        "uri": "Q41420",
        "logo": "https://logos-world.net/wp-content/uploads/2020/11/Borussia-Dortmund-Logo.png"
    }
}

def obtener_dos_equipos_distintos(equipos_dict):
    """Devuelve dos equipos distintos al azar"""
    return random.sample(list(equipos_dict.items()), 2)

def construir_query_jugador(equipo1_uri, equipo2_uri):
    """Devuelve una query SPARQL con dos equipos incluyendo información detallada e imagen"""
    return f"""
    SELECT DISTINCT ?jugadorLabel ?imagen ?equipo1Start ?equipo1End ?equipo1Matches ?equipo1Goals
                    ?equipo2Start ?equipo2End ?equipo2Matches ?equipo2Goals WHERE {{
        ?jugador wdt:P31 wd:Q5;         # humano
                 wdt:P106 wd:Q937857;   # futbolista
                 wdt:P54 {equipo1_uri}, {equipo2_uri}. # jugó en ambos clubes
        
        # Imagen del jugador (opcional)
        OPTIONAL {{ ?jugador wdt:P18 ?imagen . }}
        
        # Información del primer equipo
        OPTIONAL {{
            ?jugador p:P54 ?stmt1 .
            ?stmt1 ps:P54 {equipo1_uri} .
            OPTIONAL {{ ?stmt1 pq:P580 ?equipo1Start . }}
            OPTIONAL {{ ?stmt1 pq:P582 ?equipo1End . }}
            OPTIONAL {{ ?stmt1 pq:P1350 ?equipo1Matches . }}
            OPTIONAL {{ ?stmt1 pq:P1351 ?equipo1Goals . }}
        }}
        
        # Información del segundo equipo
        OPTIONAL {{
            ?jugador p:P54 ?stmt2 .
            ?stmt2 ps:P54 {equipo2_uri} .
            OPTIONAL {{ ?stmt2 pq:P580 ?equipo2Start . }}
            OPTIONAL {{ ?stmt2 pq:P582 ?equipo2End . }}
            OPTIONAL {{ ?stmt2 pq:P1350 ?equipo2Matches . }}
            OPTIONAL {{ ?stmt2 pq:P1351 ?equipo2Goals . }}
        }}
        
        FILTER({equipo1_uri} != {equipo2_uri})
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
    }}
    """

def buscar_jugadores_en_ambos_clubes():
    """Busca jugadores que hayan jugado en dos clubes diferentes con información detallada"""
    equipo1, equipo2 = obtener_dos_equipos_distintos(equipos_wikidata)
    nombre1 = equipo1[0]
    info1 = equipo1[1]
    nombre2 = equipo2[0]
    info2 = equipo2[1]

    query = construir_query_jugador(info1["uri"], info2["uri"])
    resultados = run_query(query, wikidata_endpoint)

    jugadores_detallados = {}
    if resultados and resultados["results"]["bindings"]:
        for r in resultados["results"]["bindings"]:
            nombre_jugador = r["jugadorLabel"]["value"]
            
            if nombre_jugador not in jugadores_detallados:
                jugadores_detallados[nombre_jugador] = {
                    "imagen": None,
                    "equipo1": {"start": None, "end": None, "matches": None, "goals": None},
                    "equipo2": {"start": None, "end": None, "matches": None, "goals": None}
                }
            
            # Imagen del jugador
            if "imagen" in r:
                jugadores_detallados[nombre_jugador]["imagen"] = r["imagen"]["value"]
            
            # Información del primer equipo
            if "equipo1Start" in r:
                jugadores_detallados[nombre_jugador]["equipo1"]["start"] = r["equipo1Start"]["value"][:4] if r["equipo1Start"]["value"] else None
            if "equipo1End" in r:
                jugadores_detallados[nombre_jugador]["equipo1"]["end"] = r["equipo1End"]["value"][:4] if r["equipo1End"]["value"] else None
            if "equipo1Matches" in r:
                jugadores_detallados[nombre_jugador]["equipo1"]["matches"] = r["equipo1Matches"]["value"]
            if "equipo1Goals" in r:
                jugadores_detallados[nombre_jugador]["equipo1"]["goals"] = r["equipo1Goals"]["value"]
                
            # Información del segundo equipo
            if "equipo2Start" in r:
                jugadores_detallados[nombre_jugador]["equipo2"]["start"] = r["equipo2Start"]["value"][:4] if r["equipo2Start"]["value"] else None
            if "equipo2End" in r:
                jugadores_detallados[nombre_jugador]["equipo2"]["end"] = r["equipo2End"]["value"][:4] if r["equipo2End"]["value"] else None
            if "equipo2Matches" in r:
                jugadores_detallados[nombre_jugador]["equipo2"]["matches"] = r["equipo2Matches"]["value"]
            if "equipo2Goals" in r:
                jugadores_detallados[nombre_jugador]["equipo2"]["goals"] = r["equipo2Goals"]["value"]

    return nombre1, info1, nombre2, info2, jugadores_detallados

def formatear_periodo(start, end):
    """Formatea el período de tiempo"""
    if start and end:
        return f"{start}-{end}"
    elif start:
        return f"{start}-?"
    elif end:
        return f"?-{end}"
    else:
        return "Período no disponible"

def formatear_estadisticas(matches, goals):
    """Formatea las estadísticas de partidos y goles"""
    stats = []
    if matches:
        stats.append(f"{matches} partidos")
    if goals:
        stats.append(f"{goals} goles")
    return " | ".join(stats) if stats else "Estadísticas no disponibles"

def mostrar_info_jugador(nombre_jugador, info_jugador, nombre_equipo1, nombre_equipo2):
    """Muestra la información detallada de un jugador con imagen"""
    # Crear dos columnas: información a la izquierda, imagen a la derecha
    col_info, col_imagen = st.columns([2, 1])
    
    with col_info:
        st.markdown(f"**{nombre_jugador}**")
        
        # Información equipo 1
        periodo1 = formatear_periodo(info_jugador["equipo1"]["start"], info_jugador["equipo1"]["end"])
        stats1 = formatear_estadisticas(info_jugador["equipo1"]["matches"], info_jugador["equipo1"]["goals"])
        st.markdown(f"  • **{nombre_equipo1}**: {periodo1}")
        if stats1 != "Estadísticas no disponibles":
            st.markdown(f"    └ {stats1}")
        
        # Información equipo 2
        periodo2 = formatear_periodo(info_jugador["equipo2"]["start"], info_jugador["equipo2"]["end"])
        stats2 = formatear_estadisticas(info_jugador["equipo2"]["matches"], info_jugador["equipo2"]["goals"])
        st.markdown(f"  • **{nombre_equipo2}**: {periodo2}")
        if stats2 != "Estadísticas no disponibles":
            st.markdown(f"    └ {stats2}")
    
    with col_imagen:
        if info_jugador["imagen"]:
            try:
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: center; align-items: center; height: 150px;'>
                        <img src='{info_jugador["imagen"]}' width='120' style='border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);' />
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except:
                st.markdown(
                    """
                    <div style='display: flex; justify-content: center; align-items: center; height: 150px; background-color: #f0f0f0; border-radius: 10px;'>
                        <span style='font-size: 40px;'>👤</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style='display: flex; justify-content: center; align-items: center; height: 150px; background-color: #f0f0f0; border-radius: 10px;'>
                    <span style='font-size: 40px;'>👤</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("---")

def validar_respuesta_jugador(nombre_ingresado, jugadores_detallados):
    """Valida si el nombre ingresado está en la lista de respuestas correctas"""
    if not nombre_ingresado or not jugadores_detallados:
        return False, None
    
    nombre_normalizado = nombre_ingresado.strip().lower()
    
    for jugador_correcto in jugadores_detallados.keys():
        if nombre_normalizado in jugador_correcto.lower() or jugador_correcto.lower() in nombre_normalizado:
            return True, jugador_correcto
    
    return False, None

# Inicializar estado del juego de jugadores
if "club1" not in st.session_state:
    st.session_state.club1 = ""
    st.session_state.club1_info = {}
    st.session_state.club2 = ""
    st.session_state.club2_info = {}
    st.session_state.jugadores_en_comun = []
    st.session_state.jugadores_encontrados = []
    st.session_state.intentos_jugador = 0
    st.session_state.respuesta_correcta_jugador = False

def generar_nueva_pregunta_jugador():
    """Genera una nueva combinación de clubes"""
    nombre1, info1, nombre2, info2, jugadores_detallados = buscar_jugadores_en_ambos_clubes()
    st.session_state.club1 = nombre1
    st.session_state.club1_info = info1
    st.session_state.club2 = nombre2
    st.session_state.club2_info = info2
    st.session_state.jugadores_en_comun = jugadores_detallados
    st.session_state.jugadores_encontrados = []
    st.session_state.intentos_jugador = 0
    st.session_state.respuesta_correcta_jugador = False

# Generar primera combinación automáticamente
if not st.session_state.club1 or not st.session_state.club2:
    with st.spinner("Buscando primera combinación de clubes..."):
        generar_nueva_pregunta_jugador()

# Mostrar interfaz del juego
if st.session_state.club1 and st.session_state.club2:
    # Mostrar logos y nombres de los equipos
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: center; align-items: center; height: 170px;'>
                    <img src='{st.session_state.club1_info["logo"]}' width='150' style='display: block; margin: auto;' />
                </div>
                """,
                unsafe_allow_html=True
            )
        except:
            st.write("🏆")  # Emoji como fallback si la imagen no carga
        st.markdown(f"<h4 style='text-align: center;'>{st.session_state.club1}</h4>", unsafe_allow_html=True)

    with col2:
        try:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: center; align-items: center; height: 170px;'>
                    <img src='{st.session_state.club2_info["logo"]}' width='150' style='display: block; margin: auto;' />
                </div>
                """,
                unsafe_allow_html=True
            )
        except:
            st.write("🏆")  # Emoji como fallback si la imagen no carga
        st.markdown(f"<h4 style='text-align: center;'>{st.session_state.club2}</h4>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**❓ ¿Qué jugador ha jugado en ambos equipos?**")
    
    # Campo de texto para respuesta
    if not st.session_state.respuesta_correcta_jugador:
        nombre_jugador = st.text_input(
            "Ingresa el nombre del jugador:",
            key=f"input_jugador_{st.session_state.club1}_{st.session_state.club2}",
            placeholder="Ej: Ronaldinho, David Beckham, etc."
        )
        
        if st.button("✅ Verificar respuesta", key="verificar_jugador"):
            if nombre_jugador:
                st.session_state.intentos_jugador += 1
                es_correcto, jugador_encontrado = validar_respuesta_jugador(nombre_jugador, st.session_state.jugadores_en_comun)
                
                if es_correcto:
                    st.success(f"🎉 ¡Correcto! **{jugador_encontrado}** jugó en ambos equipos.")
                    st.session_state.jugadores_encontrados.append(jugador_encontrado)
                    st.session_state.respuesta_correcta_jugador = True
                    
                    # Mostrar información detallada del jugador encontrado
                    st.markdown("### 📊 Información detallada:")
                    mostrar_info_jugador(
                        jugador_encontrado, 
                        st.session_state.jugadores_en_comun[jugador_encontrado],
                        st.session_state.club1,
                        st.session_state.club2
                    )
                    
                    # Mostrar otros jugadores en un expander (desplegable)
                    otros_jugadores = {k: v for k, v in st.session_state.jugadores_en_comun.items() if k != jugador_encontrado}
                    if otros_jugadores:
                        with st.expander(f"💡 Ver otros jugadores que también jugaron en ambos equipos ({len(otros_jugadores)} más)"):
                            for nombre, info in otros_jugadores.items():
                                mostrar_info_jugador(nombre, info, st.session_state.club1, st.session_state.club2)
                else:
                    st.error("❌ Respuesta incorrecta. ¡Inténtalo de nuevo!")
            else:
                st.warning("⚠️ Por favor, ingresa un nombre.")
    
    # Mostrar estadísticas del intento actual
    if st.session_state.intentos_jugador > 0:
        if st.session_state.respuesta_correcta_jugador:
            st.success(f"🏆 ¡Resuelto en {st.session_state.intentos_jugador} intento(s)!")
        else:
            st.info(f"📊 Intentos realizados: {st.session_state.intentos_jugador}")
    
    # Verificar si no hay jugadores en común
    if not st.session_state.jugadores_en_comun:
        st.warning("⚠️ No se encontraron jugadores que hayan jugado en ambos equipos. Genera una nueva combinación.")

# Botón para nueva combinación
if st.button("🔁 Probar con otros clubes", key="nuevos_clubes"):
    with st.spinner("Buscando nueva combinación..."):
        generar_nueva_pregunta_jugador()
        st.rerun()

st.divider()

# --- SECCIÓN 4: Storytelling Histórico ---
st.subheader("📖 Storytelling: Cuando el Fútbol es más que un Juego")

# --- [NUEVO] Uso de pestañas para organizar las historias ---
tab1, tab2, tab3 = st.tabs([
    "Argentina vs. Inglaterra (1986)",
    "Drogba y la Paz en Costa de Marfil",
    "Chile y el 'Partido Fantasma' (1973)"
])

with tab1:
    st.markdown("#### Un Partido, Dos Naciones y la Historia")
    
    with st.spinner("Cargando historia de 1986..."):
        # 1. Contexto Guerra
        falklands_query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        SELECT ?abstract WHERE {
            dbr:Falklands_War dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es")
        } LIMIT 1
        """
        falklands_result = run_query(falklands_query, endpoint=dbpedia_endpoint)
        if falklands_result and falklands_result["results"]["bindings"]:
            st.info(f"**Contexto - La Guerra de las Malvinas (1982):**\n\n" + falklands_result["results"]["bindings"][0]["abstract"]["value"])

        # 2. Contexto Partido
        match_abstract_query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        SELECT ?abstract WHERE {
          <http://es.dbpedia.org/resource/Argentina_vs._Inglaterra_(1986)> dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es")
        } LIMIT 1
        """
        match_abstract_result = run_query(match_abstract_query, endpoint="https://es.dbpedia.org/sparql")
        if match_abstract_result and match_abstract_result["results"]["bindings"]:
            st.success("**El Partido - Una Revancha Simbólica:**\n\n" + match_abstract_result["results"]["bindings"][0]["abstract"]["value"])

        # 3. Datos de los goles (Wikidata)
        story_query_1986 = """
        SELECT ?item ?itemLabel ?itemDescription ?image WHERE {
          VALUES ?item { wd:Q622495 wd:Q1363790 } # Hand of God, Goal of the Century
          OPTIONAL { ?item schema:description ?itemDescription . FILTER(LANG(?itemDescription) = "es") }
          OPTIONAL { ?item wdt:P18 ?image. }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
        }
        """
        story_results_1986 = run_query(story_query_1986, wikidata_endpoint)
        
        if story_results_1986 and story_results_1986["results"]["bindings"]:
            story_data_1986 = {r['item']['value'].split('/')[-1]: r for r in story_results_1986["results"]["bindings"]}
            
            st.markdown("**Los Momentos Inolvidables:**")
            col1, col2 = st.columns(2)
            
            # La Mano de Dios
            if "Q622495" in story_data_1986:
                with col1:
                    st.markdown("##### 🖐️ 'La Mano de Dios'")
                    st.write(story_data_1986["Q622495"].get("itemDescription", {}).get("value"))
                    if "image" in story_data_1986["Q622495"]:
                        st.image(story_data_1986["Q622495"]["image"]["value"], caption="https://www.youtube.com/watch?v=p-QOLsypsnQ")
            
            # El Gol del Siglo
            if "Q1363790" in story_data_1986:
                with col2:
                    st.markdown("##### 🏃 'El Gol del Siglo'")
                    st.write(story_data_1986["Q1363790"].get("itemDescription", {}).get("value"))
                    if "image" in story_data_1986["Q1363790"]:
                        st.image(story_data_1986["Q1363790"]["image"]["value"], caption="https://www.youtube.com/watch?v=IoA0YaCA2Yk")
        else:
            st.error("No se pudieron cargar los detalles de los goles desde Wikidata.")
        st.markdown("Puedes leer más sobre este partido en [Wikipedia](https://es.wikipedia.org/wiki/Argentina_vs._Inglaterra_(1986)).")

with tab2:
    st.markdown("#### El Gol que Detuvo una Guerra Civil")

    with st.spinner("Cargando historia de Drogba..."):
        # 1. Contexto Guerra Civil
        civil_war_query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        SELECT ?abstract WHERE {
            dbr:First_Ivorian_Civil_War dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es")
        } LIMIT 1
        """
        civil_war_result = run_query(civil_war_query, endpoint=dbpedia_endpoint)
        if civil_war_result and civil_war_result["results"]["bindings"]:
            st.info(f"**Contexto - La Primera Guerra Civil de Costa de Marfil:**\n\n" + civil_war_result["results"]["bindings"][0]["abstract"]["value"])
        else:
            st.warning("No se pudo cargar el contexto histórico desde DBpedia.")

        # 2. Datos de Drogba y el partido simbólico en Bouaké
        drogba_story_query = """
        SELECT ?item ?itemLabel ?image ?date WHERE {
          VALUES ?item { wd:Q48892 wd:Q4610331 } # Drogba, Partido en Bouaké
          OPTIONAL { ?item wdt:P18 ?image. }
          OPTIONAL { ?item wdt:P585 ?date. }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
        }
        """
        drogba_story_results = run_query(drogba_story_query, wikidata_endpoint)
        drogba_image = None
        bouake_match_date = "2007"
        if drogba_story_results and drogba_story_results["results"]["bindings"]:
            for r in drogba_story_results["results"]["bindings"]:
                if "Q48892" in r["item"]["value"] and "image" in r:
                    drogba_image = r["image"]["value"]
                if "Q4610331" in r["item"]["value"] and "date" in r:
                    bouake_match_date = pd.to_datetime(r["date"]["value"]).strftime('%d de %B de %Y')
        
        # 3. Narrativa
        st.success("**El Llamado a la Paz:**\n\nTras clasificar a Costa de Marfil para su primer Mundial en 2006, el capitán Didier Drogba, en lugar de celebrar, se arrodilló frente a las cámaras y suplicó a sus compatriotas que depusieran las armas. Su apasionado discurso tuvo un impacto inmediato, ayudando a catalizar un alto el fuego.")
        
        col1, col2 = st.columns([1, 2])
        if drogba_image:
            with col1:
                st.image(drogba_image, caption="Didier Drogba, líder dentro y fuera del campo. \n Discurso: https://www.youtube.com/watch?v=KAW7DF1Ufek")

        with col2:
             st.markdown("**El Partido de la Unificación:**")
             st.write(f"Pero el gesto más poderoso llegaría después. Drogba insistió en que el partido de clasificación para la Copa Africana de Naciones contra Madagascar, a jugarse el **{bouake_match_date}**, no se celebrara en la capital, sino en Bouaké, el corazón del territorio rebelde. El gobierno aceptó.")
             st.write("Jugar ese partido en Bouaké fue un acto simbólico de unidad sin precedentes. Demostró que el fútbol podía unir a una nación dividida, logrando lo que la política no había podido.")
        
        st.markdown("---")
        st.markdown("Este episodio es recordado como uno de los mayores ejemplos del poder del deporte para inspirar la paz y la reconciliación. Puedes leer más al respecto en [este artículo de la BBC](https://www.bbc.com/sport/football/52251219).")

with tab3:
    st.markdown("#### El Estadio de la Memoria y el 'Partido Fantasma'")
    with st.spinner("Cargando historia de Chile '73..."):
        # 1. Contexto Golpe de Estado
        coup_query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        SELECT ?abstract WHERE {
            <dbr:1973_Chilean_coup_d'état> dbo:abstract ?abstract .
            FILTER(LANG(?abstract) = "es")
        } LIMIT 1
        """
        coup_result = run_query(coup_query, endpoint=dbpedia_endpoint)
        if coup_result and coup_result["results"]["bindings"]:
            st.info(f"**Contexto - Golpe de Estado en Chile (1973):**\n\n" + coup_result["results"]["bindings"][0]["abstract"]["value"])

        # 2. Datos del Estadio y del Partido
        chile_story_query = """
        SELECT ?item ?itemLabel ?image ?date WHERE {
          VALUES ?item { wd:Q856670 wd:Q1987588 } # Estadio Nacional, Play-off match
          OPTIONAL { ?item wdt:P18 ?image. }
          OPTIONAL { ?item wdt:P585 ?date. }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
        }
        """
        chile_story_results = run_query(chile_story_query, wikidata_endpoint)
        stadium_image, match_date = None, "Noviembre de 1973"
        if chile_story_results and chile_story_results["results"]["bindings"]:
            for r in chile_story_results["results"]["bindings"]:
                if "Q856670" in r["item"]["value"] and "image" in r: stadium_image = r["image"]["value"]
                if "Q1987588" in r["item"]["value"] and "date" in r: match_date = pd.to_datetime(r["date"]["value"]).strftime('%d de %B de %Y')
        
        # 3. Narrativa
        st.error("**El Estadio como Centro de Detención:** Tras el golpe, el Estadio Nacional fue utilizado como el mayor centro de detención, tortura y ejecución de prisioneros políticos de la dictadura de Pinochet.")
        
        col1, col2 = st.columns([1, 2])
        if stadium_image:
            with col1: st.image(stadium_image, caption="Bombardeo de *La Moneda* en 1973.")

        with col2:
            st.markdown(f"**El Partido de la Vergüenza ({match_date}):**")
            st.write("Pese a las denuncias internacionales, la FIFA obligó a jugar el repechaje para el Mundial de 1974 contra la URSS en ese mismo estadio. La Unión Soviética se negó a presentarse en un 'campo de concentración'.")
            st.write("El equipo chileno salió a la cancha, y en un acto surrealista, marcó un gol sin rival ([ver video](https://www.youtube.com/watch?v=KvMi0cXaZDI)). Chile clasificó al Mundial, pero el partido quedó en la historia como un símbolo de la instrumentalización del fútbol por un régimen represivo y la tensión geopolítica de la Guerra Fría.")

        st.success("Hoy, partes del estadio son un memorial para recordar a las víctimas y asegurar que la historia no se repita, mezclando para siempre el deporte con la lucha por los derechos humanos.")


st.divider()

st.info("💡 **Datos obtenidos de Wikidata y DBpedia** - Dos pilares de la Web de Datos Enlazados.")
st.caption("🔄  Los datos se consultan en tiempo real y reflejan la información más actual de estas bases de conocimiento.")