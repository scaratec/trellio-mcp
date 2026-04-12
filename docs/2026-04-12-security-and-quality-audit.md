2026-04-12

# Security & Code Quality Audit -- trellio-mcp v0.1.2

**Auftraggeber:** IT-Sicherheit (Enterprise Security Review)
**Kontext:** Sicherheitsfreigabe fuer Unternehmenseinsatz (100.000 Mitarbeiter)
**Vergleichsobjekt:** mcp-google-map v0.0.50 (externer MCP-Server, TypeScript)
**Gesamtrisiko:** LOW-MEDIUM
**Empfehlung:** Freigabe nach Nachbesserung (Pflicht-Massnahmen umsetzen)

---

## 1. Security Assessment

### 1.1 Checkliste

| #  | Kategorie                  | Status | Befund |
|----|----------------------------|--------|--------|
| 1  | Hardcoded Secrets          | PASS   | Keine API-Keys, Tokens oder Passwoerter im Quellcode |
| 2  | Code Injection             | PASS   | Kein eval(), exec(), subprocess oder dynamische Code-Ausfuehrung |
| 3  | Eingabevalidierung         | INFO   | An trellio-client delegiert (Pydantic); keine Server-seitige Validierung |
| 4  | Netzwerk-Angriffsflaeche   | PASS   | Nur stdio-Transport; kein HTTP-Listener im Normalbetrieb |
| 5  | Ausgehende Verbindungen    | PASS   | Nur trello.com (HTTPS) und localhost (OAuth-Callback) |
| 6  | Telemetrie / Tracking      | PASS   | Nicht vorhanden |
| 7  | Obfuskierter Code          | PASS   | Gesamter Quellcode ist lesbares Python |
| 8  | Datenpersistenz            | PASS   | Kein Caching, keine Datenbank; Credentials mit 0600-Berechtigungen |
| 9  | Credential-Speicherung     | INFO   | Klartext-JSON; nur OS-Dateiberechtigungen; keine Verschluesselung at rest |
| 10 | Token-Ablauf               | WARN   | OAuth-Token mit `expiration: "never"` |
| 11 | Schreiboperationen         | INFO   | 40 Tools umfassen Create-, Update- und Delete-Operationen auf Trello-Daten |
| 12 | Webhook-Tool               | WARN   | `create_webhook(callback_url)` akzeptiert beliebige URLs |
| 13 | Abhaengigkeiten (direkt)   | PASS   | 2 Produktionsabhaengigkeiten, beide legitim (mcp, trellio-client) |
| 14 | Dependency Pinning         | WARN   | Nutzt `>=` (Minimum); keine Obergrenze oder exakte Pins |
| 15 | Lock-File                  | FAIL   | Kein Lock-File vorhanden |
| 16 | CI/CD-Pipeline             | FAIL   | Keine automatisierten Builds, Linting oder Security-Scans |
| 17 | Security-Dokumentation     | FAIL   | Keine SECURITY.md vor diesem Audit (jetzt hinzugefuegt) |
| 18 | LICENSE-Datei              | FAIL   | Fehlt im Repository-Root (nur in pyproject.toml deklariert) |
| 19 | BDD-Testabdeckung          | PASS   | 122 Szenarien / 732 Steps ueber 15 Feature-Dateien |
| 20 | Fehlerbehandlung           | PASS   | Strukturierte Fehler mit isError-Flag; keine Stack-Traces exponiert |
| 21 | Supply Chain (transitiv)   | INFO   | Transitive Abhaengigkeiten nicht auditiert (kein Lock-File) |
| 22 | Schadcode / Backdoors      | PASS   | Nicht gefunden |

### 1.2 Staerken

- Minimale Angriffsflaeche (stdio, 2 Abhaengigkeiten, kein Netzwerk-Listener)
- Interne Herkunft (Code im Besitz von scaratec, volle Kontrolle)
- Sichere Credential-Speicherung mit OS-Dateiberechtigungen
- Umfangreiche BDD-Testsuite
- Sauberer Code ohne Injection-Vektoren

### 1.3 Risiken

- Schreib-/Loeschoperationen auf Produktions-Trello-Daten durch KI-Agent
- Nie ablaufendes OAuth-Token mit vollem Lese-/Schreibzugriff
- Webhook-Erstellung erlaubt beliebige Callback-URLs (Datenabfluss-Vektor)
- Kein Lock-File, kein CI/CD, kein automatisiertes Security-Scanning
- Credentials nicht verschluesselt at rest

---

## 2. Code-Qualitaet

### 2.1 Uebersicht

