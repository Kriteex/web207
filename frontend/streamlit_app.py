# frontend/streamlit_app.py
import streamlit as st
import sys
import os
import json
from pathlib import Path
from PIL import Image
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns
import base64
from streamlit.components.v1 import html as st_html
import textwrap
from streamlit_extras.stylable_container import stylable_container

API_BASE = "http://localhost:8000"

def fetch_campaigns_via_api(include_insights: bool = False):
    # backend /campaigns param momentálně neřeší, takže ho neposíláme
    resp = requests.get(f"{API_BASE}/campaigns", timeout=60)
    resp.raise_for_status()
    return resp.json()

# Přesunutá mapa do frontendu
OBJECTIVE_OPTIMIZATION_MAP = {
    "OUTCOME_SALES": ["CONVERSIONS", "VALUE", "LANDING_PAGE_VIEWS"],
    "OUTCOME_TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
    "OUTCOME_ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES"],
    "OUTCOME_LEADS": ["LEAD_GENERATION", "CONVERSIONS"],
    "OUTCOME_APP_PROMOTION": ["APP_INSTALLS", "VALUE"],
    "OUTCOME_AWARENESS": ["REACH", "IMPRESSIONS"]
}

# Layout + sidebar
st.set_page_config(page_title="Madgicx MVP Dashboard", layout="wide")

# --- GLOBAL BUTTON STYLE (jednotný vzhled všech tlačítek) ---
GLOBAL_BTN_CSS = """
<style>
/* Všechna tlačítka Streamlitu */
.stButton > button,
.stDownloadButton > button,
div[data-testid="baseButton-secondary"] > button,
div[data-testid="baseButton-primary"] > button,
form button[type="submit"] {
    background: linear-gradient(90deg,#818cf8,#6366f1) !important;
    color: #ffffff !important;
    border: 0 !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,.25) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.2px;
    cursor: pointer;
    text-shadow: 0 0 2px rgba(0,0,0,.4);
}
.stButton > button:hover,
.stDownloadButton > button:hover,
form button[type="submit"]:hover {
    filter: brightness(1.12);
}
</style>
"""
st.markdown(GLOBAL_BTN_CSS, unsafe_allow_html=True)

st.sidebar.title("📊 Menu")
page = st.sidebar.radio("Vyber sekci", ["Ads Dashboard", "Ads Management", "Ads Library"])

