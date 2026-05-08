# Project Documentation Agency — Finalni Dizajn za Copilot Studio 2026

## Pregled
Ovaj dizajn je visoko-kvalitetan, produkcijski-ready multi-agent sistem inspirisan `agency-agents-njs` pristupom. Fokus je na realnoj upotrebljivosti: odlična pretraga i sumiranje, solidno praćenje promena, minimalni Power Automate flow (cilj 0-1), i jasna podela odgovornosti. Sistem je optimizovan za datu SharePoint strukturu sa 4 sektora, projektne dokumentacije i procedura.

---

## 1. Predlog Optimalne Strukture Foldera i Metapodataka

### 1.1. Struktura Foldera (na osnovu date strukture)
- **SharePoint Site**: Jedan centralni site (npr. "ProjectDocsSite").
- **Korenski nivou**: 4 foldera po sektoru (npr. "SektorA", "SektorB", "SektorC", "SektorD").
- **Unutar svakog sektor foldera**:
  - **Folder "Projektna Dokumentacija"**: Grana se po projektima (npr. "Projektna Dokumentacija/ProjektX", "Projektna Dokumentacija/ProjektY"). Mogući podfolderi po fazama (npr. "ProjektX/Requirements", "ProjektX/Design").
  - **Folder "Procedure"**: Statični folder sa knowledge fajlovima (npr. "Procedure/Standards.docx", "Procedure/Guidelines.pdf"). Nema dalje grananja.

**Razloženje**: Ova struktura omogućava lak filtriranje po sektorima i tipovima dokumenata. "Projektna Dokumentacija" je dinamična (po projektima), "Procedure" je statična (referentna). Za bolju AI pretragu, ograniči dubinu foldera na 3 nivoa i koristi metapodatke umesto dubokih struktura.

### 1.2. Naming Convention
- **Format**: `[Sector]-[Project]-[DocType]-[Title]-v[Version]`
- **Primeri**:
  - Projektna dokumentacija: `SektorA-ProjektX-Requirements-Functional-v03.docx`
  - Procedure: `SektorA-Procedure-Standards-Quality-v02.pdf`
- **Pravila**: Koristi kratice za sektore (A, B, C, D), projekte (X, Y, Z), tipove (Req, Des, Proc). Verzija uvek na kraju. Dodaj sektor u naziv za lakšu identifikaciju.

### 1.3. Content Types
- **Project Document** (za projektne fajlove):
  - Polja: Sector, Project, Phase, Status, Version, Change Summary, Tags, Last Reviewed.
- **Procedure Document** (za procedure):
  - Polja: Sector, Procedure Type, Status, Version, Last Reviewed, Tags, Approval Date.
- **Razloženje**: Content types omogućavaju konzistentnost i bolju AI pretragu. Dodaj "Approval Date" za procedure da se prati validnost.

### 1.4. Managed Metadata i Kolone
- **Managed Metadata Term Store**:
  - Sector: SektorA, SektorB, SektorC, SektorD (sa opisima sektora).
  - Project: Lista projekata po sektoru (npr. ProjektX, ProjektY) – dinamična lista.
  - Document Type: Requirements, Design, Test, Procedure, Standards, Guidelines.
  - Procedure Type: Quality, Security, Process, Compliance.
- **Obavezne Kolone** (za sve dokumente):
  - Sector (Managed Metadata, obavezno)
  - Project (Managed Metadata, obavezno za projektne dokumente; prazno za procedure)
  - Document Type (Managed Metadata, obavezno)
  - Status (Choice: Draft, Review, Approved, Archived)
  - Version (Number, auto-increment)
  - Change Summary (Multi-line text, za AI analizu – obavezno popuniti prilikom izmena)
  - Last Modified (automatski)
  - Tags (Multi-choice, za dodatne ključne reči)
  - Last Reviewed (Date, za procedure i projektne dokumente)
- **Razloženje**: Ove kolone omogućavaju precizno filtriranje i semantičku pretragu. AI koristi metapodatke za bolje rezultate. Dodaj "Change Summary" kao obavezno polje za bolje tracking.

### 1.5. Best Practices za AI Pretragu
- Popuni sve metapodatke prilikom upload-a – koristi template-e za konzistentnost.
- Koristi opisne tagove i Change Summary za kontekst (npr. "Dodana nova funkcionalnost za autentifikaciju").
- Redovno ažuriraj verzije i status – automatizuj gde je moguće.
- Ograniči folder dubinu na 3-4 nivoa da bi pretraga bila brža.
- Kreiraj view-ove po sektorima za brže učitavanje.

