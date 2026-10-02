import pandas as pd
import streamlit as st
from csp import LabCSP

st.set_page_config(page_title="Lab Slot Allocation", page_icon="🧪")

# ---------- colours ----------
st.markdown("""
<style>
.stApp { background: #eef1f6; }
.banner { background: #16213e; padding: 22px 26px; border-radius: 12px; margin-bottom: 18px; }
.banner h2 { color: white; margin: 0; }
.banner p { color: #c9d6ec; margin: 4px 0 0 0; }
.stButton > button { background: #3a7bd5; color: white; border: none; border-radius: 8px; }
.stButton > button:hover { background: #2c5fb0; color: white; }
.stTabs [aria-selected="true"] { color: #3a7bd5; }
</style>
<div class="banner">
  <h2>🧪 College Lab Slot Allocation</h2>
  <p>Constraint Satisfaction Problem + Backtracking Search</p>
</div>
""", unsafe_allow_html=True)

# ---------- starting data ----------
if "ver" not in st.session_state:
    st.session_state.ver = 0
    st.session_state.labs_df = pd.DataFrame({"Lab": [], "Capacity": []})
    st.session_state.sessions_df = pd.DataFrame(
        {"Batch": [], "Subject": [], "Students": [], "Faculty": []})
    st.session_state.days_text = ""
    st.session_state.slots_text = ""
    st.session_state.blocked = {}      # "Lab:Lab1" -> ["Monday | 9-10", ...]


def load_sample():
    st.session_state.ver += 1
    st.session_state.labs_df = pd.DataFrame({"Lab": ["Lab1", "Lab2"], "Capacity": [40, 60]})
    st.session_state.sessions_df = pd.DataFrame({
        "Batch": ["CSE-A", "CSE-B", "CSE-C"],
        "Subject": ["AI", "DBMS", "Python"],
        "Students": [35, 50, 30],
        "Faculty": ["Faculty1", "Faculty2", "Faculty1"]})
    st.session_state.days_text = "Monday, Tuesday"
    st.session_state.slots_text = "9-10, 10-11, 11-12"
    st.session_state.blocked = {}


def to_list(text):
    return list(dict.fromkeys(x.strip() for x in text.split(",") if x.strip()))


st.button("▶ Load sample data", on_click=load_sample)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["1. Labs", "2. Days & Slots", "3. Sessions", "4. Availability", "5. Result"])

# ---------- 1. labs ----------
with tab1:
    st.caption("Add a row for every lab (click the empty row at the bottom).")
    labs_df = st.data_editor(st.session_state.labs_df, num_rows="dynamic",
                             key=f"labs_{st.session_state.ver}", width="stretch")

# ---------- 2. days & slots ----------
with tab2:
    days_text = st.text_input("Days (separate with commas)", key="days_text",
                              placeholder="Monday, Tuesday, Wednesday")
    slots_text = st.text_input("Time slots (separate with commas)", key="slots_text",
                               placeholder="9-10, 10-11, 11-12")

# ---------- 3. sessions ----------
with tab3:
    st.caption("Each row is one lab session.")
    sessions_df = st.data_editor(st.session_state.sessions_df, num_rows="dynamic",
                                 key=f"sessions_{st.session_state.ver}", width="stretch")

# read the tables
labs = {}
for _, r in labs_df.dropna().iterrows():
    labs[str(r["Lab"]).strip()] = int(r["Capacity"])
days = to_list(days_text)
slots = to_list(slots_text)
sessions = {}
for _, r in sessions_df.dropna().iterrows():
    sessions[f"Session-{len(sessions) + 1}"] = {
        "batch": str(r["Batch"]).strip(), "subject": str(r["Subject"]).strip(),
        "students": int(r["Students"]), "faculty": str(r["Faculty"]).strip()}
faculty_names = sorted({s["faculty"] for s in sessions.values()})

# ---------- 4. availability ----------
with tab4:
    st.caption("Optional. Everything is available unless you mark it here.")
    kind = st.radio("Type", ["Lab", "Faculty"], horizontal=True)
    names = list(labs) if kind == "Lab" else faculty_names
    if not names or not days or not slots:
        st.info("Add labs / sessions, days and slots first.")
    else:
        name = st.selectbox("Name", names)
        key = f"{kind}:{name}"
        options = [f"{d} | {s}" for d in days for s in slots]
        saved = [o for o in st.session_state.blocked.get(key, []) if o in options]
        chosen = st.multiselect(f"{name} is NOT available at", options, default=saved,
                                key=f"block_{key}")
        st.session_state.blocked[key] = chosen

# ---------- 5. result ----------
with tab5:
    if st.button("⚙ Generate allocation"):
        if not (labs and days and slots and sessions):
            st.warning("Please add at least one lab, day, slot and session first.")
        else:
            all_combos = {(d, s) for d in days for s in slots}

            def free(kind, name):
                bad = st.session_state.blocked.get(f"{kind}:{name}", [])
                bad = {tuple(x.split(" | ")) for x in bad}
                return all_combos - bad

            engine = LabCSP(
                labs=labs, days=days, slots=slots, sessions=sessions,
                lab_availability={lab: free("Lab", lab) for lab in labs},
                faculty_availability={f: free("Faculty", f) for f in faculty_names})
            solution = engine.run()

            if solution:
                st.success("Valid allocation generated successfully.")
                rows = []
                for sess, (day, lab, slot) in solution.items():
                    info = sessions[sess]
                    rows.append({"Batch": info["batch"], "Subject": info["subject"],
                                 "Faculty": info["faculty"], "Day": day, "Lab": lab, "Slot": slot})
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            else:
                st.error("No valid allocation found. Try adding more labs, days or slots.")
