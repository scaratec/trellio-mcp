# Tool Design: Scenario-Driven Analysis

## Part 1: Usage Scenarios

### Scenario A: "Was liegt auf meinem Sprint-Board?"

**User sagt:** "Zeig mir den aktuellen Stand von meinem Sprint-Board."

**LLM muss:**
1. Board finden (nach Name) -> `search("Sprint")` oder `list_boards()`
2. Listen des Boards holen -> `list_lists(board_id)`
3. Cards pro Liste holen -> `list_cards(list_id)` x N Listen

**Analyse:** 1 + 1 + N Tool-Calls für eine einfache Übersicht.
Das ist chatty. Ein einzelner Power-User fragt das täglich.

**Design-Implikation:** Ein `get_board_overview`-Tool, das Board +
Listen + Cards in einem Call zurückgibt, wäre wertvoller als die
Einzelaufrufe. Die Resource `trello://board/{id}` löst das
teilweise, aber der LLM muss trotzdem erst das Board finden.

---

### Scenario B: "Erstelle ein neues Sprint-Board"

**User sagt:** "Erstelle ein Board 'Sprint 24' mit Listen To Do,
In Progress, Review, Done."

**LLM muss:**
1. Board erstellen -> `create_board("Sprint 24")`
2. 4 Listen erstellen -> `create_list(board_id, "To Do")` x4

**Analyse:** 5 Tool-Calls. Die Listen-Erstellung ist repetitiv
aber jede Liste braucht die board_id vom ersten Call.

**Design-Implikation:** Akzeptabel. Der LLM kann die 4 Listen-
Calls parallel machen (wenn der Client Parallelisierung
unterstützt). Ein Batch-Tool wäre Over-Engineering.

---

### Scenario C: "Verschiebe 'Fix Login' nach Done"

**User sagt:** "Verschiebe die Card 'Fix Login' nach Done."

**LLM muss:**
1. Card finden -> `search("Fix Login")` -> bekommt card mit id
2. Ziel-Liste finden -> `list_lists(board_id)` -> "Done" finden
3. Card verschieben -> `update_card(card_id, idList=done_list_id)`

**Analyse:** 3 Calls. Der LLM muss die Done-Liste per Name
finden und die richtige ID extrahieren. Fehleranfällig.

**Design-Implikation:** Das ist der häufigste Workflow und der
fehleranfälligste. Optionen:
- Option 1: Status quo -- 3 Calls, LLM muss IDs matchen
- Option 2: `move_card(card_id, list_name)` -- Server resolved
  den Listen-Namen zu einer ID
- Option 3: Status quo + gute Tool-Descriptions die den LLM
  leiten

Option 2 ist verlockend, versteckt aber Logik (Name->ID
Resolution) im Server. Wenn der Name mehrdeutig ist (zwei
Listen "Done" auf verschiedenen Boards), wird es undurchsichtig.
**Besser: Status quo mit guter Description.**

---

### Scenario D: "Füge eine Checklist zu Card X hinzu"

**User sagt:** "Füge der Card 'Deploy v2.1' eine Checklist
'Pre-Deploy' mit Items 'Run tests', 'Update changelog',
'Tag release' hinzu."

**LLM muss:**
1. Card finden -> `search("Deploy v2.1")`
2. Checklist erstellen -> `create_checklist(card_id, "Pre-Deploy")`
3. Items hinzufügen -> `create_check_item(cl_id, "Run tests")` x3

**Analyse:** 5 Calls. Akzeptabel -- der LLM kann die 3
check_item-Calls sequentiell machen (braucht checklist_id).

**Design-Implikation:** Kein Batch-Tool nötig. Die granularen
Tools funktionieren hier gut.

---

### Scenario E: "Kommentiere die letzte Entscheidung"

**User sagt:** "Schreib auf die Card 'Auth Redesign' einen
Kommentar: 'Decision: JWT statt Session Tokens, siehe ADR 005'."

**LLM muss:**
1. Card finden -> `search("Auth Redesign")`
2. Kommentar schreiben -> `add_comment(card_id, text)`

**Analyse:** 2 Calls. Clean und direkt.

