import sys
import os
import io
import pandas as pd
from flask import Flask, request, jsonify, send_file
from core.algo import generer_planning, conversions_par_equipe

# Ajout du dossier racine au PYTHONPATH pour permettre l'import de 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration pour éviter le tri alphabétique des clés JSON (Supporte anciennes et nouvelles versions de Flask)
app.config['JSON_SORT_KEYS'] = False
app.json.sort_keys = False


@app.route("/")
def read_index():
    """ Sert le fichier index.html à la racine. """
    return app.send_static_file('index.html')


@app.route("/api/generate", methods=['POST'])
def generate_planning_route():
    """
    Génère le planning et le retourne au format JSON.
    Attends un JSON avec 'teams' et 'ateliers'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Données manquantes"}), 400

    teams = [t.strip() for t in data.get('teams', []) if t.strip()]
    ateliers = [a.strip() for a in data.get('ateliers', []) if a.strip()]

    if not teams or not ateliers:
        return jsonify({"detail": "Les listes d'équipes et d'ateliers ne peuvent pas être vides."}), 400

    try:
        df_resultat = generer_planning(ateliers, teams)
        # Conversion du DataFrame en dictionnaire (records) pour JSON
        result = df_resultat.fillna("").to_dict(orient="records")
        return jsonify(result)
    except Exception as e:
        return jsonify({"detail": f"Erreur lors de la génération : {str(e)}"}), 500


@app.route("/api/export/csv", methods=['POST'])
def export_csv():
    """
    Génère le planning global et le retourne en CSV.
    """
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Données manquantes"}), 400

    teams = [t.strip() for t in data.get('teams', []) if t.strip()]
    ateliers = [a.strip() for a in data.get('ateliers', []) if a.strip()]

    if not teams or not ateliers:
        return jsonify({"detail": "Listes vides."}), 400

    try:
        df = generer_planning(ateliers, teams)
        # Encodage en bytes pour send_file
        output = io.BytesIO()
        df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
        output.seek(0)
        
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="planning_tournoi.csv"
        )
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@app.route("/api/export/xlsx", methods=['POST'])
def export_excel():
    """
    Génère le planning par équipe et le retourne en Excel (multi-onglets).
    """
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Données manquantes"}), 400

    teams = [t.strip() for t in data.get('teams', []) if t.strip()]
    ateliers = [a.strip() for a in data.get('ateliers', []) if a.strip()]

    if not teams or not ateliers:
        return jsonify({"detail": "Listes vides."}), 400

    try:
        df = generer_planning(ateliers, teams)
        plannings = conversions_par_equipe(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for equipe, df_eq in plannings.items():
                sheet_name = equipe[:30].replace(":", "").replace("/", "")
                df_eq.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name="plannings_equipes.xlsx"
        )
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


if __name__ == '__main__':
    # Mode développement
    app.run(debug=True, port=8000)
