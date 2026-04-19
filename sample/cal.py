import streamlit as st
from streamlit_calendar import calendar
import json
import os

FILE = "data/events.json"

CATEGORIES = {
    "Interview": "#2563eb",
    "Leave": "#ef4444",
    "Meeting": "#10b981",
    "Deadline": "#f59e0b"
}

# -----------------------------
# LOAD / SAVE
# -----------------------------
def load_events():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_events(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# MAIN
# -----------------------------
def show():

    # load once
    if "events" not in st.session_state:
        st.session_state.events = load_events()

    tab1, tab2 = st.tabs(["Calendar", "Events"])

    # =============================
    # TAB 1 — CALENDAR
    # =============================
    with tab1:

        st.title("Calendar")

        with st.expander("Add Event"):

            title = st.text_input("Title")
            category = st.selectbox("Type", list(CATEGORIES.keys()))

            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")

            if st.button("Add Event"):
                if title:
                    new_event = {
                        "title": title,
                        "start": str(start),
                        "end": str(end),
                        "color": CATEGORIES[category]
                    }

                    st.session_state.events.append(new_event)
                    save_events(st.session_state.events)

                    st.success("Event Added")
                    st.rerun()
                else:
                    st.warning("Enter title")

        st.divider()

        calendar(
            events=st.session_state.events,
            options={
                "initialView": "dayGridMonth",
                "height": 650,
                "headerToolbar": {
                    "left": "prev,next",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay"
                }
            },
            key="calendar"
        )

    # =============================
    # TAB 2 — EVENTS LIST
    # =============================
    with tab2:

        if st.session_state.events:

            for i, ev in enumerate(st.session_state.events):
                col1, col2 = st.columns([6,1])

                col1.markdown(f"**{ev['title']}**  \n"
                            f"<span style='color:{ev['color']}'>category: {list(CATEGORIES.keys())[list(CATEGORIES.values()).index(ev['color'])]}</span>  \n"
                            f"{ev['start']} to {ev['end']}",
                            unsafe_allow_html=True)

                if col2.button("Delete", key=i):
                    st.session_state.events.pop(i)
                    save_events(st.session_state.events)
                    st.rerun()