**Design-Implikation:** Funktioniert perfekt mit 1:1 Mapping.

---

### Scenario F: "Was wurde diese Woche erledigt?"

**User sagt:** "Was wurde auf dem Sprint-Board diese Woche
nach Done verschoben?"

**LLM muss:**
1. Board finden -> `search("Sprint")` oder `list_boards()`
2. Done-Liste finden -> `list_lists(board_id)`
3. Cards in Done holen -> `list_cards(done_list_id)`
4. (Trello API liefert kein Moved-Date -- Limitation)

**Analyse:** Der LLM kann Cards in "Done" auflisten, aber nicht
wissen, WANN sie dorthin verschoben wurden. Die Trello API
liefert `dateLastActivity` auf Cards, aber das ist jede
Änderung, nicht nur Verschiebungen. Actions (Card-History)
sind in trellio nicht implementiert (nur comment-Actions).

**Design-Implikation:** Ehrliche Limitation. Der
`daily_standup`-Prompt sollte dokumentieren, dass er nur den
aktuellen Zustand zeigen kann, nicht die Historie.

---

### Scenario G: "Lösche das Archiv-Board"

**User sagt:** "Lösche das Board 'Archiv Q2'."

**LLM muss:**
1. Board finden -> `search("Archiv Q2")`
2. Board löschen -> `delete_board(board_id)`

**Analyse:** 2 Calls. Destruktive Operation -- der LLM sollte
vor der Löschung bestätigen, aber das ist Client-Verantwortung
(Claude Code fragt automatisch bei Tool-Calls, die als
destruktiv markiert sind).

**Design-Implikation:** Tool-Description sollte warnen:
"Permanently deletes the board and all its contents. This
action cannot be undone."

---

### Scenario H: "Suche alle Cards zu Authentication"

**User sagt:** "Zeig mir alle Cards, die mit Auth zu tun haben."

**LLM muss:**
1. `search("authentication")` -> bekommt cards + boards

**Analyse:** 1 Call. Perfekt.

**Design-Implikation:** Search ist eines der wertvollsten Tools.
Die Description sollte klar machen, dass es über alle Boards
sucht.

---

### Scenario I: "Webhook für Board-Änderungen einrichten"

**User sagt:** "Richte einen Webhook ein, der mich über
Änderungen am Board 'Production' informiert."

**LLM muss:**
1. Board finden -> `search("Production")`
2. Webhook erstellen -> `create_webhook(callback_url, board_id)`

**Analyse:** Der LLM braucht eine Callback-URL vom User. Er
kann sie nicht raten.

**Design-Implikation:** Tool-Description: "Registers a webhook.
Requires a callback URL where Trello will POST notifications."
Der LLM muss den User nach der URL fragen.

---

### Scenario J: "Gib mir einen Überblick über alle meine Boards"

**User sagt:** "Was habe ich alles in Trello?"

**LLM muss:**
1. `list_boards()` -> alle Boards

**Analyse:** 1 Call. Aber bei 20+ Boards ist die Response groß.

**Design-Implikation:** list_boards sollte kompakte Daten
zurückgeben (id, name, url) nicht das vollständige Board-Objekt.
**Rückgabe-Format ist ein Design-Entscheidung pro Tool.**

---

## Part 2: Erkenntnisse aus den Szenarien

### Erkenntnis 1: Das Board-Overview-Problem

Szenarien A und F zeigen: "Zeig mir Board X" braucht 2+N Calls.
Das ist der häufigste Workflow. Lösung:

**Composite-Tool `get_board_overview(board_id)`** das Board +
Listen + Card-Counts (nicht vollständige Cards) in einem Call
zurückgibt. Das bricht die 1:1-Regel, aber der Nutzen ist hoch.

Alternativ: Die Resource `trello://board/{id}` liefert dasselbe.
Aber Resources werden vom Client geladen, nicht vom LLM aufgerufen.
**Beides anbieten.**

### Erkenntnis 2: Name-zu-ID-Resolution

