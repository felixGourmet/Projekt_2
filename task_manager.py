import mysql.connector

# Nastavení připojení
DB = {
    "host": "localhost",
    "user": "root",
    "password": "heslicko1.",
    "database": "ukoly_db"
}

# Připojení k databázi
def pripojeni_db():
    try:
        spojeni = mysql.connector.connect(**DB)
        return spojeni
    except:
        print("Chyba při připojení k databázi.")
        return None

# Vytvoření tabulky, pokud neexistuje
def vytvoreni_tabulky(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ukoly(
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('nezahájeno','probíhá','hotovo') DEFAULT 'nezahájeno',
            datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# Hlavní menu
def hlavni_menu():
    conn = pripojeni_db()
    if conn is None:
        return
    vytvoreni_tabulky(conn)

    while True:
        print("\n1) Přidat úkol")
        print("2) Zobrazit úkoly")
        print("3) Aktualizovat úkol")
        print("4) Odstranit úkol")
        print("5) Ukončit program")

        volba = input("Vyber možnost: ")

        if volba == "1":
            nazev = input("Název: ")
            popis = input("Popis: ")
            try:
                pridat_ukol(conn, nazev, popis)
                print("Úkol přidán.")
            except Exception as e:
                print("Chyba:", e)

        elif volba == "2":
            ukoly = zobrazit_ukoly(conn)
            if ukoly:
                for u in ukoly:
                    print(u)
            else:
                print("Seznam úkolů je prázdný.")

        elif volba == "3":
            ukoly = zobrazit_ukoly(conn)
            if not ukoly:
                print("Žádné úkoly k aktualizaci.")
            else:
                print("\nDostupné úkoly:")
                for u in ukoly:
                    print(f"ID: {u[0]}, Název: {u[1]}, Stav: {u[3]}")
                iid = input("Zadej ID úkolu: ")
                stav = input("Nový stav (probíhá/hotovo): ")
                try:
                    aktualizovat_ukol(conn, iid, stav)
                    print("✅ Stav byl změněn.")
                except Exception as e:
                    print("Chyba:", e)

        elif volba == "4":
            ukoly = zobrazit_ukoly(conn)
            if not ukoly:
                print("Žádné úkoly k odstranění.")
            else:
                print("\nDostupné úkoly:")
                for u in ukoly:
                    print(f"ID: {u[0]}, Název: {u[1]}, Stav: {u[3]}")
                iid = input("Zadej ID úkolu: ")
                try:
                    odstranit_ukol(conn, iid)
                    print("Úkol byl odstraněn z databáze.")
                except Exception as e:
                    print("Chyba:", e)

        elif volba == "5":
            print("Program ukončen.")
            break
        else:
            print("Neplatná volba.")

    conn.close()

# Přidání úkolu
def pridat_ukol(conn, nazev, popis):
    if nazev.strip() == "" or popis.strip() == "":
        raise ValueError("Název i popis musí být vyplněné.")
    cur = conn.cursor()
    cur.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
    conn.commit()

# Zobrazení úkolů
def zobrazit_ukoly(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('nezahájeno','probíhá')")
    return cur.fetchall()

# Aktualizace úkolu
def aktualizovat_ukol(conn, ukol_id, novy_stav):
    if novy_stav not in ("probíhá", "hotovo"):
        raise ValueError("Neplatný stav.")
    cur = conn.cursor()
    cur.execute("UPDATE ukoly SET stav=%s WHERE id=%s", (novy_stav, ukol_id))
    if cur.rowcount == 0:
        raise LookupError("Úkol s tímto ID nebyl nalezen.")
    conn.commit()

# Odstranění úkolu
def odstranit_ukol(conn, ukol_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM ukoly WHERE id=%s", (ukol_id,))
    if cur.rowcount == 0:
        raise LookupError("Úkol s tímto ID nebyl nalezen.")
    conn.commit()

if __name__ == "__main__":
    hlavni_menu()
