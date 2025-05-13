import os
import logging
import dotenv
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_caching import Cache
from utils.api_client import get_tvl_data
from utils.openai_client import analyze_on_chain_data

# Cargar variables de entorno desde el archivo .env
dotenv.load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Inicializar aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configurar caché
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutos
}
app.config.from_mapping(cache_config)
cache = Cache(app)

@app.route('/')
def index():
    """Página principal"""
    openai_api_key = session.get('openai_api_key', '')
    has_api_key = bool(openai_api_key)
    return render_template('index.html', has_api_key=has_api_key)

@app.route('/api-settings', methods=['GET', 'POST'])
def api_settings():
    """Página de configuración de clave API"""
    if request.method == 'POST':
        openai_api_key = request.form.get('openai_api_key')
        session['openai_api_key'] = openai_api_key
        flash('Clave API actualizada con éxito', 'success')
        return redirect(url_for('index'))
    
    openai_api_key = session.get('openai_api_key', '')
    return render_template('api_settings.html', openai_api_key=openai_api_key)

@app.route('/tvl')
def tvl():
    """Página de Valor Total Bloqueado (TVL)"""
    return render_template('tvl.html')

@app.route('/protocols')
def protocols():
    """Página de Protocolos DeFi ordenados por TVL"""
    return render_template('protocols.html')

@app.route('/chains')
def chains():
    """Página de Cadenas de Blockchain ordenadas por TVL"""
    return render_template('chains.html')

@app.route('/api/tvl')
@cache.cached(timeout=300)
def api_tvl():
    """Endpoint API para datos TVL"""
    try:
        data = get_tvl_data()
        
        # Si hay un error en los datos, devolver respuesta de error
        if "error" in data:
            return jsonify(data), 500
            
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error al obtener datos TVL: {str(e)}")
        return jsonify({
            "error": f"Error al obtener datos TVL: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/protocols')
@cache.cached(timeout=300)
def api_protocols():
    """Endpoint API para datos de protocolos (top por TVL)"""
    try:
        # Usar la API de DefiLlama para obtener protocolos ordenados por TVL
        response = requests.get("https://api.llama.fi/protocols")
        response.raise_for_status()
        protocols = response.json()
        
        # Verificar datos válidos
        if not protocols or not isinstance(protocols, list):
            return jsonify({
                "error": "Formato de datos de protocolo no válido",
                "timestamp": datetime.now().isoformat()
            }), 500
            
        # Filtrar protocolos con TVL válido
        valid_protocols = [p for p in protocols if p.get('tvl') is not None]
        
        # Ordenar protocolos por TVL y obtener top 20
        top_protocols = sorted(valid_protocols, key=lambda x: float(x.get('tvl', 0)), reverse=True)[:20]
        
        # Formatear datos para frontend
        formatted_data = {
            "protocols": [
                {
                    "name": protocol.get('name', 'Unknown'),
                    "tvl": float(protocol.get('tvl', 0)),
                    "chain": protocol.get('chain', 'Unknown'),
                    "category": protocol.get('category', 'Unknown'),
                    "change_1d": float(protocol.get('change_1d', 0)) if protocol.get('change_1d') is not None else 0,
                    "change_7d": float(protocol.get('change_7d', 0)) if protocol.get('change_7d') is not None else 0
                } for protocol in top_protocols
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(formatted_data)
    except Exception as e:
        logging.error(f"Error al obtener datos de protocolos: {str(e)}")
        return jsonify({
            "error": f"Error al obtener datos de protocolos: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chains')
@cache.cached(timeout=300)
def api_chains():
    """Endpoint API para datos de cadenas blockchain por TVL"""
    try:
        # Usar la API de DefiLlama para obtener datos de cadenas
        response = requests.get("https://api.llama.fi/chains")
        response.raise_for_status()
        chains = response.json()
        
        # Verificar datos válidos
        if not chains or not isinstance(chains, list):
            return jsonify({
                "error": "Formato de datos de cadenas no válido",
                "timestamp": datetime.now().isoformat()
            }), 500
            
        # Filtrar cadenas con TVL válido
        valid_chains = [c for c in chains if c.get('tvl') is not None]
        
        # Ordenar cadenas por TVL y obtener top 15
        top_chains = sorted(valid_chains, key=lambda x: float(x.get('tvl', 0)), reverse=True)[:15]
        
        # Formatear datos para frontend
        formatted_chains = []
        for chain in top_chains:
            formatted_chains.append({
                "name": chain.get('name', 'Unknown'),
                "tvl": float(chain.get('tvl', 0)),
                "tokenSymbol": chain.get('tokenSymbol', '-')
            })
            
        formatted_data = {
            "chains": formatted_chains,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(formatted_data)
    except Exception as e:
        logging.error(f"Error al obtener datos de cadenas: {str(e)}")
        return jsonify({
            "error": f"Error al obtener datos de cadenas: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Endpoint API para análisis OpenAI de datos on-chain"""
    openai_api_key = session.get('openai_api_key')
    if not openai_api_key:
        return jsonify({"error": "Clave API de OpenAI no configurada. Por favor configúrala en Configuración de API."}), 400
    
    try:
        if not request.is_json:
            return jsonify({"error": "Se esperaba contenido JSON"}), 400
            
        data_type = request.json.get('dataType') if request.json else None
        data = request.json.get('data') if request.json else None
        
        if not data_type or not data:
            return jsonify({"error": "Falta el tipo de datos o los datos"}), 400
        
        analysis = analyze_on_chain_data(data_type, data, openai_api_key)
        return jsonify({"analysis": analysis})
    except Exception as e:
        logging.error(f"Error al analizar datos: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