Szenarien C, D, E, G, I zeigen: Der User spricht in Namen
("Sprint-Board", "Done-Liste", "Fix Login"), aber die API braucht
IDs. Der LLM muss immer erst suchen/listen, dann operieren.

Lösungen:
- **search()** ist der universelle Resolver -- muss prominent sein
- Tool-Descriptions sollten den LLM leiten: "Use search() or
  list_boards() first to find the board ID"
- **Kein** Name-zu-ID-Resolution im Server -- das gehört zum LLM

### Erkenntnis 3: Rückgabe-Format

Jedes Tool gibt Daten zurück, die der LLM für Folgecalls braucht.
Kritisch ist:
- **IDs müssen immer in der Response sein** (für Chaining)
- **Namen/Titles müssen dabei sein** (für User-Anzeige)
- **Unnötige Felder weglassen** (URLs, Timestamps, Badges)

Ein `list_boards()` das 20 vollständige Board-Objekte mit URLs,
Badges, und Metadata zurückgibt, verschwendet Kontext. Besser:
kompakte Darstellung mit id + name + essentiellen Feldern.

### Erkenntnis 4: Destruktive Operationen

Szenarien G zeigt: delete-Tools brauchen klare Warnungen.
Die Tool-Description ist der einzige Ort, wo der LLM erfährt,
dass eine Operation destruktiv ist.

### Erkenntnis 5: Batch-Operationen nicht nötig

Kein Szenario erfordert Batch-Tools. Der LLM kann sequentielle
Calls machen. Batch-Tools (create_board_with_lists,
create_checklist_with_items) wären premature abstractions.

---

## Part 3: Tool-Design (abgeleitet aus Szenarien)

### Kategorie 1: Discovery (LLM findet Ressourcen)

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_boards` | - | [{id, name, closed}] | A, J |
| `search` | query, limit? | {boards: [{id, name}], cards: [{id, name, idBoard}]} | C, E, H |

**Beschreibung search:** "Search across all boards and cards by
keyword. Returns matching board and card names with IDs. Use this
to find resources before operating on them."

### Kategorie 2: Board Operations

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `get_board_overview` | board_id | {board, lists: [{id, name, cards: [{id, name}]}]} | A, F |
| `create_board` | name, description? | {id, name} | B |
| `update_board` | board_id, name?, description? | {id, name} | - |
| `delete_board` | board_id | {deleted: true} | G |

**Beschreibung delete_board:** "Permanently deletes the board
and ALL its lists, cards, and attachments. Cannot be undone."

**get_board_overview** ist das Composite-Tool. Es ruft intern
get_board + list_lists + list_cards pro Liste auf und liefert
eine aggregierte Ansicht. Das ist der einzige "intelligente"
Tool-Handler.

### Kategorie 3: List Operations

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_lists` | board_id | [{id, name}] | A, C |
| `create_list` | board_id, name | {id, name} | B |

Listen haben kein Update/Delete in der Trello API (nur close).

### Kategorie 4: Card Operations

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_cards` | list_id | [{id, name, desc?, idList}] | A, F |
| `create_card` | list_id, name, desc? | {id, name} | - |
| `get_card` | card_id | {id, name, desc, idList, idBoard} | - |
| `update_card` | card_id, name?, desc?, idList? | {id, name} | C |
| `delete_card` | card_id | {deleted: true} | - |

**Beschreibung update_card:** "Update card properties. Set idList
to move the card to a different list."

### Kategorie 5: Labels

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_board_labels` | board_id | [{id, name, color}] | - |
| `create_label` | board_id, name, color | {id, name, color} | - |
| `update_label` | label_id, name?, color? | {id, name, color} | - |
| `delete_label` | label_id | {deleted: true} | - |

### Kategorie 6: Checklists + Items

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_card_checklists` | card_id | [{id, name, checkItems: [{id, name, state}]}] | - |
| `create_checklist` | card_id, name | {id, name} | D |
| `delete_checklist` | checklist_id | {deleted: true} | - |
| `create_check_item` | checklist_id, name | {id, name, state} | D |
| `update_check_item` | card_id, check_item_id, state | {id, name, state} | - |
| `delete_check_item` | checklist_id, check_item_id | {deleted: true} | - |

### Kategorie 7: Comments

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_comments` | card_id | [{id, text, date}] | - |
| `add_comment` | card_id, text | {id, text} | E |
| `update_comment` | comment_id, text | {id, text} | - |
| `delete_comment` | comment_id | {deleted: true} | - |