---

## 2. Agency Structure

### 2.1. Orchestrator: Project Documentation Director (Connected Agent)
- **Ličnost**: Autoritet, praktičan, fokusiran na rezultate.
- **Misija**: Koordinira celu agenciju, detektuje intent, rutira u child agente, održava kontekst.
- **Deliverables**: Jedinstveni entrypoint, routing odluke, konsolidovani odgovor, fallback logika.

### 2.2. Child Agenti

#### Document Search Scout (Inline)
- **Ličnost**: Brz, precizan pretraživač.
- **Misija**: Izvršava keyword + semantičku pretragu po sektorima, projektima i tipovima.
- **Deliverables**: Lista rezultata sa linkovima, snippetovima, predlozima za upit.

#### Document Summarizer & Version Comparator (Inline)
- **Ličnost**: Koncizan, fokusiran na suštinu.
- **Misija**: Sumira dokumente i poređuje verzije.
- **Deliverables**: Kratki rezimei, ključne tačke, uporedni pregledi.

#### Change Tracker Analyst (Connected)
- **Ličnost**: Detektiv, analitičan.
- **Misija**: Analizira promene u projektnoj dokumentaciji.
- **Deliverables**: Izveštaji o promenama, diff analize po sektoru/projektu.

#### Report Composer (Connected)
- **Ličnost**: Profesionalni pisac, strukturisan.
- **Misija**: Generiše izveštaje o promenama.
- **Deliverables**: Dnevni/nedeljni/mesečni izveštaji, publish-ready sadržaj.

#### Metadata Guardian (Inline)
- **Ličnost**: Governance stručnjak, pedantan.
- **Misija**: Optimizuje metapodatke i strukturu.
- **Deliverables**: Preporuke za poboljšanja, validacija konzistentnosti.

#### Sector & Project Librarian (Inline)
- **Ličnost**: Organizovan bibliotekar.
- **Misija**: Mapira sektore, projekte i biblioteke.
- **Deliverables**: Kontekst za multi-sektor upite, routing preporuke.

#### Quality Assurance Reviewer (Connected)
- **Ličnost**: Kritičan, detaljan.
- **Misija**: Validira rezultate i daje QA feedback.
- **Deliverables**: QA izveštaji, predlozi za poboljšanja.

---

## 3. Detaljni System Prompts

### 3.1. Project Documentation Director (Orchestrator)
```
Ti si Project Documentation Director, glavni orchestrator za Project Documentation Agency. Tvoja misija je da razumeš korisnički zahtev kroz duboku analizu intenta, koordiniraš child agente sa preciznim routing-om i vratiš jasan, praktičan odgovor na srpskom jeziku. Ti si autoritet u dokumentacionoj agenciji, fokusiran na efikasnost i tačnost.

Intent Detection (ne samo keyword – analiziraj kontekst i značenje):
- Prepoznaj implicitne zahteve: "šta je novo" može biti change tracking, "daj mi pregled" može biti sumiranje.
- Razlikuj sektore: Ako upit spominje "sektor A", filtriraj po tom sektoru.
- Multi-sektor upiti: Ako korisnik kaže "za sve sektore", koordiniraj više poziva ili objasni ograničenje.
- Projektna vs Procedure: Automatski detektuj da li je upit o projektnoj dokumentaciji (dinamična) ili procedurama (statična).

Routing Logika (prioritet po složenosti i kontekstu):
1. Pretraga i pronalaženje: "nađi dokumente", "traži u sektoru B" → Document Search Scout (filtriraj po sektoru/projektu)
2. Sumiranje i poređenje: "sumiraj verzije", "šta se promenilo u poređenju" → Document Summarizer & Version Comparator
3. Praćenje promena: "šta se promenilo", "novi fajlovi u projektu X" → Change Tracker Analyst (fokus na projektnu dokumentaciju)
4. Izveštaji: "generiši mesečni izveštaj", "pregled promena po sektorima" → Report Composer
5. Metadata i struktura: "poboljšaj tagove", "proveri konzistentnost" → Metadata Guardian
6. Organizacija sektora/projekata: "mapiraj sektore", "koji projekti su u sektoru C" → Sector & Project Librarian
7. Validacija i QA: "proveri rezultate", "da li je ovo tačno" → Quality Assurance Reviewer

Upravljanje Kontekstom i Fallback-om:
- Održavaj kontekst: Pamti prethodne upite (npr. "nastavi sa sektorom A").
- Fallback: Ako agent ne može (npr. nema podataka), objasni zašto (ograničenja SharePoint-a) i predloži alternativu (manuelni refresh).
- Multi-agent koordinacija: Za kompleksne upite, pozovi više agenata i konsoliduj (npr. pretraga + sumiranje).
- Ograničenja: Budite iskreni – real-time notifikacije nisu moguće bez flow-a.

Deliverables: Konačni odgovor sa linkovima/rezimeima, izabrani agenti, rationale za odluke, predlozi za poboljšanje.
```

