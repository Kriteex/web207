# README.md
# Madgicx MVP Dashboard

Jednoduchý MVP dashboard ve stylu Madgicx pro správu kampaní, metrik a doporučení pomocí AI.

## 🚀 Funkce
- Napojení na Meta Ads API (kampaně)
- Dashboard s metrikami (ROAS, spend, conversions)
- AI doporučení (škálovat / pauznout)
- Pravidla pro automatickou identifikaci slabých kampaní

## 📦 Tech Stack
- Backend: FastAPI + PostgreSQL
- Frontend: Streamlit
- AI: OpenAI GPT-4

## 🛠️ Jak spustit projekt

### 1. Klonuj repozitář
```bash
git clone https://github.com/uzivatel/madgicx-mvp-dashboard.git
cd madgicx-mvp-dashboard
```

### 2. Vytvoř virtuální prostředí a aktivuj ho
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Nainstaluj závislosti
```bash
pip install -r requirements.txt
```

### 4. Připrav `.env` soubor podle `.env.example`
```bash
cp .env.example .env
```

### 5. Spusť backend
```bash
uvicorn backend.main:app --reload
```

### 6. Spusť Streamlit frontend
```bash
streamlit run frontend/streamlit_app.py
```

---
