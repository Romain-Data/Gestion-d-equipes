import sys
import os

# Ajout du dossier racine au PYTHONPATH pour permettre l'import de 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse, StreamingResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from typing import List, Dict, Any  # noqa: E402
import io  # noqa: E402
import pandas as pd  # noqa: E402

from core.algo import generer_planning, conversions_par_equipe  # noqa: E402

app = FastAPI(title="Générateur de Tournoi API")

# Montage des fichiers statiques pour le frontend
app.mount("/static", StaticFiles(directory="web/static"), name="static")


class PlanningRequest(BaseModel):
    """ Modèle Pydantic pour la requête de génération. """
    teams: List[str]
    ateliers: List[str]


@app.get("/")
async def read_index():
    """ Sert le fichier index.html à la racine. """
    return FileResponse("web/static/index.html")


@app.post("/api/generate")
async def generate_planning(request: PlanningRequest) -> List[Dict[str, Any]]:
    """
    Génère le planning et le retourne au format JSON.

    Args:
        request (PlanningRequest): Listes des équipes et des ateliers.

    Returns:
        List[Dict[str, Any]]: La liste des enregistrements (lignes du tableau).
    """
    teams = [t.strip() for t in request.teams if t.strip()]
    ateliers = [a.strip() for a in request.ateliers if a.strip()]

    if not teams or not ateliers:
        raise HTTPException(status_code=400, detail="Les listes d'équipes et d'ateliers ne peuvent pas être vides.")

    try:
        df_resultat = generer_planning(ateliers, teams)
        # Conversion du DataFrame en dictionnaire (records) pour JSON
        # replace({float('nan'): None}) permet de gérer les valeurs NaN proprement en JSON
        result = df_resultat.fillna("").to_dict(orient="records")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")


@app.post("/api/export/csv")
async def export_csv(request: PlanningRequest):
    """
    Génère le planning global et le retourne en CSV.
    """
    teams = [t.strip() for t in request.teams if t.strip()]
    ateliers = [a.strip() for a in request.ateliers if a.strip()]

    if not teams or not ateliers:
        raise HTTPException(status_code=400, detail="Listes vides.")

    try:
        df = generer_planning(ateliers, teams)
        stream = io.StringIO()
        df.to_csv(stream, index=False, sep=';', encoding='utf-8-sig')
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=planning_tournoi.csv"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/xlsx")
async def export_excel(request: PlanningRequest):
    """
    Génère le planning par équipe et le retourne en Excel (multi-onglets).
    """
    teams = [t.strip() for t in request.teams if t.strip()]
    ateliers = [a.strip() for a in request.ateliers if a.strip()]

    if not teams or not ateliers:
        raise HTTPException(status_code=400, detail="Listes vides.")

    try:
        df = generer_planning(ateliers, teams)
        plannings = conversions_par_equipe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for equipe, df_eq in plannings.items():
                sheet_name = equipe[:30].replace(":", "").replace("/", "")
                df_eq.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="plannings_equipes.xlsx"'
        }
        return StreamingResponse(output,
                                 headers=headers,
                                 media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                 )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pour lancer : uvicorn web.main:app --reload
