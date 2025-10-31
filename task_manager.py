import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Načtení konfiguračních údajů z .env souboru
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Připojení k databázi
def pripojeni_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print("Chyba při připojení k databázi:", e)
        return None

# Vytvoření databáze + tabulky
def vytvoreni_databaze():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.commit()
        cur.close()
        conn.close()
    except Error as e:
        print("Chyba při vytváření databáze:", e)

def vytvoreni_tabulky(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('nezahájeno','probíhá','hotovo') NOT NULL DEFAULT 'nezahájeno',
                datum_vytvoreni DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
    except Error as e:
        print("Chyba při vytváření tabulky:", e)

# Hlavní menu
def hlavni_menu():
    vytvoreni_databaze()
    conn = pripojeni_db()
    if not conn:
        print("Nelze pokračovat bez připojení k databázi.")
        return

    try:
        vytvoreni_tabulky(conn)
    except Error as e:
        print("Nelze připravit tabulku:", e)
        conn.close()
        return

    while True:
        print("\n1) Přidat úkol")
        print("2) Zobrazit úkoly")
        print("3) Aktualizovat úkol")
        print("4) Odstranit úkol")
        print("5) Ukončit program")
        volba = input("Vyber možnost: ").strip()

        if volba == "1":
            pridat_ukol(conn)
        elif volba == "2":
            zobrazit_ukoly(conn)
        elif volba == "3":
            aktualizovat_ukol(conn)
        elif volba == "4":
            odstranit_ukol(conn)
        elif volba == "5":
            print("Program ukončen.")
            conn.close()
            break
        else:
            print("Neplatná volba, zkus znovu.")

# Přidání úkolu
def pridat_ukol(conn):
    nazev = input("Název úkolu: ").strip()
    popis = input("Popis úkolu: ").strip()
    if not nazev or not popis:
        print("Název i popis musí být vyplněné.")
        return

    try:
        pridat_ukol_db(conn, nazev, popis)
        print("Úkol byl přidán.")
    except Error as e:
        print("Chyba při přidávání úkolu:", e)

# Zobrazení úkolů
def zobrazit_ukoly(conn):
    try:
        ukoly = vrat_ukoly_db(conn)
        if not ukoly:
            print("Seznam úkolů je prázdný.")
        else:
            for u in ukoly:
                print(f"ID: {u['id']}, Název: {u['nazev']}, Stav: {u['stav']}")
    except Error as e:
        print("Chyba při načítání úkolů:", e)

# Aktualizace úkolu
def aktualizovat_ukol(conn):
    zobrazit_ukoly(conn)
    s_id = input("Zadej ID úkolu: ").strip()
    if not s_id.isdigit():
        print("ID musí být číslo.")
        return

    novy_stav = input("Nový stav (probíhá/hotovo): ").strip().lower()
    if novy_stav not in ("probíhá", "hotovo"):
        print("Neplatný stav.")
        return

    try:
        aktualizovat_ukol_db(conn, int(s_id), novy_stav)
        print("Stav úkolu byl úspěšně změněn.")
    except LookupError as e:
        print(e)
    except Error as e:
        print("Chyba při aktualizaci:", e)

# Odstranění úkolu
def odstranit_ukol(conn):
    zobrazit_ukoly(conn)
    s_id = input("Zadej ID úkolu k odstranění: ").strip()
    if not s_id.isdigit():
        print("ID musí být číslo.")
        return

    try:
        odstranit_ukol_db(conn, int(s_id))
        print("Úkol byl odstraněn z databáze.")
    except LookupError as e:
        print(e)
    except Error as e:
        print("Chyba při odstraňování:", e)

# DB Funkce 
def pridat_ukol_db(conn, nazev, popis):
    if not nazev or not popis:
        raise ValueError("Název i popis jsou povinné.")
    cur = conn.cursor()
    cur.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
    conn.commit()
    cur.close()

def vrat_ukoly_db(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly WHERE stav IN ('nezahájeno','probíhá')")
    rows = cur.fetchall()
    cur.close()
    return rows

def aktualizovat_ukol_db(conn, ukol_id, novy_stav):
    if novy_stav not in ("probíhá", "hotovo"):
        raise ValueError("Neplatný stav.")
    cur = conn.cursor()
    cur.execute("UPDATE ukoly SET stav=%s WHERE id=%s", (novy_stav, ukol_id))
    if cur.rowcount == 0:
        cur.close()
        raise LookupError("Úkol s tímto ID nebyl nalezen.")
    conn.commit()
    cur.close()

def odstranit_ukol_db(conn, ukol_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM ukoly WHERE id=%s", (ukol_id,))
    if cur.rowcount == 0:
        cur.close()
        raise LookupError("Úkol s tímto ID nebyl nalezen.")
    conn.commit()
    cur.close()

if __name__ == "__main__":
    hlavni_menu()
