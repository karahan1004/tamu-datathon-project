# pages/Monthly_Shipments.py
import re
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Monthly Matrix • Data 1 & Data 2", layout="wide")

PRIMARY = "#cd1b1b"

D1_GROUPS = ["All Day Menu", "Lunch Menu", "Open Food", "Gift Card", "Signature Drinks"]
D1_COLORS = ["#7f1d1d", "#b91c1c", "#ef4444", "#f97316", "#f59e0b"]

D2_CATEGORIES = [
    "Additional", "Appetizer", "Bingsu", "Combo Items", "Dessert", "Drink",
    "Fried Chicken", "Fried Rice", "Fruit Tea", "Gift Card", "Jas-Lemonade",
    "Lunch Special", "Mai Dessert", "Milk Tea", "Open Food", "Prep item",
    "Ramen", "Rice Noodle", "Special Offer", "Tossed Ramen",
    "Tossed Rice Noodle", "Wonton"
]

DATA_DIR = (Path(__file__).parent.parent / "data").resolve()
MONTH_FILE_RE = re.compile(r"^([A-Za-z]+)_Data_Matrix\.(xlsx|xls|csv)$", re.I)

def _month_key(m: str) -> int:
    return pd.to_datetime(m, format="%B").month

def discover_month_files() -> dict[str, Path]:
    """Return {MonthName -> Path} for files that match *_Data_Matrix.* (calendar order)."""
    mapping: dict[str, Path] = {}
    for p in DATA_DIR.glob("*_Data_Matrix.*"):
        m = MONTH_FILE_RE.match(p.name)
        if not m:
            continue
        month_name = m.group(1).capitalize()
        mapping[month_name] = p
    return dict(sorted(mapping.items(), key=lambda kv: _month_key(kv[0])))

