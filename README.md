# 🏆 Fútbol Conectado

**Fútbol Conectado** es una aplicación interactiva desarrollada con [Streamlit](https://streamlit.io/) que explora datos históricos del fútbol a través de consultas en tiempo real a **Wikidata** y **DBpedia**, dos de las principales fuentes de *Linked Open Data* (LOD).
A través de visualizaciones, preguntas tipo quiz y storytelling, los usuarios pueden aprender sobre mundiales, jugadores legendarios, clubes famosos y eventos donde el fútbol se entrelazó con la historia.

---

## 🚀 Características

### ⚽ Consultas de Campeones del Mundo

* Selecciona un año de Mundial y descubre qué país fue el campeón.
* Accede a la URI de Wikidata asociada para ver más datos abiertos.

### 🎯 Quiz de Campeones

* Juego interactivo: adivina qué selección ganó en cada edición del Mundial FIFA.
* Las respuestas se extraen dinámicamente desde Wikidata.

### 🔄 Jugadores que jugaron en dos clubes

* Elige dos clubes (o deja que el sistema los elija al azar).
* Adivina qué jugador profesional ha jugado en ambos equipos.
* Visualiza estadísticas, períodos de juego e imágenes cuando estén disponibles.

### 📖 Storytelling con Datos Abiertos

Explora relatos históricos que mezclan política, cultura y fútbol, como:

* **Argentina vs. Inglaterra (1986)** y la Guerra de las Malvinas.
* **Didier Drogba** y su llamado a la paz en Costa de Marfil.
* **El “Partido Fantasma” de Chile (1973)** y el Estadio Nacional como campo de detención.

---

## 🌐 Tecnologías Utilizadas

* **[Streamlit](https://streamlit.io/)** – Framework para aplicaciones web interactivas en Python.
* **[Wikidata](https://www.wikidata.org/)** – Base de conocimiento estructurada enlazada.
* **[DBpedia](https://dbpedia.org/)** – Extractor de datos estructurados desde Wikipedia.
* **[SPARQLWrapper](https://rdflib.github.io/sparqlwrapper/)** – Cliente Python para consultas SPARQL.
* **Pandas** – Para procesamiento y análisis de datos.

---

## 📦 Instalación y Uso

### 1. Clona el repositorio

```bash
git clone [https://github.com/DanF57/Aplicacion_SPARQL.git](https://github.com/DanF57/Aplicacion_SPARQL/)
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecuta la aplicación

```bash
streamlit run app.py
```
## 🎓 Público Objetivo

* Entusiastas del fútbol y la historia.
* Estudiantes o desarrolladores interesados en Web Semántica, SPARQL y conocimiento abierto.

¿Quieres que también genere un `requirements.txt` con las dependencias necesarias para este proyecto?
