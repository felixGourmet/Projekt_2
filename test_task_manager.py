import pytest
import mysql.connector
from task_manager import vytvoreni_tabulky, pridat_ukol, zobrazit_ukoly, aktualizovat_ukol, odstranit_ukol

TEST_CFG = {
    "host": "localhost",
    "user": "root",
    "password": "heslicko1."
}
DB_NAME = "ukoly_test_db"

@pytest.fixture(scope="module")
def conn():
    conn = mysql.connector.connect(**TEST_CFG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.database = DB_NAME
    vytvoreni_tabulky(conn)
    yield conn
    cur.execute(f"DROP DATABASE {DB_NAME}")
    conn.close()

def test_pridat_ukol_ok(conn):
    pridat_ukol(conn, "Test", "Test_popis")
    ukoly = zobrazit_ukoly(conn)
    assert len(ukoly) > 0

def test_pridat_ukol_neplatny_vstup(conn):
    with pytest.raises(ValueError):
        pridat_ukol(conn, "", "")

def test_aktualizovat_ukol_ok(conn):
    pridat_ukol(conn, "Test_zmena", "Test_zmena_popis")
    ukol_id = zobrazit_ukoly(conn)[-1][0]
    aktualizovat_ukol(conn, ukol_id, "probíhá")
    cur = conn.cursor()
    cur.execute("SELECT stav FROM ukoly WHERE id=%s", (ukol_id,))
    assert cur.fetchone()[0] == "probíhá"

def test_aktualizovat_ukol_neplatne_id(conn):
    with pytest.raises(LookupError):
        aktualizovat_ukol(conn, 999999, "hotovo")

def test_odstranit_ukol_ok(conn):
    pridat_ukol(conn, "Test_smazat", "Test_smazat_popis")
    ukol_id = zobrazit_ukoly(conn)[-1][0]
    odstranit_ukol(conn, ukol_id)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ukoly WHERE id=%s", (ukol_id,))
    assert cur.fetchone()[0] == 0

def test_odstranit_ukol_neplatne_id(conn):
    with pytest.raises(LookupError):
        odstranit_ukol(conn, 999999)