### Kategorie 8: Members (read-only)

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `get_me` | - | {id, username, fullName} | - |
| `list_board_members` | board_id | [{id, username, fullName}] | - |
| `get_member` | member_id | {id, username, fullName} | - |

### Kategorie 9: Attachments

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_attachments` | card_id | [{id, name, url}] | - |
| `create_attachment` | card_id, url, name? | {id, name, url} | - |
| `delete_attachment` | card_id, attachment_id | {deleted: true} | - |

### Kategorie 10: Webhooks

| Tool | Parameter | Rückgabe | Szenario |
|------|-----------|----------|----------|
| `list_webhooks` | - | [{id, description, callbackURL, active}] | - |
| `create_webhook` | callback_url, id_model, description? | {id, callbackURL} | I |
| `get_webhook` | webhook_id | {id, description, callbackURL, active} | - |
| `update_webhook` | webhook_id, description?, active? | {id, description} | - |
| `delete_webhook` | webhook_id | {deleted: true} | - |

---

## Part 4: Abweichungen von der 1:1-Regel

ADR 004 definiert "1 Tool pro Client-Methode". Die Szenario-
Analyse zeigt eine Ausnahme:

### Neues Composite-Tool: get_board_overview

**Begründung:** Szenario A ("Was liegt auf meinem Board?") ist
der häufigste Workflow. Ohne Composite-Tool braucht es 2+N
Calls. Mit dem Tool: 1 Call.

**Was es tut:**
1. `client.get_board(board_id)`
2. `client.list_lists(board_id)`
3. Für jede Liste: `client.list_cards(list_id)`
4. Aggregiert zu: `{board, lists: [{name, cards: [{name}]}]}`

**Was es NICHT tut:**
- Keine Business-Logik
- Keine Filterung
- Keine Berechnung
- Nur Aggregation von 3 read-only Calls

Das ist die einzige Abweichung. ADR 004 wird entsprechend
ergänzt.

### Entfernte trellio-Methoden (kein eigenes Tool)

- `list_all_boards()` (async generator) -- nicht als Tool
  exponierbar, da MCP-Tools keine Streaming-Responses
  unterstützen. `list_boards(limit)` reicht.
- `get_board()` -- subsumiert durch `get_board_overview`.
  Wird aber trotzdem als Tool behalten für Fälle, wo nur
  die Board-Metadaten gebraucht werden (weniger Kontext).

---

## Part 5: Tool-Beschreibungen (kritisch für LLM-Usability)

Jede Beschreibung folgt dem Muster:
1. Was das Tool tut (1 Satz)
2. Wann man es nutzt (optional, wenn nicht offensichtlich)
3. Warnungen (nur bei destruktiven Ops)

Beispiele:

**search:** "Search boards and cards by keyword across all your
Trello boards. Use this to find resource IDs before performing
operations."

**update_card:** "Update card properties like name, description,
or list assignment. Set idList to move the card to a different
list."

**delete_board:** "Permanently delete a board including all its
lists, cards, and attachments. This cannot be undone."

**create_webhook:** "Register a webhook to receive HTTP POST
notifications about changes to a board or card. Requires a
publicly accessible callback URL."

---

## Zusammenfassung

| Kategorie | Anzahl Tools | Davon Composite |
|-----------|-------------|-----------------|
| Discovery | 2 | 0 |
| Boards | 4 | 1 (get_board_overview) |
| Lists | 2 | 0 |
| Cards | 5 | 0 |
| Labels | 4 | 0 |
| Checklists | 6 | 0 |
| Comments | 4 | 0 |
| Members | 3 | 0 |
| Attachments | 3 | 0 |
| Webhooks | 5 | 0 |
| **Total** | **38** | **1** |

38 Tools (37 delegierend + 1 Composite), abgeleitet aus 10
konkreten Usage-Szenarien.
