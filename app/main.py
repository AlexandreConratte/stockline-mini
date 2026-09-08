"""StockLine mini — API d'inventaire simplifiée (version en mémoire)."""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ENVIRONNEMENT = os.environ.get("STOCKLINE_ENV", "dev")

app = FastAPI(title="StockLine mini")


class Produit(BaseModel):
    nom: str
    quantite: int
    seuil_alerte: int = 5


PRODUITS: dict[int, dict] = {
    1: {"id": 1, "nom": "Clavier mécanique", "quantite": 12, "seuil_alerte": 5},
    2: {"id": 2, "nom": "Écran 27 pouces", "quantite": 3, "seuil_alerte": 5},
    3: {"id": 3, "nom": "Câble HDMI 2 m", "quantite": 40, "seuil_alerte": 10},
}


@app.get("/sante")
def sante():
    return {"statut": "ok", "environnement": ENVIRONNEMENT, "base_de_donnees": "ok"
}


@app.get("/produits")
def lister_produits():
    return list(PRODUITS.values())


@app.get("/produits/{produit_id}")
def lire_produit(produit_id: int):
    if produit_id not in PRODUITS:
        raise HTTPException(status_code=404, detail="produit inconnu")
    return PRODUITS[produit_id]


@app.post("/produits", status_code=201)
def creer_produit(produit: Produit):
    nouvel_id = max(PRODUITS, default=0) + 1
    PRODUITS[nouvel_id] = {"id": nouvel_id, **produit.model_dump()}
    return PRODUITS[nouvel_id]


@app.get("/alertes")
def alertes():
    """Produits dont la quantité est passée sous le seuil d'alerte."""
    return [p for p in PRODUITS.values() if p["quantite"] < p["seuil_alerte"]]