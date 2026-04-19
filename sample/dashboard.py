import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

EMP_FILE = "data/employees.csv"
ATT_FILE = "data/attendance.csv"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Mulish:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Mulish', sans-serif; }

.dash-header {
    background: linear-gradient(120deg,#0b1628 60%,#0f2a4a 100%);
    border-radius: 20px; padding: 28px 32px; margin-bottom: 22px;
    border: 1px solid rgba(56,189,248,0.12);
    box-shadow: 0 0 60px rgba(56,189,248,0.05);
}
.dash-header h1 { font-family:'Syne',sans-serif; color:#e2e8f0; font-size:28px; margin:0 0 4px; }
.dash-header p  { color:#475569; font-size:13px; margin:0; }

.kpi { background:#0b1628; border-radius:16px; padding:20px 22px;
       border:1px solid rgba(255,255,255,0.06); transition:transform .2s; }
.kpi:hover { transform:translateY(-3px); box-shadow:0 8px 30px rgba(0,0,0,0.3); }
.kpi-val { font-family:'Syne',sans-serif; font-size:38px; font-weight:800; line-height:1; }
.kpi-lbl { font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:.8px; margin-top:5px; }
.kpi-sub { font-size:12px; margin-top:4px; }

.sec { font-family:'Syne',sans-serif; font-size:13px; color:#64748b;
       text-transform:uppercase; letter-spacing:1px;
       border-left:3px solid #38bdf8; padding-left:10px; margin:22px 0 12px; }
</style>
"""

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Mulish", color="#94a3b8", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
)

def load_df(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        return df
    return pd.DataFrame()

def pct(a, b): return round((a / b) * 100) if b else 0


def show():
    st.markdown(CSS, unsafe_allow_html=True)

    emp_df = load_df(EMP_FILE)
    att_df = load_df(ATT_FILE)

    today = str(datetime.now().date())
    t_att   = att_df[att_df["date"] == today] if not att_df.empty else pd.DataFrame()
    present = (t_att["status"] == "Present").sum()
    total   = len(emp_df)
    absent  = total - present
    rate    = pct(present, total)

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="dash-header">
      <h1><i class="fas fa-chart-line"></i> HR Analytics Dashboard</h1>
      <p style="color:white;">{today} &nbsp;·&nbsp; Real-time workforce overview  </p>
    </div>""", unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, clr, sub in [
        (c1, total,    "Total Employees", "#60a5fa", "All departments"),
        (c2, present,  "Present Today",   "#34d399", f"{rate}% rate"),
        (c3, absent,   "Absent Today",    "#f87171", f"{pct(absent,total)}% missing"),
        (c4, f"{rate}%","Attendance Rate","#fbbf24", "Today's coverage"),
    ]:
        col.markdown(f"""
        <div class="kpi">
          <div class="kpi-val" style="color:{clr}">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-sub" style="color:{clr}99">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Row 1: Trend + Department Bar ─────────────────────────────
    ca, cb = st.columns(2)

    with ca:
        st.markdown('<div class="sec">Attendance — Last 14 Days</div>', unsafe_allow_html=True)
        if not att_df.empty:
            dates  = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
            counts = [len(att_df[(att_df["date"] == d) & (att_df["status"] == "Present")]) for d in dates]
            fig = go.Figure(go.Scatter(
                x=dates, y=counts, mode="lines+markers",
                line=dict(color="#38bdf8", width=3.5),
                marker=dict(size=10, color="#38bdf8"),   
                fill="tozeroy", fillcolor="rgba(56,189,248,0.08)"
            ))
            fig.update_layout(**PLOT, height=230,
                xaxis=dict(showgrid=False, tickformat="%d %b", tickangle=-30),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance data.")

    with cb:
        st.markdown('<div class="sec">Headcount by Department</div>', unsafe_allow_html=True)
        if not emp_df.empty and "department" in emp_df.columns:
            d = emp_df["department"].value_counts().reset_index()
            d.columns = ["dept", "n"]
            colors = ["#38bdf8","#34d399","#fbbf24","#f87171","#a78bfa","#fb7185"]
            fig2 = go.Figure(go.Bar(
                x=d["dept"], y=d["n"],
                marker=dict(color=colors[:len(d)], line=dict(width=0)),
                text=d["n"], textposition="outside",
                textfont=dict(color="#94a3b8")
            ))
            fig2.update_layout(**PLOT, height=230,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No department data.")

    # ── Row 2: Donut + Role Bar ────────────────────────────────────
    cc, cd = st.columns(2)

    with cc:
        st.markdown('<div class="sec">Present vs Absent</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Pie(
            labels=["Present","Absent"],
            values=[max(present,0), max(absent,0)],
            hole=0.65,
            marker=dict(colors=["#34d399","#f87171"], line=dict(width=0)),
            textinfo="none"
        ))
        fig3.add_annotation(
            text=f"<b>{rate}%</b>", x=0.5, y=0.5, showarrow=False,
            font=dict(size=24, color="#e2e8f0", family="Syne")
        )
        fig3.update_layout(**PLOT, height=230, showlegend=True,
            legend=dict(orientation="h", x=0.1, y=-0.05,
                        font=dict(color="#94a3b8")))
        st.plotly_chart(fig3, use_container_width=True)

    with cd:
        st.markdown('<div class="sec">Headcount by Role</div>', unsafe_allow_html=True)
        if not emp_df.empty and "role" in emp_df.columns:
            r = emp_df["role"].value_counts().reset_index()
            r.columns = ["role", "n"]
            colors = ["#a78bfa","#38bdf8","#34d399","#fbbf24","#f87171"]
            fig4 = go.Figure(go.Bar(
                y=r["role"], x=r["n"], orientation="h",
                marker=dict(color=colors[:len(r)], line=dict(width=0)),
                text=r["n"], textposition="outside",
                textfont=dict(color="#94a3b8")
            ))
            fig4.update_layout(**PLOT, height=230,
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(showgrid=False))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No role data.")

    # ── Heatmap ───────────────────────────────────────────────────
    st.markdown('<div class="sec">Monthly Attendance Heatmap</div>', unsafe_allow_html=True)
    if not att_df.empty and total > 0:
        now        = datetime.now()
        month_days = calendar.monthrange(now.year, now.month)[1]
        all_dates  = [(datetime(now.year, now.month, d)).strftime("%Y-%m-%d")
                      for d in range(1, month_days + 1)]
        daily      = [pct(len(att_df[(att_df["date"]==d) & (att_df["status"]=="Present")]), total)
                      for d in all_dates]

        pad    = datetime(now.year, now.month, 1).weekday()
        padded = [None]*pad + daily
        while len(padded) % 7: padded.append(None)

        rows  = [padded[i:i+7] for i in range(0, len(padded), 7)]
        z     = [[v if v is not None else -1 for v in r] for r in rows]
        texts = [[f"{v}%" if v is not None and v >= 0 else "" for v in r] for r in rows]

        fig5 = go.Figure(go.Heatmap(
            z=z, x=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            y=[f"Week {i+1}" for i in range(len(rows))],
            text=texts, texttemplate="%{text}",
            colorscale=[[0,"rgba(255,255,255,0.03)"],[0.01,"#1e3a2f"],[0.5,"#16a34a"],[1,"#34d399"]],
            zmin=0, zmax=100, showscale=True,
            colorbar=dict(title="%", tickfont=dict(color="#64748b"), thickness=10),
            hovertemplate="<b>%{x} %{y}</b><br>Rate: %{text}<extra></extra>"
        ))
        fig5.update_layout(**PLOT, height=250,
            xaxis=dict(showgrid=False, side="top"),
            yaxis=dict(showgrid=False, autorange="reversed"))
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No data available for heatmap.")


    st.markdown('<div class="sec">Recent Check-ins</div>', unsafe_allow_html=True)
    if not t_att.empty:
        st.table(t_att[["name", "check_in", "check_out", "status"]].sort_values(by="check_in", ascending=False).head(10).reset_index(drop=True))
    else:
        st.info("No check-ins recorded for today.")
