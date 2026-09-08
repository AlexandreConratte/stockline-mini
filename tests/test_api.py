"""Tests de l'API StockLine mini (version PostgreSQL)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Le "with" déclenche le cycle de vie : création de la table incluse.
    with TestClient(app) as c:
        yield c



def test_sante_repond_ok(client):
    reponse = client.get("/sante")
    print(reponse.json())
    assert reponse.status_code == 200
    assert reponse.json()["base_de_donnees"] == "ok"


def test_liste_des_produits(client):
    reponse = client.get("/produits")
    assert reponse.status_code == 200
    assert len(reponse.json()) >= 3


def test_produit_inconnu_renvoie_404(client):
    reponse = client.get("/produits/9999")
    assert reponse.status_code == 404


def test_creation_puis_lecture_d_un_produit(client):
    nouveau = {"nom": "Souris sans fil", "quantite": 25, "seuil_alerte": 8}
    creation = client.post("/produits", json=nouveau)
    assert creation.status_code == 201
    produit_id = creation.json()["id"]

    relecture = client.get(f"/produits/{produit_id}")
    assert relecture.status_code == 200
    assert relecture.json()["nom"] == "Souris sans fil"


def test_alertes_detecte_le_stock_bas(client):
    reponse = client.get("/alertes")
    noms = [p["nom"] for p in reponse.json()]
    assert "Écran 27 pouces" in noms  # 3 en stock, seuil à 5

