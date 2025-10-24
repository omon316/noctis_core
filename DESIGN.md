# NoctisCore Dashboard - Design Spezifikation

**Master-Referenz für alle Design-Entscheidungen**  
Erstellt: 22.10.2025  
Style: Palantir Gotham (Tactical/Military)

---

## 🎨 Farbpalette

### Primäre Farben:
```css
--bg-primary: #000000        /* Haupthintergrund - reines Schwarz */
--bg-secondary: #0a0a0a      /* Sidebar, Top-Nav - sehr dunkel */
--bg-tertiary: #1a1a1a       /* Cards, Hover-States */
--bg-elevated: #252525       /* Elevated Elements */
```

### Border & Lines:
```css
--border-primary: #333333    /* Standard-Borders */
--border-accent: #00d4ff     /* Aktive/Hover-Borders */
```

### Text:
```css
--text-primary: #e0e0e0      /* Haupttext - hell */
--text-secondary: #a0a0a0    /* Sekundärer Text */
--text-muted: #666666        /* Muted/Disabled Text */
```

### Akzente:
```css
--accent-cyan: #00d4ff       /* Primär-Akzent (Gotham-Blau) */
--accent-green: #00ff9f      /* Success/Online */
--accent-red: #ff3366        /* Error/Watchlist */
--accent-yellow: #ffd700     /* Warning/RF */
```

---

## 📐 Layout-Struktur

### Gesamt-Layout:
```
┌─────────────────────────────────────────────────────────┐
│  TOP NAVIGATION (50px)                                  │
│  [Logo] [HOME|SCAN|STATS|MAP|...] [Search] [🔔] [⚙️]   │
├────────────┬────────────────────────────────────────────┤
│  SIDEBAR   │  MAIN CONTENT                              │
│  (280px)   │                                            │
│            │  ┌─ Header ──────────────────────┐        │
│  Filters   │  │ Title          [Buttons]      │        │
│  Sections  │  └───────────────────────────────┘        │
│            │                                            │
│            │  ┌─ Scanner Cards ───────────────┐        │
│            │  │ [BT] [WiFi] [RF]              │        │
│            │  └───────────────────────────────┘        │
│            │                                            │
│            │  ┌─ Device Table ────────────────┐        │
│            │  │                                │        │
│            │  └───────────────────────────────┘        │
└────────────┴────────────────────────────────────────────┘
```

### Top Navigation:
- **Höhe:** 50px
- **Background:** `#0a0a0a`
- **Border-Bottom:** 1px solid `#333`
- **Shadow:** `0 2px 8px rgba(0,0,0,0.8)`

**Elemente:**
1. **Logo** (links)
   - 2 Kreise SVG-Icon (cyan)
   - Text: "NOCTIS" + "CORE" (cyan)
   - Font-Size: 1rem
   - Letter-Spacing: 0.15em

2. **Horizontale Navigation** (center)
   - Items: HOME, SCAN, STATS, MAP, LOGS, WATCH, EXPORT, AI
   - Font-Size: 0.75rem
   - Letter-Spacing: 0.1em
   - Border-Right zwischen Items
   - Active: cyan bottom-border (2px)

3. **Rechte Seite** (right)
   - Suchfeld (280px)
   - Notification Bell (mit Badge)
   - Settings Icon

### Sidebar (Links):
- **Breite:** 280px
- **Background:** `#0a0a0a`
- **Border-Right:** 1px solid `#333`
- **Padding:** 1.5rem 1rem

**Sections:**
1. Quick Scan (Button)
2. Time Range (Checkboxen)
3. Scanner Type (Checkboxen)
4. Device Type (Checkboxen)
5. Status (Status-LEDs)
6. System Info (klein)

### Main Content:
- **Padding:** 2rem
- **Background:** `#000`

**Header:**
- Title: 1.5rem, letter-spacing 0.1em
- Action Buttons rechts
- Border-Bottom: 1px solid `#333`

---

## 🔲 Komponenten

### Scanner Cards:
```css
Background: #0a0a0a
Border: 1px solid #333
Border-Radius: 2px (sehr wenig!)
Padding: 1.5rem
Hover: cyan border + shadow
```

**Card-Icon:**
- 50x50px
- Border-Radius: 2px
- Background: rgba(accent, 0.1)
- Border: 1px solid rgba(accent, 0.3)

**Card-Stats:**
- Grid: 3 Spalten
- Label: 0.65rem, muted
- Value: 1.2rem, cyan, bold

### Buttons:

