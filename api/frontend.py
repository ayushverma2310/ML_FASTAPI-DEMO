"""
Premium Category Estimator — Streamlit frontend for the FastAPI model service.

Just run this:  streamlit run frontend.py

The uvicorn backend (app:app) is started automatically on first load if it
isn't already listening. To run it yourself instead, start it before this:
    uvicorn app:app --reload
"""

import atexit
import json
import os
import subprocess
import sys
import time

import requests
import streamlit as st

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

DEFAULT_API = "http://127.0.0.1:8000/"

# The uvicorn target: <module>:<FastAPI instance>. Your file is app.py and the
# instance inside it is called `app`, hence "app:app".
API_MODULE = "app:app"
API_HOST = "127.0.0.1"
API_PORT = 8000
API_STARTUP_TIMEOUT = 30.0  # seconds — model.pkl unpickling can be slow

TIER_1_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
]

TIER_2_CITIES = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam",
    "Coimbatore", "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur",
    "Raipur", "Amritsar", "Varanasi", "Agra", "Dehradun", "Mysore", "Jabalpur",
    "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik", "Allahabad", "Udaipur",
    "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode",
    "Warangal", "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol",
    "Siliguri",
]

OCCUPATIONS = [
    "student", "freelancer", "private_job", "government_job",
    "business_owner", "unemployed", "retired",
]

st.set_page_config(
    page_title="Premium Category Estimator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------------------------------
# Backend lifecycle — start uvicorn if nothing is already serving
# --------------------------------------------------------------------------

def _api_is_up(base_url: str, timeout: float = 1.0) -> bool:
    """True if something answers on the API's docs endpoint."""
    try:
        requests.get(f"{base_url.rstrip('/')}/docs", timeout=timeout)
        return True
    except requests.exceptions.RequestException:
        return False


@st.cache_resource(show_spinner=False)
def ensure_api_running() -> dict:
    """
    Start the FastAPI backend as a child process, once per Streamlit session.

    @st.cache_resource is load-bearing: Streamlit re-executes this whole script
    on every widget interaction, and without the cache we'd spawn a new uvicorn
    on every click — all of which would die on "address already in use".

    Returns a small status dict so the sidebar can report what happened.
    """
    base = f"http://{API_HOST}:{API_PORT}"

    if _api_is_up(base):
        return {"state": "external", "pid": None}

    here = os.path.dirname(os.path.abspath(__file__))

    try:
        proc = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", API_MODULE,
                "--host", API_HOST,
                "--port", str(API_PORT),
                # Deliberately NO --reload: the reloader forks a child, so
                # terminating the parent would orphan a process still holding
                # port 8000.
            ],
            cwd=here,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError as exc:
        return {"state": "failed", "pid": None, "error": str(exc)}

    atexit.register(_shutdown, proc)

    deadline = time.time() + API_STARTUP_TIMEOUT
    while time.time() < deadline:
        if proc.poll() is not None:  # died during startup
            output = proc.stdout.read() if proc.stdout else ""
            return {
                "state": "failed",
                "pid": None,
                "error": output[-2000:] or f"uvicorn exited with code {proc.returncode}",
            }
        if _api_is_up(base):
            return {"state": "started", "pid": proc.pid}
        time.sleep(0.4)

    _shutdown(proc)
    return {
        "state": "failed",
        "pid": None,
        "error": f"API did not become reachable within {API_STARTUP_TIMEOUT:.0f}s.",
    }