| Kriterium             | Bewertung | Anmerkung |
|-----------------------|-----------|-----------|
| Typsicherheit         | 6/10      | Partielle Type Hints; einige Parameter untypisiert |
| Fehlerbehandlung      | 7/10      | Konsistentes Pattern, aber JSON-Parsing nicht abgesichert |
| Code-Duplizierung     | 5/10      | 45x identisches json.dumps-Pattern, wiederholte try/except-Bloecke |
| Modularisierung       | 8/10      | Saubere Domain-Trennung in tools/, klare Verantwortlichkeiten |
| Dokumentation         | 4/10      | Keine Docstrings; gute ADRs und BDD-Specs, aber Code undokumentiert |
| Async-Patterns        | 9/10      | Korrektes async/await; keine blockierenden Aufrufe im Async-Kontext |
| Toter Code            | 9/10      | `set_client()` in server.py definiert aber nie aufgerufen |
| Anti-Patterns         | 7/10      | Globaler mutabler Client-Singleton; nicht thread-safe |

### 2.2 Befunde

#### B-1: Fehlende Docstrings (alle Module)

Kein einziges Modul, keine Funktion und keine Klasse hat eine
Docstring. Tool-Beschreibungen existieren nur als `description`-
Parameter in `@server.tool()`-Dekoratoren.

**Betroffene Dateien:** Alle `.py`-Dateien unter `src/trello_mcp/`

**Empfehlung:** Mindestens Modul-Docstrings und Docstrings fuer
oeffentliche Funktionen mit Nicht-offensichtlicher Logik ergaenzen
(insbesondere `auth.py`, `errors.py`, `server.py`).

#### B-2: json.dumps Aufruf-Stil

Alle 45 Aufrufe verwenden die Form:

```python
json.dumps(ensure_ascii=False, obj={...})
```

Standardmaessig ist das erste Argument von `json.dumps` positional
(`obj`). Die aktuelle Form funktioniert, weicht aber von der
ueblichen Konvention ab:

```python
json.dumps({...}, ensure_ascii=False)
```

**Betroffene Dateien:** Alle Tool-Dateien unter `src/trello_mcp/tools/`

**Empfehlung:** Auf konventionelle Parameterreihenfolge umstellen.

#### B-3: Code-Duplizierung in Tool-Dateien

Alle Tool-Dateien wiederholen dasselbe Pattern:

```python
@server.tool(description="...")
async def tool_name(...) -> str:
    try:
        result = await get_client().method(...)
        return json.dumps(ensure_ascii=False, obj={...})
    except TrelloAPIError as e:
        handle_api_error(e)
```

Dazu kommt ein identisches `kwargs`-Aufbau-Pattern in allen
Update-Tools:

```python
kwargs = {}
if name:
    kwargs["name"] = name
if description:
    kwargs["description"] = description
```

**Betroffene Dateien:** `boards.py`, `cards.py`, `lists.py`,
`labels.py`, `checklists.py`, `comments.py`, `webhooks.py`

**Empfehlung:** Fuer die wiederholten Patterns (try/except,
kwargs-Aufbau) pruefen, ob ein Dekorator oder eine Helper-
Funktion die Duplizierung reduziert. Nur umsetzen, wenn es
die Lesbarkeit nicht verschlechtert.

#### B-4: Untypisierter `set_client()`-Parameter

```python
# server.py:24
def set_client(client) -> None:
```

`client` hat keine Type Annotation. Die Funktion wird zudem
nirgends im Produktionscode aufgerufen.

**Empfehlung:** Typ ergaenzen (`client: TrellioClient`) oder
Funktion entfernen, falls sie nicht fuer Tests benoetigt wird.

#### B-5: `Optional`-Import in auth.py

`auth.py:5` importiert `Optional` aus `typing`, obwohl das
Projekt bereits die moderne `X | None`-Syntax (Python 3.10+)
in `server.py:7` verwendet.

**Datei:** `src/trello_mcp/auth.py`, Zeile 5 und 17

**Empfehlung:** `Optional[tuple[str, str]]` durch
`tuple[str, str] | None` ersetzen und den `Optional`-Import
entfernen.

#### B-6: Fehlende Fehlerbehandlung in auth.py

`auth.py:110` parst JSON vom HTTP-Request-Body ohne
Absicherung:

```python
body = json.loads(self.rfile.read(length))
```

Ein fehlerhafter Request fuehrt zu einem unbehandelten
`JSONDecodeError`.

**Datei:** `src/trello_mcp/auth.py`, Zeile 110

**Empfehlung:** `json.loads` in try/except wrappen und bei
Fehler HTTP 400 zurueckgeben.

#### B-7: Globaler mutabler Client-Singleton

```python
# server.py:7
_client: TrellioClient | None = None
```

Der Client wird als globale Variable mit Lazy-Initialisierung
verwaltet. Das ist nicht thread-safe, was fuer den aktuellen
stdio-Betrieb akzeptabel ist, aber bei zukuenftigen Transport-
Erweiterungen (HTTP) zum Problem wird.

