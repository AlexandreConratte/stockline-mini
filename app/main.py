"""StockLine mini — API d'inventaire adossée à PostgreSQL."""
import asyncio
import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

PRODUITS_INITIAUX = [
    ("Clavier mécanique", 12, 5),
    ("Écran 27 pouces", 3, 5),
    ("Câble HDMI 2 m", 40, 10),
]


def dsn():
    """Construit la chaîne de connexion depuis les variables d'environnement."""
    return (
        f"host={os.environ.get('DB_HOTE', 'localhost')} "
        f"port={os.environ.get('DB_PORT', '5432')} "
        f"dbname={os.environ.get('DB_NOM', 'stockline')} "
        f"user={os.environ.get('DB_UTILISATEUR', 'stockline')} "
        f"password={os.environ['DB_MOT_DE_PASSE']}"
    )


def connexion():
    return psycopg.connect(dsn(), row_factory=dict_row)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    # La base peut mettre quelques secondes à démarrer : on réessaie.
    for _ in range(10):
        try:
            with connexion() as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS produits (
                           id SERIAL PRIMARY KEY,
                           nom TEXT NOT NULL,
                           quantite INTEGER NOT NULL,
                           seuil_alerte INTEGER NOT NULL DEFAULT 5
                       )"""
                )
                nb = conn.execute(
                    "SELECT COUNT(*) AS nb FROM produits"
                ).fetchone()["nb"]
                if nb == 0:
                    conn.cursor().executemany(
                        "INSERT INTO produits (nom, quantite, seuil_alerte) "
                        "VALUES (%s, %s, %s)",
                        PRODUITS_INITIAUX,
                    )
            break
        except psycopg.OperationalError:
            await asyncio.sleep(2)
    else:
        raise RuntimeError("base de données injoignable après 10 tentatives")
    yield


app = FastAPI(title="StockLine mini", lifespan=cycle_de_vie)


class Produit(BaseModel):
    nom: str
    quantite: int
    seuil_alerte: int = 5


@app.get("/sante")
def sante():
    try:
        with connexion() as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="base de données injoignable")
    return {"statut": "ok", "base_de_donnees": "ok"}


@app.get("/produits")
def lister_produits():
    with connexion() as conn:
        return conn.execute("SELECT * FROM produits ORDER BY id").fetchall()


@app.get("/produits/{produit_id}")
def lire_produit(produit_id: int):
    with connexion() as conn:
        produit = conn.execute(
            "SELECT * FROM produits WHERE id = %s", (produit_id,)
        ).fetchone()
    if produit is None:
        raise HTTPException(status_code=404, detail="produit inconnu")
    return produit


@app.post("/produits", status_code=201)
def creer_produit(produit: Produit):
    with connexion() as conn:
        return conn.execute(
            "INSERT INTO produits (nom, quantite, seuil_alerte) "
            "VALUES (%s, %s, %s) RETURNING *",
            (produit.nom, produit.quantite, produit.seuil_alerte),
        ).fetchone()


@app.get("/alertes")
def alertes():
    """Produits dont la quantité est passée sous le seuil d'alerte."""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM produits WHERE quantite < seuil_alerte ORDER BY id"
        ).fetchall()