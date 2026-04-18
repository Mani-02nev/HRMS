import streamlit as st
from streamlit_calendar import calendar

# -----------------------------
# CATEGORY COLORS
# -----------------------------
CATEGORIES = {
    "Interview": "#2563eb",
    "Leave": "#ef4444",
    "Meeting": "#10b981",
    "Deadline": "#f59e0b"
}

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def show():

    if "events" not in st.session_state:
        st.session_state.events = []
    tab1, tab2 = st.tabs(["Calendar", "Events"])
    with tab1:

    # -----------------------------
    # SAFE PREMIUM CSS (SCOPED)
    # -----------------------------
        st.markdown("""
    <style>

    .cal-card {
        background:#0f172a;
        border:1px solid #1e293b;
        border-radius:12px;
        padding:16px;
    }

    /* FullCalendar styling */
    .cal-card .fc {
        --fc-border-color:#1e293b;
        --fc-today-bg-color:rgba(37,99,235,0.1);
        color:#cbd5e1;
    }

    .cal-card .fc-toolbar-title {
        color:#e2e8f0;
        font-weight:600;
        font-size:16px;
    }

    .cal-card .fc-button {
        background:transparent;
        border:1px solid #334155;
        color:#cbd5e1;
        border-radius:6px;
        font-size:12px;
    }

    .cal-card .fc-button:hover {
        background:#1e293b;
    }

    .cal-card .fc-button-active {
        background:#2563eb !important;
        border-color:#2563eb !important;
        color:white !important;
    }

    .cal-card .fc-daygrid-day-number {
        color:#64748b;
        font-size:12px;
    }

    .cal-card .fc-day-today .fc-daygrid-day-number {
        background:#2563eb;
        color:white;
        border-radius:6px;
        padding:2px 6px;
    }

    .cal-card .fc-event {
        border-radius:6px;
        font-size:11px;
        padding:2px 6px;
        border:none;
    }

    </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # HEADER
    # -----------------------------
        st.title("Calendar")

    # -----------------------------
    # ADD EVENT (CLEAN FORM)
    # -----------------------------
        with st.expander("Add Event"):

            title = st.text_input("Title")
            category = st.selectbox("Type", list(CATEGORIES.keys()))

            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")

        if st.button("Add Event"):
            if title:
                st.session_state.events.append({
                    "title": title,
                    "start": str(start),
                    "end": str(end),
                    "color": CATEGORIES[category]
                })
                st.success("Event Added")
                st.rerun()
            else:
                st.warning("Enter title")

        st.divider()

    # -----------------------------
    # CALENDAR
    # -----------------------------
        st.markdown('<div class="cal-card">', unsafe_allow_html=True)

        calendar(
        events=st.session_state.events,
        options={
            "initialView": "dayGridMonth",
            "height": 650,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "dayMaxEvents": True
        },
        key="calendar"
    )

        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # EVENT LIST (SIMPLE)
    # -----------------------------
    with tab2:  
        if st.session_state.events:
            st.subheader("Events")

            for i, ev in enumerate(st.session_state.events):
                col1, col2 = st.columns([6,1])

                col1.write(f"{ev['title']} — {ev['start']}")

                if col2.button("Delete", key=i):
                    st.session_state.events.pop(i)
                    st.rerun()