# -------------------------
# ADS DASHBOARD
# -------------------------
if page == "Ads Dashboard":
    st.title("Madgicx MVP Dashboard – 📈 Ads Dashboard")

    def img_to_base64(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""  # fallback

    # --- CSS pro card ---
    SW_CSS = """
    <style>
    .sw-card{
      background:#1e1e2f;
      color:#fff;
      border-radius:16px;
      padding:18px 22px 16px 22px;
      font-family: sans-serif;
      box-shadow:0 2px 6px rgba(0,0,0,.2);
    }
    .sw-head{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:12px;
      font-size:16px;
      font-weight:600;
    }
    .sw-head .num{
      color:#818cf8;
    }
    .sw-avatars{
      display:flex;
      align-items:center;
    }
    .sw-avatars img{
      width:32px;height:32px;border-radius:50%;
      border:2px solid #1e1e2f;
      margin-left:-8px;
    }
    .sw-row{
      font-size:14px;
      margin:4px 0;
      line-height:1.2;
    }
    .sw-row span.time{
      color:#bbb;font-size:12px;font-style:italic;margin-left:4px;
    }
    .sw-progress-label{
      margin-top:14px;
      margin-bottom:6px;
      font-size:13px;
      font-weight:600;
    }
    .sw-progress-wrapper{
      position:relative;
      width:100%;
      height:10px;
      background:#3b3b4f;
      border-radius:6px;
      overflow:hidden;
    }
    .sw-progress-fill{
      position:absolute;
      height:100%;
      left:0;top:0;
      background:linear-gradient(90deg,#a78bfa,#6366f1);
    }
    .sw-progress-value{
      text-align:right;
      font-size:12px;
      margin-top:4px;
      color:#ccc;
    }
    </style>
    """

    # --- DATA ---
    people = [
        {
            "name": "Niklas",
            "action": "Set budget from $5,132 to $740",
            "time": "1 hour ago",
            "avatar": "frontend/media/avatars/niklas.jpg"
        },
        {
            "name": "Sophie",
            "action": "Set budget from $740 to $2,340",
            "time": "4 hours ago",
            "avatar": "frontend/media/avatars/sophie.jpg"
        },
        {
            "name": "Anna",
            "action": "No recent change",
            "time": "",
            "avatar": "frontend/media/avatars/anna.jpg"
        }
    ]

    automation_pct = 70  # procenta

    # --- RENDER ---
    left_box, right_space = st.columns([0.4, 0.6])

    with left_box:
        st.markdown(SW_CSS, unsafe_allow_html=True)

        # Avatary -> base64, aby se 100% vykreslily
        avatars_html = ""
        for p in people:
            b64 = img_to_base64(p["avatar"])
            if b64:
                avatars_html += f'<img src="data:image/jpeg;base64,{b64}"/>'

        rows_html = ""
        for p in people:
            rows_html += f'<div class="sw-row"><b>{p["name"]}</b> – {p["action"]}<span class="time">{p["time"]}</span></div>'

        box_html = f"""
        <div class="sw-card">
          <div class="sw-head">
            <div>Save work for <span class="num">{len(people)}</span> people</div>
            <div class="sw-avatars">{avatars_html}</div>
          </div>

          {rows_html}

          <div class="sw-progress-label">Percent of account automation</div>
          <div class="sw-progress-wrapper">
            <div class="sw-progress-fill" style="width:{automation_pct}%"></div>
          </div>
          <div class="sw-progress-value">{automation_pct}%</div>
        </div>
        """
        st.markdown(box_html, unsafe_allow_html=True)


    # ---------------- NEW: MONTHLY GOALS BOX (fixed) ----------------
    with right_space:
        MG_CSS = """
        <style>
        .mg-card{
          background:#1e1e2f;
          color:#fff;
          border-radius:16px;
          padding:18px 22px 16px 22px;
          font-family: sans-serif;
          box-shadow:0 2px 6px rgba(0,0,0,.2);
          margin-bottom:20px;
        }
        .mg-head{
          font-size:16px;
          font-weight:600;
          margin-bottom:12px;
          display:flex;
          align-items:center;
          gap:6px;
        }
        .mg-row{ margin:12px 0; }
        .mg-row-label{
          font-size:13px;
          color:#ddd;
          margin-bottom:4px;
          display:flex;
          justify-content:space-between;
        }
        .mg-bar{
          width:100%;height:10px;background:#3b3b4f;border-radius:6px;overflow:hidden;
        }
        .mg-fill{
          height:100%;background:linear-gradient(90deg,#34d399,#059669);
        }
        </style>
        """

        goals = [
            {"name": "Revenue", "current": 34500, "target": 50000, "fmt": "${:,.0f}"},
            {"name": "Spend",   "current": 18000, "target": 20000, "fmt": "${:,.0f}"},
            {"name": "ROAS",    "current": 1.92,  "target": 2.50,  "fmt": "{:,.2f}x"},
        ]

        rows = []
        for g in goals:
            pct = min(100, int((g["current"] / g["target"]) * 100)) if g["target"] else 0
            curr = g["fmt"].format(g["current"])
            targ = g["fmt"].format(g["target"])
            rows.append(
                f'<div class="mg-row">'
                f'  <div class="mg-row-label"><span>{g["name"]}</span>'
                f'  <span>{curr} / {targ} ({pct}%)</span></div>'
                f'  <div class="mg-bar"><div class="mg-fill" style="width:{pct}%"></div></div>'
                f'</div>'
            )
        rows_html = "".join(rows)

        mg_html = (
            MG_CSS +
            '<div class="mg-card">'
            '  <div class="mg-head">📅 Monthly Goals</div>'
            f'  {rows_html}'
            '</div>'
        )

        # použijeme komponentu, aby se nic neescapovalo
        st_html(mg_html, height=260, scrolling=False)
    # -------------- END MONTHLY GOALS BOX --------------

    # -------------- NEW: MAGICAL RECOMMENDATIONS BOX --------------
    # CSS (chip štítky atd.)
    RECS_CSS = """
    <style>
    .rec-chip{
      display:inline-block;
      background:#2d2d40;
      color:#c9c9ff;
      padding:2px 8px;
      border-radius:12px;
      font-size:10px;
      margin-right:4px;
      margin-top:2px;
    }
    .rec-row{
      padding:8px 0 10px 0;
      border-bottom:1px solid rgba(255,255,255,0.06);
    }
    .rec-title{
      font-size:14px;
      font-weight:600;
      margin-bottom:2px;
    }
    .rec-why{
      font-size:12px;
      color:#bbb;
      margin-bottom:4px;
    }
    </style>
    """

    st.markdown(RECS_CSS, unsafe_allow_html=True)

    # Demo data – později nahradíš voláním AI / backendu
    if "dismissed_recs" not in st.session_state:
        st.session_state["dismissed_recs"] = set()

    recommendations = [
        {
            "title": "Increase budget on top 3 ROAS ad sets",
            "why":  "ROAS > 3.0, but spend < 20% of daily budget. Estimated +12% revenue.",
            "tags": ["Budget", "Meta", "ROAS"],
            "action_key": "launch_budget"
        },
        {
            "title": "Pause low CTR creatives",
            "why":  "CTR < 0.7% for 5 days. Reallocate spend to higher CTR assets.",
            "tags": ["Creative", "CTR", "Optimization"],
            "action_key": "pause_creatives"
        },
        {
            "title": "Test new hook for Summer sale",
            "why":  "Engagement down 18% WoW on primary audience. Add fresh intro line.",
            "tags": ["Copywriting", "Seasonal", "Idea"],
            "action_key": "test_hook"
        }
    ]

    with stylable_container(
        key="recs_card",
        css_styles="""
        {
          background:#1e1e2f;
          color:#fff;
          border-radius:16px;
          padding:18px 22px 16px 22px;
          box-shadow:0 2px 6px rgba(0,0,0,.2);
          margin-top:20px;
          font-family:sans-serif;
        }
        """
    ):
        st.markdown("### ✨ Magical Recommendations")

        # Render každé doporučení
        for i, rec in enumerate(recommendations):
            if i in st.session_state["dismissed_recs"]:
                continue  # přeskoč už skryté

            c1, c2 = st.columns([0.82, 0.18], vertical_alignment="center")
            with c1:
                st.markdown(f"<div class='rec-row'>", unsafe_allow_html=True)
                st.markdown(f"<div class='rec-title'>{rec['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rec-why'>{rec['why']}</div>", unsafe_allow_html=True)
                tags_html = " ".join([f"<span class='rec-chip'>{t}</span>" for t in rec["tags"]])
                st.markdown(tags_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                launch = st.button("Launch", key=f"rec_launch_{i}")
                dismiss = st.button("✖", key=f"rec_dismiss_{i}")

                if launch:
                    st.success(f"Launched: {rec['title']}")
                    # TODO: zavolej backend akci / AI engine
                if dismiss:
                    st.session_state["dismissed_recs"].add(i)
                    st.experimental_rerun()

        st.markdown("---")
        ask_more = st.button("Ask AI marketer to do more", key="ask_ai_marketer")
        if ask_more:
            st.info("TODO: Trigger AI marketer – pošli prompt na backend/AI engine.")
    # -------------- END MAGICAL RECOMMENDATIONS BOX --------------


    # -------------- CAMPAIGNS --------------------------
    with stylable_container(
        key="camp_card",
        css_styles="""
        {
          background:#1e1e2f;
          color:#fff;
          border-radius:16px;
          padding:18px 22px 20px 22px;
          box-shadow:0 2px 6px rgba(0,0,0,.2);
          margin-top:20px;
          font-family:sans-serif;
        }
        """
    ):

        st.markdown("""
        <style>
        #camp_card .col-title, 
        #camp_card .col-button{
            display:flex;
            align-items:center;   /* vertikální zarovnání na střed */
            height:38px;          /* cca výška tlačítka */
        }
        #camp_card .col-title h3{
            margin:0 !important;
            line-height:38px;     /* stejné jako výška tlačítka */
        }
        </style>
        """, unsafe_allow_html=True)


        # ------------------------------------------

        head_l, head_r = st.columns([0.82, 0.18])
        with head_l:
            st.markdown('<div class="col-title"><h3>📦 Campaigns</h3></div>', unsafe_allow_html=True)
        with head_r:
            st.markdown('<div class="col-button">', unsafe_allow_html=True)
            refresh_clicked = st.button("↻ Refresh", key="load_campaigns_button", type="primary")
            st.markdown('</div>', unsafe_allow_html=True)


        # --- původní logika beze změny ---
        if "campaigns_data" not in st.session_state:
            st.session_state["campaigns_data"] = None

        if refresh_clicked:
            with st.spinner("Načítám kampaně…"):
                try:
                    st.session_state["campaigns_data"] = fetch_campaigns_via_api(include_insights=True)
                except Exception as e:
                    st.error("Nepodařilo se načíst kampaně.")
                    st.exception(e)

        if st.session_state["campaigns_data"]:
            display_campaigns(st.session_state["campaigns_data"])
        # ---------------------------------



# -------------------------
# ADS MANAGEMENT
# -------------------------
elif page == "Ads Management":
    st.title("Madgicx MVP Dashboard – ⚙️ Ads Management")

    st.markdown("---")
    st.subheader("🚀 Vytvořit novou kampaň")

    with st.form("create_campaign_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="campaign_account")
        campaign_name = st.text_input("Název kampaně", key="campaign_name")
        objective = st.selectbox("Cíl kampaně", list(OBJECTIVE_OPTIMIZATION_MAP.keys()), key="campaign_objective")
        status = st.selectbox("Stav", ["PAUSED", "ACTIVE"], key="campaign_status")
        special_ad_categories = st.multiselect(
            "Special Ad Categories (např. HOUSING, EMPLOYMENT, CREDIT)",
            ["NONE", "HOUSING", "EMPLOYMENT", "CREDIT"],
            default=["NONE"],
            key="campaign_special"
        )
        submit_campaign = st.form_submit_button("Vytvořit kampaň")

        if submit_campaign:
            res = requests.post(
                "http://localhost:8000/create_campaign",
                json={
                    "account_id": account_id,
                    "name": campaign_name,
                    "objective": objective,
                    "status": status,
                    "special_ad_categories": [] if "NONE" in special_ad_categories else special_ad_categories
                }
            )
            if res.status_code == 200:
                st.success(f"Kampaň vytvořena: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("📦 Vytvořit nový Ad Set")

    # Dynamické UI s rerenderem mimo form kvůli aktualizaci valid_goals
    selected_objective = st.selectbox("Objective kampaně pro ad set", list(OBJECTIVE_OPTIMIZATION_MAP.keys()), key="adset_objective")
    valid_goals = OBJECTIVE_OPTIMIZATION_MAP.get(selected_objective, [])

    with st.form("create_adset_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="adset_account")
        campaign_id = st.text_input("Campaign ID", key="adset_campaign")
        adset_name = st.text_input("Název Ad Setu", key="adset_name")
        daily_budget = st.number_input("Denní rozpočet (v centích)", min_value=100, key="adset_budget")
        billing_event = st.selectbox("Billing Event", ["IMPRESSIONS", "CLICKS", "LINK_CLICKS"], key="adset_billing")
        country = st.text_input("Země cílení (např. US)", value="US", key="adset_country")
        optimization_goal = st.selectbox("Optimalizační cíl", valid_goals, key="adset_optimization")
        bid_amount = st.number_input("Bid Amount (v centích)", min_value=1, key="adset_bid")

        submit_adset = st.form_submit_button("Vytvořit Ad Set")

        if submit_adset:
            res = requests.post(
                "http://localhost:8000/create_adset",
                json={
                    "account_id": account_id,
                    "campaign_id": campaign_id,
                    "name": adset_name,
                    "daily_budget": daily_budget,
                    "optimization_goal": optimization_goal,
                    "billing_event": billing_event,
                    "bid_amount": bid_amount,
                    "targeting": {
                        "geo_locations": {"countries": [country]}
                    },
                    "status": "PAUSED"
                }
            )
            if res.status_code == 200:
                st.success(f"Ad Set vytvořen: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("🎨 Vytvořit Ad Creative (přes object_story_spec s image_url)")

    with st.form("create_creative_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="creative_account")
        creative_name = st.text_input("Název Creativu", key="creative_name")
        page_id = st.text_input("Page ID", key="creative_page_id")
        message = st.text_area("Text reklamy", key="creative_message")
        image_url = st.text_input("Obrázek (URL)", key="creative_image")

        submit_creative = st.form_submit_button("Vytvořit Creative")

        if submit_creative:
            payload = {
                "account_id": account_id,
                "name": creative_name,
                "object_story_spec": {
                    "page_id": page_id,
                    "link_data": {
                        "message": message,
                        "link": "https://example.com",
                        "image_url": image_url
                    }
                }
            }
            res = requests.post("http://localhost:8000/create_creative", json=payload)
            if res.status_code == 200:
                st.success(f"Creative vytvořen: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("📢 Vytvořit Ad")

    with st.form("create_ad_form"):
        adset_id = st.text_input("Ad Set ID", key="ad_adset_id")
        ad_name = st.text_input("Název reklamy", key="ad_name")
        creative_id = st.text_input("Creative ID", key="ad_creative_id")
        status = st.selectbox("Stav", ["PAUSED", "ACTIVE"], key="ad_status")

        submit_ad = st.form_submit_button("Vytvořit Ad")

        if submit_ad:
            payload = {
                "adset_id": adset_id,
                "name": ad_name,
                "creative_id": creative_id,
                "status": status
            }
            res = requests.post("http://localhost:8000/create_ad", json=payload)
            if res.status_code == 200:
                st.success(f"Reklama vytvořena: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("🖼️ Upload obrázku pro reklamu")

    with st.form("upload_image_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="upload_account")
        image_file = st.file_uploader("Vyber obrázek (JPG/PNG)", type=["jpg", "jpeg", "png"], key="upload_image")
        submit_upload = st.form_submit_button("Nahrát obrázek")

        if submit_upload and image_file is not None:
            files = {'file': (image_file.name, image_file.getvalue(), image_file.type)}
            data = {'account_id': account_id}
            res = requests.post("http://localhost:8000/upload_ad_image", files=files, data=data)
            if res.status_code == 200:
                images = res.json().get("images", {})
                if images:
                    image_hash = list(images.values())[0].get("hash", "Nezískán")
                    st.success(f"Nahráno. Hash: {image_hash}")
                else:
                    st.error(f"Chyba: Obrázek nebyl nahrán. Odpověď: {res.json()}")
                    image_hash = "Nezískán"
                st.success(f"Obrázek nahrán. Hash: `{image_hash}`")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("🎨 Vytvořit Ad Creative (přes image_hash – link ad)")

    with st.form("create_adcreative_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="adcreative_account")
        creative_name = st.text_input("Název Creativu", key="adcreative_name")
        title = st.text_input("Titulek reklamy", key="adcreative_title")
        body = st.text_area("Text reklamy", key="adcreative_body")
        object_url = st.text_input("Cílový odkaz (např. https://example.com)", key="adcreative_url")
        image_hash = st.text_input("Image Hash (z předchozího kroku)", key="adcreative_hash")

        submit_creative = st.form_submit_button("Vytvořit Ad Creative")

        if submit_creative:
            res = requests.post("http://localhost:8000/create_adcreative", json={
                "account_id": account_id,
                "name": creative_name,
                "title": title,
                "body": body,
                "object_url": object_url,
                "image_hash": image_hash
            })

            if res.status_code == 200:
                if "id" in res.json():
                    st.success(f"Creative vytvořen: ID {res.json()['id']}")
                else:
                    st.error("Chyba při vytváření Creativu:")
                    st.code(res.json(), language="json")
            else:
                st.error(f"Chyba: {res.text}")

# -------------------------
# ADS LIBRARY
# -------------------------


elif page == "Ads Library":
    st.markdown("## 🎞️ Ads Library – Galerie")

    media_dir = os.path.join("frontend", "media", "ads")
    allowed_extensions = [".mp4", ".jpg", ".jpeg", ".png"]

    files = [
        f for f in os.listdir(media_dir)
        if os.path.splitext(f)[1].lower() in allowed_extensions
    ]

    # --- Rozdělení podle prefixu názvu (case-insensitive) ---
    products = [f for f in files if os.path.basename(f).lower().startswith("product")]
    avatars  = [f for f in files if os.path.basename(f).lower().startswith("avatar")]
    others   = [f for f in files if f not in products and f not in avatars]

    # --- CSS: zachování "flex" feelingu (žádné mezery) ---
    st.markdown("""
        <style>
        div[data-testid="column"] { padding: 0 !important; }
        video, img {
            width: 100% !important;
            height: auto !important;
            margin-bottom: -4px;
            display: block;
        }
        .section-title{
            margin: 22px 0 10px 0;
            font-weight: 600;
            font-size: 18px;
            color: #fff;
        }
        </style>
    """, unsafe_allow_html=True)

    def render_grid(file_list, cols=4):
        if not file_list:
            return
        # vytvoříme 4 vertikální sloupce a “sypeme” do nich soubory postupně
        columns = st.columns(cols)
        for idx, fname in enumerate(sorted(file_list)):
            col = columns[idx % cols]
            fpath = os.path.join(media_dir, fname)
            ext = os.path.splitext(fname)[1].lower()
            with col:
                with st.container():
                    if ext == ".mp4":
                        with open(fpath, "rb") as f:
                            st.video(f.read())
                    else:
                        with open(fpath, "rb") as f:
                            st.image(f.read())

    # --- Sekce PRODUCTS ---
    if products:
        st.markdown("<div class='section-title'>🛍️ Products</div>", unsafe_allow_html=True)
        render_grid(products)
        st.markdown("---")

    # --- Sekce AVATARS ---
    if avatars:
        st.markdown("<div class='section-title'>👤 Avatars</div>", unsafe_allow_html=True)
        render_grid(avatars)
        st.markdown("---")

    # --- Sekce OTHERS ---
    if others:
        st.markdown("<div class='section-title'>📦 Others</div>", unsafe_allow_html=True)
        render_grid(others)