def _shutdown(proc: subprocess.Popen) -> None:
    """Terminate the backend, escalating to kill if it ignores us."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


api_status = ensure_api_running()


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --paper:  #F4F5F0;
    --ink:    #14181A;
    --pine:   #245A4A;
    --ochre:  #C89B3C;
    --rule:   #D3D6CD;
    --muted:  #6B7472;
}

.stApp { background: var(--paper); }

/* kill Streamlit's default top padding so the masthead sits high */
.block-container { padding-top: 2.2rem; max-width: 1180px; }

h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; color: var(--ink); }
body, p, label, .stMarkdown { font-family: 'Inter', system-ui, sans-serif; color: var(--ink); }

/* ---------- masthead ---------- */
.masthead {
    border-bottom: 1px solid var(--ink);
    padding-bottom: 14px;
    margin-bottom: 26px;
}
.masthead .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--pine);
    margin-bottom: 6px;
}
.masthead h1 {
    font-size: 42px !important;
    font-weight: 300 !important;
    line-height: 1.05;
    margin: 0 0 6px 0 !important;
    letter-spacing: -0.02em;
}
.masthead h1 em { font-style: italic; color: var(--pine); }
.masthead .sub {
    font-size: 14px;
    color: var(--muted);
    max-width: 62ch;
}

/* ---------- section labels ---------- */
.sec {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6px;
    margin: 4px 0 14px 0;
}

/* ---------- derived-field panel (the signature) ---------- */
.derive {
    background: #FFFFFF;
    border: 1px solid var(--rule);
    border-left: 3px solid var(--ochre);
    padding: 18px 20px 6px 20px;
}
.derive .head {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ochre);
    margin-bottom: 2px;
}
.derive .note {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 16px;
    line-height: 1.5;
}
.row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 9px 0;
    border-bottom: 1px dotted var(--rule);
}
.row:last-child { border-bottom: none; }
.row .k {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--muted);
}
.row .v {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 15px;
    font-weight: 500;
    color: var(--ink);
}
.row .v.hi   { color: #A8322D; }
.row .v.med  { color: #B87A18; }
.row .v.lo   { color: var(--pine); }

/* ---------- result ---------- */
.result {
    background: var(--pine);
    color: #F4F5F0;
    padding: 26px 28px;
    margin-top: 4px;
}
.result .k {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    opacity: 0.72;
    margin-bottom: 8px;
}
.result .v {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 46px;
    font-weight: 600;
    line-height: 1;
    text-transform: capitalize;
    letter-spacing: -0.01em;
}
.awaiting {
    border: 1px dashed var(--rule);
    padding: 26px 28px;
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--muted);
}

/* ---------- buttons ---------- */
.stButton > button {
    background: var(--ink);
    color: var(--paper);
    border: none;
    border-radius: 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 12px 0;
    width: 100%;
    transition: background 120ms ease;
}
.stButton > button:hover { background: var(--pine); color: #FFFFFF; }
.stButton > button:focus-visible { outline: 2px solid var(--ochre); outline-offset: 2px; }

/* ---------- inputs ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 0 !important;
    border-color: var(--rule) !important;
    font-family: 'Inter', sans-serif;
}
label { font-size: 13px !important; font-weight: 500 !important; }

footer, #MainMenu { visibility: hidden; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Derivations — mirrors the @computed_field logic in the API's Pydantic model
# --------------------------------------------------------------------------

def derive_bmi(weight: float, height: float) -> float:
    return weight / (height ** 2)


def derive_age_group(age: int) -> str:
    if age < 25:
        return "young"
    if age < 45:
        return "adult"
    if age < 60:
        return "middle_aged"
    return "senior"


def derive_city_tier(city: str) -> int:
    if city in TIER_1_CITIES:
        return 1
    if city in TIER_2_CITIES:
        return 2
    return 3


def derive_lifestyle_risk(smoker: bool, bmi: float) -> str:
    if smoker and bmi > 30:
        return "high"
    if smoker and bmi > 27:
        return "medium"
    return "low"


# --------------------------------------------------------------------------
# Masthead
# --------------------------------------------------------------------------

st.markdown(
    """
    <div class="masthead">
        <div class="eyebrow">Model service · premium banding</div>
        <h1>What band does this <em>applicant</em> fall into?</h1>
        <div class="sub">
            Enter the seven details the model was trained on. The four fields it actually
            reads are derived from those — you can watch them resolve on the right before
            you send anything.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("**Connection**")
    api_base = st.text_input("API base URL", DEFAULT_API)

    if api_status["state"] == "started":
        st.success(f"Backend started automatically (pid {api_status['pid']}).")
    elif api_status["state"] == "external":
        st.info("Using a backend that was already running.")
    else:
        st.error("Couldn't start the backend automatically.")
        st.caption("Start it yourself with: `uvicorn app:app --reload`")
        with st.expander("Startup output"):
            st.code(api_status.get("error", "unknown error"))

    st.caption("Point this at wherever uvicorn is serving the FastAPI app.")

left, right = st.columns([1.15, 1], gap="large")


# --------------------------------------------------------------------------
# Input column
# --------------------------------------------------------------------------

