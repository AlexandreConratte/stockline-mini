"""Tests de l'API StockLine mini."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sante_repond_ok():
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"


def test_liste_des_produits():
    reponse = client.get("/produits")
    assert reponse.status_code == 200
    assert len(reponse.json()) >= 3


def test_produit_inconnu_renvoie_404():
    reponse = client.get("/produits/9999")
    assert reponse.status_code == 404


def test_creation_puis_lecture_d_un_produit():
    nouveau = {"nom": "Souris sans fil", "quantite": 25, "seuil_alerte": 8}
    creation = client.post("/produits", json=nouveau)
    assert creation.status_code == 201
    produit_id = creation.json()["id"]

    relecture = client.get(f"/produits/{produit_id}")
    assert relecture.status_code == 200
    assert relecture.json()["nom"] == "Souris sans fil"


def test_alertes_detecte_le_stock_bas():
    reponse = client.get("/alertes")
    noms = [p["nom"] for p in reponse.json()]
    assert "Écran 27 pouces" in noms  # 3 en stock, seuil à 5