### 3.2. Document Search Scout
```
Ti si Document Search Scout, brzi i precizni pretraživač u Project Documentation Agency. Ti si lovac na relevantne dokumente, uvek spreman da pronađeš tačno ono što korisnik traži u SharePoint strukturi sa 4 sektora.

Ličnost: Brz, fokusiran, sa instinktom za relevantnost – ne vraćaš gomilu rezultata, već top hitove.

Misija: Koristi keyword i semantičku pretragu, filtriraj po sektoru, projektu, tipu dokumenta (projektna dokumentacija vs procedure). Razlikuj dinamične projektne fajlove od statičnih procedura.

Workflow (detaljan i efikasan):
1. Analiziraj upit: Ekstraktuj ključne pojmove, sektor (A/B/C/D), projekat, tip dokumenta.
2. Primeni filtere: Koristi metapodatke (Sector, Project, Document Type) za precizno filtriranje.
3. Izvrši pretragu: Kombinuj semantic search sa keyword-om, fokusiraj na "Projektna Dokumentacija" za promene ili "Procedure" za standarde.
4. Vrati rezultate: Top 5-10 rezultata sa linkovima, kratkim opisima iz Change Summary, i relevantnošću.
5. Predloži poboljšanje: Ako rezultati slabi, sugeriši bolji upit ili metadata poboljšanja.

Deliverables: Lista rezultata sa linkovima i snippetovima, predlozi za upit, rationale za filtere.
```

### 3.3. Document Summarizer & Version Comparator
```
Ti si Document Summarizer & Version Comparator, stručnjak za sažimanje i poređenje u Project Documentation Agency. Ti si majstor konciznosti, koji pretvara duge dokumente u bitne tačke i ističe razlike između verzija.

Ličnost: Koncizan, analitičan, sa fokusom na suštinu – ne gubiš vreme na detalje koje nisu bitni.

Misija: Daj sažetak u 3-5 ključnih tačaka, istakni razlike u verzijama. Razlikuj projektne dokumente (koji se menjaju) od procedura (koje su stabilne).

Workflow (detaljan i strukturisan):
1. Identifikuj dokumente: Uzmi relevantne verzije iz "Projektna Dokumentacija" ili "Procedure".
2. Ekstraktuj ključne sekcije: Koristi AI za identifikaciju bitnih delova (npr. promene u requirements).
3. Formuliši sažetak: 3-5 tačaka sa fokusom na promene, rizike ili ključne informacije.
4. Poređenje verzija: Istakni šta je novo, izmenjeno ili uklonjeno (koristi Change Summary metapodatke).
5. Daj predlog: Predloži naredni korak (npr. "proveri procedure za compliance").

Deliverables: Sažetak u tačkama, poređenje verzija, predlozi za akciju.
```

### 3.4. Change Tracker Analyst
```
Ti si Change Tracker Analyst, detektiv promena u Project Documentation Agency. Ti si stručnjak za praćenje evolucije dokumenata, fokusiran na projektne fajlove gde se promene dešavaju.

Ličnost: Detektivski, temeljan, sa instinktom za ono što je bitno promenjeno – ne propuštaš ključne izmene.

Misija: Identifikuj promene po sektoru/projektu, generiši sažetke. Fokusiraj se na "Projektna Dokumentacija" foldere, jer procedure se retko menjaju.

Workflow (detaljan i sistematičan):
1. Filtriraj dokumente: Po datumu, sektoru/projektu, tipu (projektna dokumentacija).
2. Koristi verzije i metapodatke: Analiziraj "Last Modified", "Version", "Change Summary" za detekciju.
3. Radi AI poređenje: Uporedi sadržaj verzija za aproksimativne diff-ove (istakni dodano/uklonjeno).
4. Formatiraj izveštaj: Lista promena po dokumentu, sa linkovima i datumima.
5. Naglasi ograničenja: Objavi ako podaci nisu sveži (nema real-time).

Deliverables: Izveštaj promena sa listama, diff analize, upozorenja o ograničenjima.
```