**Primary (Cyan):**
```css
Background: #00d4ff
Color: #000
Border: 1px solid #00d4ff
Hover: transparent bg, cyan text + glow
```

**Secondary:**
```css
Background: transparent
Color: #e0e0e0
Border: 1px solid #333
Hover: #1a1a1a bg, cyan border
```

**Disabled:**
```css
Opacity: 0.3
Cursor: not-allowed
```

### Checkboxen (Filter):
```css
Size: 14x14px
Border: 1px solid #333
Border-Radius: 2px
Checked: cyan bg + checkmark
Hover: cyan border
```

### Status-LEDs:
```css
Size: 8px diameter
Border-Radius: 50%
Box-Shadow: 0 0 6px (same color)

Colors:
- Green: #00ff9f (Online)
- Gray: #666 (Inactive, no shadow)
- Red: #ff3366 (Watchlist)
```

### Table:
```css
Background: #0a0a0a
Border: 1px solid #333
Border-Radius: 2px

Header:
- Background: #1a1a1a
- Font-Size: 0.7rem
- Letter-Spacing: 0.1em
- Color: #666
- Padding: 1rem

Rows:
- Padding: 1rem
- Font-Size: 0.8rem
- Border-Bottom: 1px solid #333
- Hover: #1a1a1a bg
```

---

## ✍️ Typografie

**Font-Family:**
```css
'Consolas', 'Monaco', 'Courier New', monospace
```

**Font-Sizes:**
- Page Title: 1.5rem
- Section Title: 1rem
- Card Title: 0.9rem
- Nav Items: 0.75rem
- Body Text: 0.8rem
- Sidebar Labels: 0.7rem
- Small Text: 0.65rem

**Letter-Spacing:**
- Titles: 0.1em - 0.15em
- Uppercase Text: 0.05em - 0.1em

**Font-Weights:**
- Bold: 700
- Normal: 600 (für Labels)
- Regular: 400

---

## 🎭 Design-Prinzipien

### 1. **Scharfe Kanten**
- Border-Radius: **2px maximum** (fast keine Rundungen!)
- Keine weichen Schatten
- Präzise Linien

### 2. **Kontrast**
- Schwarz vs. Cyan
- Hell vs. Dunkel
- Keine Grautöne dazwischen

### 3. **Minimalismus**
- Keine unnötigen Elemente
- Alles hat eine Funktion
- Clean & Technical

### 4. **Tactical Feel**
- Military/Security-Look
- Geometrische Icons
- Status-LEDs statt Text
- Monospace Font

### 5. **Information Density**
- Viele Infos auf wenig Raum
- Aber nicht überladen
- Hierarchie durch Größe/Farbe

---

## 🚫 Was NICHT zu tun ist

❌ **Keine runden Ecken** (außer Status-LEDs)  
❌ **Keine bunten Farben** (nur schwarz + 4 Akzente)  
❌ **Keine weichen Schatten** (nur harte box-shadows)  
❌ **Keine Comic-Sans** (nur Monospace!)  
❌ **Keine Emojis** (nur geometrische Icons)  
❌ **Keine Animationen** (außer hover-transitions)  

---

## 📸 Screenshots

**Original Mockup:**
- Siehe Chat: dashboard2
- Datum: 21.10.2025
- Design by: Claude + User

---

## 🔄 Versionen

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | 22.10.2025 | Initial Design |
| 1.1 | 22.10.2025 | Korrektur nach falscher Implementierung |

---

## 📝 Verwendung

**Diese Datei ist die MASTER-REFERENZ!**

Bei JEDER Design-Änderung:
1. ✅ Prüfe diese Datei
2. ✅ Halte dich an die Specs
3. ✅ Update diese Datei bei Änderungen

**Für neue Features:**
- Benutze bestehende Komponenten
- Falls neue Components nötig: dokumentiere hier!

---

## 🎯 Quick Reference

```css
/* Copy-Paste für neue Components */

/* Standard Card */
.card {
    background: #0a0a0a;
    border: 1px solid #333;
    border-radius: 2px;
    padding: 1.5rem;
    transition: all 0.2s;
}

.card:hover {
    border-color: #00d4ff;
    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);
}

/* Standard Button */
.btn {
    padding: 0.75rem 1.5rem;
    font-family: 'Consolas', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s;
}

/* Standard Input */
.input {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 2px;
    color: #e0e0e0;
    font-family: 'Consolas', monospace;
    padding: 0.75rem;
    outline: none;
}

.input:focus {
    border-color: #00d4ff;
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.1);
}
```

---

**Ende der Design-Spezifikation**  
Bei Fragen: Siehe diese Datei!