**Datei:** `src/trello_mcp/server.py`, Zeilen 7-21

**Empfehlung:** Vorerst dokumentieren, dass der Server
single-threaded betrieben werden muss. Bei spaeterer HTTP-
Unterstuetzung auf Request-Scope oder AsyncLocal umstellen.

---

## 3. Massnahmenkatalog

### Pflicht -- vor Produktivfreigabe

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| P-1  | **Lock-File erstellen.** `pip-compile` (pip-tools) oder Migration zu Poetry. Lock-File in Git committen. | Klein | `pyproject.toml`, neues `requirements.lock` |
| P-2  | **Token-Ablauf auf 30 Tage setzen.** `"expiration": "never"` in `auth.py:43` durch konfigurierbare Variable ersetzen (Standard: `"30days"`, ueberschreibbar per `TRELLIO_TOKEN_EXPIRATION` oder `--expiration`). In README dokumentieren, dass `never` nur fuer Entwicklung empfohlen wird. | Klein | `src/trello_mcp/auth.py:43`, `README.md` |
| P-3  | **LICENSE-Datei hinzufuegen.** Vollstaendigen GPL-3.0-Text als `LICENSE` ins Repository-Root aufnehmen. | Trivial | neues `LICENSE` |
| P-4  | **Webhook-Tools absichern.** Umgebungsvariable `TRELLIO_ALLOWED_CALLBACK_HOSTS` (Allowlist, kommagetrennt) einfuehren. `create_webhook` und `update_webhook` gegen die Allowlist validieren. Ohne gesetzte Variable: Webhooks deaktivieren oder auf `localhost` beschraenken. | Mittel | `src/trello_mcp/tools/webhooks.py:25`, `src/trello_mcp/__init__.py` |

### Hoch -- innerhalb 90 Tagen

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| E-1  | **CI/CD-Pipeline einrichten.** GitHub Actions mit `ruff check`, `pip-audit`, `behave`, optional `mypy`. Workflow bei PRs auf `main` ausfuehren. | Mittel | neues `.github/workflows/ci.yml` |
| E-2  | **Credential-Verschluesselung at rest.** OS-Keyring (`keyring`-Bibliothek) als primaere Speichermethode; Datei-Fallback beibehalten. | Mittel | `src/trello_mcp/auth.py`, `pyproject.toml` |
| E-3  | **Read-Only-Modus.** `TRELLIO_READ_ONLY=true` registriert nur lesende Tools (list_*, get_*, search). | Klein | `src/trello_mcp/__init__.py` |
| E-4  | **Dependency-Pinning verschaerfen.** Von `>=` auf `~=` umstellen: `mcp~=1.12.0`, `trellio-client~=1.0.0`. | Trivial | `pyproject.toml:27-29` |

### Mittel -- innerhalb 6 Monaten

| ID   | Massnahme | Aufwand | Dateien |
|------|-----------|---------|---------|
| E-5  | **Audit-Logging.** Optionales strukturiertes Logging (JSON) auf stderr. Felder: Zeitstempel, Tool-Name, Parameter (ohne Credentials), Status. Aktivierung per `TRELLIO_AUDIT_LOG=true`. | Mittel | neues `src/trello_mcp/logging.py`, alle Tool-Dateien |
| E-6  | **Eingabevalidierung im Server.** Pydantic-Modelle oder Laengen-/Format-Checks fuer IDs (Trello-IDs = 24-stellige Hex-Strings) und URLs. | Mittel | alle Tool-Dateien |

### Code-Qualitaet -- bei naechster Gelegenheit

| ID   | Massnahme | Aufwand | Referenz |
|------|-----------|---------|----------|
| Q-1  | **json.dumps-Aufrufe vereinheitlichen.** Positionales `obj` statt Keyword-Argument. | Trivial | Befund B-2 |
| Q-2  | **Modul- und Funktions-Docstrings ergaenzen.** Prioritaet: `auth.py`, `server.py`, `errors.py`. | Klein | Befund B-1 |
| Q-3  | **`set_client()` typisieren oder entfernen.** | Trivial | Befund B-4 |
| Q-4  | **`Optional`-Import durch Union-Syntax ersetzen.** | Trivial | Befund B-5 |
| Q-5  | **JSONDecodeError in auth.py abfangen.** | Trivial | Befund B-6 |
| Q-6  | **Code-Duplizierung in Tools pruefen.** Nur reduzieren, wenn Lesbarkeit erhalten bleibt. | Klein | Befund B-3 |
| Q-7  | **Client-Singleton als single-threaded dokumentieren.** | Trivial | Befund B-7 |
