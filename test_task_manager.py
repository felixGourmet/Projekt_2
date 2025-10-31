import os
from dotenv import load_dotenv
import mysql.connector
import pytest
from task_manager import vytvoreni_tabulky, pridat_ukol_db, aktualizovat_ukol_db, odstranit_ukol_db

# Načtení konfiguračních údajů z .env souboru
load_dotenv()

TEST_HOST = os.getenv("DB_HOST", "localhost")
TEST_USER = os.getenv("DB_USER", "root")
TEST_PASS = os.getenv("DB_PASSWORD", "")
TEST_DB = os.getenv("TEST_DB_NAME", "ukoly_test_db")

@pytest.fixture(scope="module")
def conn():
    server = mysql.connector.connect(host=TEST_HOST, user=TEST_USER, password=TEST_PASS)
    cur = server.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
    cur.execute(f"USE {TEST_DB}")
    cur.execute("DROP TABLE IF EXISTS ukoly")
    server.commit()

    vytvoreni_tabulky(server)
    yield server

    cur.execute(f"DROP DATABASE {TEST_DB}")
    server.close()

# Pomocné dotazy pro kontrolu dat v databázi
def _count_tasks(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ukoly")
    n = c.fetchone()[0]
    c.close()
    return n

def _get_last_id(conn):
    c = conn.cursor()
    c.execute("SELECT id FROM ukoly ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    c.close()
    return row[0] if row else None

def _get_status(conn, uid):
    c = conn.cursor()
    c.execute("SELECT stav FROM ukoly WHERE id=%s", (uid,))
    row = c.fetchone()
    c.close()
    return row[0] if row else None

# Testy funkcí

def test_pridat_ukol_ok(conn):
    pridat_ukol_db(conn, "Test", "Popis")
    assert _count_tasks(conn) > 0

def test_pridat_ukol_neplatny_vstup(conn):
    with pytest.raises(ValueError):
        pridat_ukol_db(conn, "", "")

def test_aktualizovat_ukol_ok(conn):
    pridat_ukol_db(conn, "Zmena_Ok", "Zmena_Popis_Ok")
    uid = _get_last_id(conn)
    aktualizovat_ukol_db(conn, uid, "probíhá")
    assert _get_status(conn, uid) == "probíhá"

def test_aktualizovat_ukol_neplatny_id(conn):
    with pytest.raises(LookupError):
        aktualizovat_ukol_db(conn, 999999, "hotovo")

def test_aktualizovat_ukol_neplatny_stav(conn):
    pridat_ukol_db(conn, "Zmena_Neplatne", "Zmena_Popis_Neplatne")
    uid = _get_last_id(conn)
    with pytest.raises(ValueError):
        aktualizovat_ukol_db(conn, uid, "Neplatny_Stav")

def test_odstranit_ukol_ok(conn):
    pridat_ukol_db(conn, "Delete_Ok", "Delete_Ok_Popis")
    uid = _get_last_id(conn)
    odstranit_ukol_db(conn, uid)
    assert _get_status(conn, uid) is None

def test_odstranit_ukol_neplatny_id(conn):
    with pytest.raises(LookupError):
        odstranit_ukol_db(conn, 123456789)