@st.cache_data(show_spinner=False)
def load_data1(path: Path, month_label: str) -> pd.DataFrame:
    """Read sheet 'data 1' with columns ['Group', 'Amount']."""
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path) 
    else:
        df = pd.read_excel(path, sheet_name="data 1", engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    required = {"Group", "Amount"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing one of {required} in {path.name} (data 1)")

    out = df[["Group", "Amount"]].copy()
    out["Amount"] = (
        out["Amount"].astype("string")
        .str.replace(r"[\$,]", "", regex=True)
        .replace({"": "0", pd.NA: "0"})
    ).astype(float)

    out["Group"] = out["Group"].astype("string").fillna("").str.strip()
    out["Month"] = month_label
    return out

@st.cache_data(show_spinner=False)
def load_data2(path: Path, month_label: str) -> pd.DataFrame:
    """Read sheet 'data 2' with columns ['Category','Count','Amount']."""
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path, sheet_name="data 2", engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    required = {"Category", "Count", "Amount"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Missing one of {required} in {path.name} (data 2). Missing: {missing}")

    out = df[["Category", "Count", "Amount"]].copy()
    out["Category"] = out["Category"].astype("string").fillna("").str.strip()
    out["Count"] = pd.to_numeric(out["Count"], errors="coerce").fillna(0)
    out["Amount"] = (
        out["Amount"].astype("string")
        .str.replace(r"[\$,]", "", regex=True)
        .replace({"": "0", pd.NA: "0"})
    )
    out["Amount"] = pd.to_numeric(out["Amount"], errors="coerce").fillna(0.0)
    out["Month"] = month_label
    return out

tabs = st.tabs(["📊 Data 1 — Stacked Revenue", "🥧 Data 2 — Category Pies"])

with tabs[0]:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:10px 0 4px 0;">
          <div style="width:12px;height:28px;background:{PRIMARY};border-radius:3px;"></div>
          <h3 style="margin:0;">Stacked Revenue by Group</h3>
        </div>
        """, unsafe_allow_html=True
    )

    month_to_path = discover_month_files()
    if not month_to_path:
        st.error(f"No files found in {DATA_DIR}")
        st.stop()
    months_all = list(month_to_path.keys())

    st.caption("Choose the month range for Data 1:")
    start_m, end_m = st.select_slider(
        "Month Range", options=months_all,
        value=(months_all[0], months_all[-1]),
        label_visibility="collapsed",
    )
    i0, i1 = months_all.index(start_m), months_all.index(end_m)
    lo, hi = sorted([i0, i1])
    months_d1 = months_all[lo:hi+1]

    with st.expander("Advanced groups (optional)"):
        d1_groups = st.multiselect("Stack segments", D1_GROUPS, default=D1_GROUPS)
        if not d1_groups:
            st.warning("At least one group is required; reverting to defaults.")
            d1_groups = D1_GROUPS[:]
    color_scale = alt.Scale(domain=d1_groups, range=D1_COLORS[:len(d1_groups)])

    frames1 = [load_data1(month_to_path[m], m) for m in months_d1]
    d1 = pd.concat(frames1, ignore_index=True) if frames1 else pd.DataFrame(columns=["Group","Amount","Month"])

    pivot = (
        d1.groupby(["Month", "Group"], as_index=False)["Amount"].sum()
          .pivot(index="Month", columns="Group", values="Amount")
    )
    pivot = pivot.reindex(index=months_d1).reindex(columns=d1_groups).fillna(0.0)

    long = pivot.reset_index().melt(id_vars="Month", var_name="Group", value_name="Amount")
    tot = long.groupby("Month", as_index=False)["Amount"].sum().rename(columns={"Amount": "Total"})
    long = long.merge(tot, on="Month", how="left")

    chart = (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X("Month:N", sort=months_d1, axis=alt.Axis(labelAngle=0), title=None),
            y=alt.Y("Amount:Q", stack="zero", title="Total ($)"),
            color=alt.Color("Group:N", scale=color_scale, title="Group"),
            order=alt.Order("Group:N"),
            tooltip=[
                alt.Tooltip("Month:N"),
                alt.Tooltip("Group:N"),
                alt.Tooltip("Amount:Q", format=",.2f", title="Group Amount ($)"),
                alt.Tooltip("Total:Q", format=",.2f", title="Month Total ($)"),
            ],
        )
        .properties(height=430)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show totals table"):
        st.dataframe(
            pivot.assign(**{"Month Total ($)": pivot.sum(axis=1)}).reset_index(),
            use_container_width=True
        )

with tabs[1]:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:10px 0 4px 0;">
          <div style="width:12px;height:28px;background:{PRIMARY};border-radius:3px;"></div>
          <h3 style="margin:0;">Category Share by Month (Pie)</h3>
        </div>
        """, unsafe_allow_html=True
    )

    month_to_path = discover_month_files()
    months_all = list(month_to_path.keys())
    if not months_all:
        st.error(f"No files found in {DATA_DIR}")
        st.stop()

    # Left = controls + the ONLY legend. Right = charts.
    left, right = st.columns([1.05, 2.0], gap="large")

    with left:
        st.caption("Choose months and categories for Data 2:")

        m_sel = st.multiselect("Months", months_all, default=months_all)
        if not m_sel:
            st.info("Select at least one month.")
            st.stop()

        use_all = st.checkbox("Use all categories", value=True, help="Turn off to pick a subset.")
        if use_all:
            cats_selected = D2_CATEGORIES[:]           
        else:
            cats_selected = st.multiselect(
                "Categories (scroll + search)",
                options=D2_CATEGORIES,
                default=[],
                help="Scroll or search to select one or more categories."
            )

        if cats_selected:
            color_scale = alt.Scale(domain=cats_selected, scheme="tableau10")
            legend_df = pd.DataFrame({"Category": cats_selected})
            legend_chart = (
                alt.Chart(legend_df)
                .mark_rect(width=14, height=14)
                .encode(
                    y=alt.Y("Category:N", sort=cats_selected, axis=alt.Axis(title=None)),
                    color=alt.Color("Category:N", scale=color_scale, legend=None),
                )
                .properties(width=200, height=min(24 * len(cats_selected), 360))
            )
            st.markdown("**Legend**")
            st.altair_chart(legend_chart, use_container_width=False)
        else:
            color_scale = alt.Scale(domain=[], scheme="tableau10")

        per_row = 2

    with right:
        frames2 = [load_data2(month_to_path[m], m) for m in m_sel]
        d2 = pd.concat(frames2, ignore_index=True) if frames2 else pd.DataFrame(columns=["Category","Count","Amount","Month"])

        d2["Category"] = d2["Category"].astype("string").fillna("").str.strip()

        if cats_selected:
            d2 = d2[d2["Category"].isin(cats_selected)]
        else:
            d2 = d2.iloc[0:0] 

        d2 = d2[d2["Amount"] > 0]

        if d2.empty:
            st.info("No data for the chosen filters.")
        else:
            agg = (
                d2.groupby(["Month", "Category"], as_index=False)[["Amount", "Count"]]
                  .sum()
            )
            for i in range(0, len(m_sel), per_row):
                row = st.columns(per_row, gap="large")
                for col, month in zip(row, m_sel[i:i+per_row]):
                    dfm = agg[(agg["Month"] == month)]
                    if dfm.empty:
                        continue

                    total_amt = dfm["Amount"].sum()
                    title = f"{month} • ${total_amt:,.0f}"

                    pie = (
                        alt.Chart(dfm, title=title)
                        .mark_arc(outerRadius=110, innerRadius=0)
                        .encode(
                            theta=alt.Theta("Amount:Q", stack=True, title=None),
                            color=alt.Color("Category:N", scale=color_scale, legend=None),
                            tooltip=[
                                alt.Tooltip("Category:N"),
                                alt.Tooltip("Count:Q", format=",.0f", title="Units"),
                                alt.Tooltip("Amount:Q", format=",.2f", title="Sales ($)"),
                            ],
                        )
                        .properties(width=300, height=300)
                    )
                    with col:
                        st.altair_chart(pie, use_container_width=False)

    with st.expander("Show raw table (Data 2)"):
        st.dataframe(d2.sort_values(["Month", "Category"]), use_container_width=True)
