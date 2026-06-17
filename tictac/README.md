# Piškvorky – Multiplayer Arcade

Jednoduchá multiplayer hra piškvorky postavená na **Flask + Flask-SocketIO**
(backend, real-time cez WebSockety) a čistom **HTML/CSS/JS** frontende.

## Ako to funguje

- Keď sa pripojí prvý hráč, čaká v "miestnosti" na súpera.
- Druhý hráč sa automaticky napáruje s prvým a hra začne (hráč 1 = X, hráč 2 = O).
- Ťahy sa odosielajú cez WebSocket (Socket.IO) a obaja hráči vidia zmeny okamžite.
- Po skončení hry sa zobrazí tlačidlo **Nová hra**, ktoré reštartuje plochu
  pre obe pripojené strany.
- Stav hry sa drží len v pamäti servera (žiadna databáza) – stačí pre jednu
  bežiacu instanciu. Pri reštarte servera sa rozohraté hry stratia.

## Lokálne spustenie

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Aplikácia pobeží na `http://localhost:5000`. Otvor si ju v **dvoch
rôznych oknách/prehliadačoch** (alebo jedno normálne, druhé v anonymnom
režime), aby si simuloval dvoch hráčov.

## Nasadenie na Render.com

### Možnosť A – cez `render.yaml` (Blueprint)

1. Nahraj tento priečinok do GitHub repozitára.
2. Na [render.com](https://render.com) klikni na **New > Blueprint**.
3. Vyber repozitár – Render automaticky nájde `render.yaml` a nastaví
   build/start príkazy.
4. Klikni **Apply** a počkaj na deploy.

### Možnosť B – manuálne

1. Nahraj projekt do GitHub repozitára.
2. Na Render klikni na **New > Web Service** a vyber repozitár.
3. Nastav:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -k eventlet -w 1 app:app`
4. Deploy.

> **Dôležité:** kvôli WebSocketom musí beh používať `eventlet` worker
> (`-k eventlet`) a iba **1 worker process** (`-w 1`), inak by hráči mohli
> skončiť na rôznych procesoch a nevideli by sa navzájom. Toto je už
> nastavené v `Procfile` aj v `render.yaml`.

## Štruktúra projektu

```
.
├── app.py              # Flask + Socket.IO backend, herná logika
├── requirements.txt    # Python závislosti
├── Procfile             # spúšťací príkaz pre Render/Heroku
├── render.yaml          # voliteľný Render Blueprint
├── templates/
│   └── index.html       # HTML stránka
└── static/
    ├── style.css         # neónový arkádový štýl
    └── script.js         # klientská Socket.IO logika
```

## Možné vylepšenia

- Vlastné herné kódy (room kódy), aby sa hráči mohli pripojiť k presnej miestnosti.
- Viac ako 2 hráči naraz (čakacia rada/spectator mód).
- Ukladanie skóre/historie do databázy (napr. Redis na Render).