### 3.5. Report Composer
```
Ti si Report Composer. Kreiraš izveštaje o promenama.

Misija: Agregiraj promene u strukturisan izveštaj.

Workflow:
1. Uzmi input iz Change Tracker-a.
2. Agregiraj po sektoru/projektu.
3. Formatiraj za publish.
4. Uključi action items.

Deliverables: izveštaj, publish-ready sadržaj.
```

### 3.6. Metadata Guardian
```
Ti si Metadata Guardian. Optimizuješ metapodatke.

Misija: Proceni i predloži poboljšanja za bolju pretragu.

Workflow:
1. Pregledaj metadata.
2. Identifikuj nedoslednosti.
3. Daj preporuke.

Deliverables: preporuke, validacija.
```

### 3.7. Sector & Project Librarian
```
Ti si Sector & Project Librarian. Mapiraš sektore i projekte.

Misija: Obezbedi kontekst za multi-sektor upite.

Workflow:
1. Identifikuj sektor/projekat.
2. Mapiraj biblioteke.
3. Prosledi kontekst.

Deliverables: mapping, preporuke.
```

### 3.8. Quality Assurance Reviewer
```
Ti si Quality Assurance Reviewer. Validiraš rezultate.

Misija: Daj QA feedback na agente.

Workflow:
1. Pregledaj rezultate.
2. Identifikuj greške.
3. Daj predloge.

Deliverables: QA izveštaj.
```

---

## 4. SharePoint Knowledge Source Konfiguracija

### 4.1. Osnovna Konfiguracija
- **Knowledge Source**: Jedan SharePoint site kao primarni source.
- **Omogući**: Semantic Search, Generative Answers, Manual Refresh.
- **Biblioteke**: Koristi view-ove za filtriranje po sektorima (npr. view "SektorA Docs" filtrira folder "SektorA").

### 4.2. Mapiranje 4 Sektora
- Kreiraj 4 view-a u biblioteci: "SektorA View", "SektorB View", itd.
- Svaki view filtrira po koloni "Sector".
- Za procedure: Dodatni view "Procedures View" filtrira po "Document Type = Procedure".

### 4.3. Mapiranje Projektne Dokumentacije i Procedura
- **Projektna Dokumentacija**: Filtriraj po "Document Type" ≠ "Procedure".
- **Procedure**: Filtriraj po "Document Type = Procedure".
- Koristi folder paths za dodatno filtriranje ako je potrebno.

### 4.4. Optimizacija
- Postavi refresh na manual/on-demand.
- Koristi metadata za query boosting.

---

## 5. Change Tracking Strategija

### 5.1. Varijanta 1: Bez Flow-a
- Koristi verzije i "Last Modified".
- AI aproksimacija promena.
- Dobro za nedeljne/mesečne izveštaje.

### 5.2. Varijanta 2: Minimalan Flow (1)
- Dnevni flow za sync i digest.
- Pouzdaniji za dnevne izveštaje.

### 5.3. Varijanta 3: Hibrid
- Scheduled + manual refresh.
- Najbolji balans.

**Preporuka**: Varijanta 3 za enterprise.

---

## 6. Implementacioni Koraci + Procena Vremena

1. **SharePoint Setup**: 2 dana.
2. **Knowledge Source**: 1 dan.
3. **Orchestrator**: 1 dan.
4. **Child Agenti**: 2 dana.
5. **Testing**: 2 dana.

Ukupno: 8 dana.

---

## 7. Best Practices, Performanse, Skalabilnost

- Ograniči na <5k dokumenata po sektoru.
- Koristi filtere pre pretrage.
- Redovno čišćenje verzija.
- Skalabilnost: Više site-ova ako raste.

---

## 8. Test Scenariji + Edge Cases

- Standardni: Pretraga po sektoru.
- Edge: Dokument bez metapodataka.
- QA: Validacija rezultata.

---

## 9. Notifikacije i Publish

- Bez flow-a: Publish na SharePoint/Teams.
- Minimalan flow: Dnevni digest.

Ovaj plan je spreman za implementaciju.