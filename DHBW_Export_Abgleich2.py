import re
from playwright.sync_api import Playwright, sync_playwright
import time
import os

# Funktion zum Extrahieren der relevanten Inhalte und Speichern im Textfile
def extract_and_append_content(page, filename, semester_label):
    print(f"Extrahiere Inhalte für {semester_label}...")  # Debugging-Ausgabe
    try:
        # Extrahiere den relevanten Textinhalt der Seite (Name des Fachs, Endnote und Credits)
        subjects = page.locator("table").nth(1).locator("tr").nth(1).locator("td")
        extracted_data = []

        if subjects.count() == 0:
            print("Keine Fächer gefunden!")  # Debugging-Ausgabe
        else:
            print(f"{subjects.count()} Fächer gefunden.")  # Debugging-Ausgabe

        rows = page.locator("table").nth(1).locator("tr")
        for i in range(1, rows.count()):  # Überspringe die Header-Zeile
            row = rows.nth(i)
            columns = row.locator("td")
            if columns.count() > 3:
                name = columns.nth(1).inner_text().strip()
                grade = columns.nth(2).inner_text().strip()
                credits = columns.nth(3).inner_text().strip()
                extracted_data.append(f"{name}: {grade} (Credits: {credits})")

        if extracted_data:
            print(f"Inhalt für {semester_label} erfolgreich extrahiert.")
            # Neuen Inhalt anhängen, inklusive der Semester-Information
            with open(filename, 'a', encoding='utf-8') as file:  # 'a' für Anhängen, erstellt die Datei, wenn sie nicht existiert
                file.write(f"\n\n--- Ergebnisse für {semester_label} ---\n")
                for line in extracted_data:
                    file.write(f"{line}\n")
                print(f"Inhalt für {semester_label} wurde in die Datei {filename} geschrieben.")
        else:
            print(f"Inhalt für {semester_label} ist leer oder konnte nicht extrahiert werden.")
    except Exception as e:
        print(f"Fehler bei der Extraktion für {semester_label}: {str(e)}")

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigiere durch die Seiten und logge dich ein
    print("Navigiere zur Login-Seite...")  # Debugging-Ausgabe
    page.goto("https://dualis.dhbw.de/")
    page.goto("https://dualis.dhbw.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=STARTPAGE_DISPATCH&ARGUMENTS=-N000000000000001")
    page.goto("https://dualis.dhbw.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N000000000000001,-N000324,-Awelcome")
    page.get_by_label("Benutzername:").fill("s212566@student.dhbw-mannheim.de")
    page.get_by_label("Passwort:").fill("8LiBEG9hR")
    page.get_by_role("button", name="Anmelden").click()
    print("Erfolgreich eingeloggt.")  # Debugging-Ausgabe

    # Warte, bis die Seite vollständig geladen ist, bevor du fortfährst
    page.get_by_role("link", name="Prüfungsergebnisse").click()
    page.wait_for_load_state("networkidle")
    print("Prüfungsergebnisse geladen.")  # Debugging-Ausgabe

    # Warte auf das Vorhandensein des Dropdown-Menüs für das Semester
    try:
        page.wait_for_selector('select[name="Semester:"]', timeout=10000)  # Warte bis zu 10 Sekunden
        print("Semester-Dropdown gefunden.")  # Debugging-Ausgabe

        # Alle Optionen im Auswahlmenü "Semester" extrahieren
        semester_options = page.locator('select[name="Semester:"] option')
        options_count = semester_options.count()
        print(f"{options_count} Semester-Optionen gefunden.")  # Debugging-Ausgabe

        for i in range(options_count):
            # Semester auswählen
            option_value = semester_options.nth(i).get_attribute("value")
            option_label = semester_options.nth(i).inner_text()
            page.select_option('select[name="Semester:"]', option_value)
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Sicherheitspause für den Fall von Ladeverzögerungen
            extract_and_append_content(page, filename, option_label)

    except Exception as e:
        print(f"Fehler beim Finden des Semester-Dropdowns: {str(e)}")

    # Speicherpfad des Textfiles in der Konsole ausgeben
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")  # Pfad zum Desktop
    filename = os.path.join(desktop_path, 'webpage_text.txt')  # Spezifiziert den Dateinamen auf dem Desktop
    print(f"Das Textfile wurde gespeichert unter: {filename}")

    # Browser nach einer kurzen Wartezeit schließen
    time.sleep(30)
    context.close()
    browser.close()

# Hauptfunktion
with sync_playwright() as playwright:
    run(playwright)
