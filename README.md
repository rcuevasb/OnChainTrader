# OnChainTrader — Análisis Inteligente de Trading On-Chain 📊🤖

OnChainTrader es una herramienta web asistida por IA para analizar datos on-chain y generar recomendaciones de trading. Está desarrollada en Python utilizando Flask y OpenAI, con persistencia en PostgreSQL y soporte para scraping y análisis de contenido.

## ⚙️ Funcionalidades principales

- 📈 Análisis de datos on-chain
- 🤖 Generación de insights con OpenAI
- 🧠 Almacenamiento estructurado en PostgreSQL vía SQLAlchemy
- 📦 API web con Flask y caché integrado
- 📰 Procesamiento de textos web con Trafilatura

## 🛠️ Tecnologías utilizadas

- **Lenguaje:** Python 3.11+
- **Framework Web:** Flask
- **Base de datos:** PostgreSQL (vía SQLAlchemy)
- **IA / NLP:** OpenAI
- **Scraping:** Trafilatura, Requests
- **Otros:** Gunicorn, Flask-Caching, python-dotenv

## 🚀 Instalación

```bash
git clone https://github.com/tu-usuario/OnChainTrader.git
cd OnChainTrader
pip install -r requirements.txt  # o usar poetry/uv según tu entorno
```

Configura el archivo `.env` con tus claves necesarias (OpenAI, base de datos, etc.).

## ▶️ Ejecutar el servidor

```bash
python app.py
# o usando Gunicorn:
gunicorn -w 4 app:app
```

## 📁 Archivos importantes

- `app.py` → Servidor principal de Flask
- `main.py` → Lógica principal y flujo de ejecución
- `.env` → Variables sensibles y de configuración
- `pyproject.toml` → Dependencias y metadatos del proyecto

## 📄 Licencia

MIT © 2025 OnChainTrader

---

> Esta app es ideal para traders, analistas o desarrolladores que buscan aprovechar IA y datos blockchain para tomar decisiones informadas.