with left:
    st.markdown('<div class="sec">Applicant details</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", min_value=1, max_value=119, value=30, step=1)
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0, step=0.5)
    with c2:
        height = st.number_input(
            "Height (m)", min_value=0.5, max_value=2.5, value=1.72, step=0.01,
            help="In metres — 1.72, not 172.",
        )
        income_lpa = st.number_input(
            "Annual income (₹ lakh)", min_value=0.1, value=12.0, step=0.5,
        )

    c3, c4 = st.columns(2)
    with c3:
        occupation = st.selectbox("Occupation", OCCUPATIONS, index=2)
    with c4:
        smoker_choice = st.radio("Smoker", ["No", "Yes"], horizontal=True)
        smoker = smoker_choice == "Yes"

    all_cities = sorted(TIER_1_CITIES + TIER_2_CITIES)
    city_pick = st.selectbox(
        "City", all_cities + ["Somewhere else…"],
        index=all_cities.index("Ranchi") if "Ranchi" in all_cities else 0,
    )
    if city_pick == "Somewhere else…":
        city = st.text_input("City name", placeholder="Type the city")
    else:
        city = city_pick

    st.write("")
    submitted = st.button("Estimate premium category")


# --------------------------------------------------------------------------
# Derived + result column
# --------------------------------------------------------------------------

bmi = derive_bmi(weight, height)
age_group = derive_age_group(age)
city_tier = derive_city_tier(city) if city else 3
risk = derive_lifestyle_risk(smoker, bmi)
risk_class = {"high": "hi", "medium": "med", "low": "lo"}[risk]

with right:
    st.markdown('<div class="sec">What the model receives</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="derive">
            <div class="head">Derived fields</div>
            <div class="note">
                Computed the same way the API computes them, so this preview and the
                prediction always agree.
            </div>
            <div class="row"><span class="k">bmi</span>
                <span class="v">{bmi:.1f}</span></div>
            <div class="row"><span class="k">age_group</span>
                <span class="v">{age_group}</span></div>
            <div class="row"><span class="k">city_tier</span>
                <span class="v">{city_tier}</span></div>
            <div class="row"><span class="k">lifestyle_risk</span>
                <span class="v {risk_class}">{risk}</span></div>
            <div class="row"><span class="k">income_lpa</span>
                <span class="v">{income_lpa:.1f}</span></div>
            <div class="row"><span class="k">occupation</span>
                <span class="v">{occupation}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown('<div class="sec">Prediction</div>', unsafe_allow_html=True)
    result_slot = st.empty()
    result_slot.markdown(
        '<div class="awaiting">Nothing sent yet.</div>', unsafe_allow_html=True
    )


# --------------------------------------------------------------------------
# Call the API
# --------------------------------------------------------------------------

if submitted:
    if not city.strip():
        result_slot.markdown(
            '<div class="awaiting">Add a city — it decides the tier the model uses.</div>',
            unsafe_allow_html=True,
        )
    else:
        payload = {
            "age": int(age),
            "weight": float(weight),
            "height": float(height),
            "income_lpa": float(income_lpa),
            "smoker": bool(smoker),
            "city": city.strip(),
            "occupation": occupation,
        }

        try:
            resp = requests.post(f"{api_base.rstrip('/')}/predict", json=payload, timeout=10)

            if resp.status_code == 200:
                category = resp.json().get("Predicted_category", "—")
                result_slot.markdown(
                    f"""
                    <div class="result">
                        <div class="k">Premium category</div>
                        <div class="v">{category}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif resp.status_code == 404:
                result_slot.markdown(
                    '<div class="awaiting">Reached the server, but there is no '
                    '<b>/predict</b> route. Check the endpoint name in app.py.</div>',
                    unsafe_allow_html=True,
                )
            elif resp.status_code == 422:
                result_slot.markdown(
                    '<div class="awaiting">The API rejected these values — '
                    'check the details below.</div>',
                    unsafe_allow_html=True,
                )
                st.json(resp.json())
            else:
                result_slot.markdown(
                    f'<div class="awaiting">API returned {resp.status_code}.</div>',
                    unsafe_allow_html=True,
                )
                st.code(resp.text)

        except requests.exceptions.ConnectionError:
            result_slot.markdown(
                f'<div class="awaiting">No API at {api_base} — the backend either '
                'failed to start (see the sidebar) or the URL is wrong.</div>',
                unsafe_allow_html=True,
            )
        except requests.exceptions.Timeout:
            result_slot.markdown(
                '<div class="awaiting">The API took longer than 10s to answer.</div>',
                unsafe_allow_html=True,
            )

        with st.expander("Request sent"):
            st.code(json.dumps(payload, indent=2), language="json")