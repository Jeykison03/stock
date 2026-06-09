import os
import pandas            as pd
import plotly.graph_objects as go
import streamlit         as st
from sqlalchemy          import text
from dotenv              import load_dotenv
from data_base            import get_engine

load_dotenv()

st.set_page_config(
    page_title = "Stock Market Dashboard",
    page_icon  = "📈",
    layout     = "wide"    #to use full screen
)

def load_all_data():
   
    engine = get_engine()
    with engine.connect() as conn:  # get all data
        df = pd.read_sql(
            text("""
                SELECT
                    symbol,
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    "Sma_5d",
                    "Sma_20d",
                    daily_return,
                    daily_range,
                    signal
                FROM  stock_analysis
                ORDER BY symbol, date
            """),
            conn
        )
    return df
 
 
@st.cache_data(ttl=300)
def load_latest():
    
    engine = get_engine()
    with engine.connect() as conn:    # get only one data for each
        df = pd.read_sql(
            text("""
                SELECT DISTINCT ON (symbol)
                    symbol,
                    date,
                    close,
                    daily_return,
                    volume,
                    signal
                FROM  stock_analysis
                ORDER BY symbol, date DESC
            """),
            conn
        )
    return df
 
 

 
def format_volume(volume):

    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return str(volume)
 
 
def signal_colour(signal):
   
    if signal == "BUY":
        return "🟢"
    elif signal == "SELL":
        return "🔴"
    return "🟡"


def price_chart(df, symbol):
 
    fig = go.Figure()
 
    
    fig.add_trace(go.Scatter(
        x    = df["date"],
        y    = df["close"],
        name = "Close Price",
        line = dict(color="#4C9BE8", width=2)
    ))
 
    
    fig.add_trace(go.Scatter(
        x    = df["date"],
        y    = df["Sma_5d"],
        name = "MA 5",
        line = dict(color="#F5A623", width=1.5, dash="dot")
    ))
 
    
    fig.add_trace(go.Scatter(
        x    = df["date"],
        y    = df["Sma_20d"],
        name = "MA 20",
        line = dict(color="#E8534C", width=1.5, dash="dash")
    ))
 
    fig.update_layout(
        title      = f"{symbol} — Price & Moving Averages",
        xaxis_title= "Date",
        yaxis_title= "Price (USD)",
        hovermode  = "x unified",    
        height     = 420,
        legend     = dict(
            orientation = "h",       
            yanchor     = "bottom",
            y           = 1.02,
            xanchor     = "right",
            x           = 1
        )
    )
 
    return fig


def volume_chart(df, symbol):
    
 
    colours = [
        "#2ECC71" if r >= 0 else "#E74C3C"
        for r in df["daily_return"].fillna(0)
    ]
 
    fig = go.Figure()
 
    fig.add_trace(go.Bar(
        x              = df["date"],
        y              = df["volume"],
        name           = "Volume",
        marker_color   = colours
    ))
 
    fig.update_layout(
        title      = f"{symbol} — Daily Volume",
        xaxis_title= "Date",
        yaxis_title= "Volume",
        height     = 280
    )
 
    return fig
 
 
def daily_return_chart(df, symbol):
    """
    Bar chart showing daily return % per day.
    Positive = green, negative = red.
    """
 
    clean_df = df.dropna(subset=["daily_return"])
 
    colours = [
        "#2ECC71" if r >= 0 else "#E74C3C"
        for r in clean_df["daily_return"]
    ]
 
    fig = go.Figure()
 
    fig.add_trace(go.Bar(
        x            = clean_df["date"],
        y            = clean_df["daily_return"],
        name         = "Daily Return %",
        marker_color = colours
    ))
 
    fig.add_hline(y=0, line_color="white", line_width=1)
 
    fig.update_layout(
        title      = f"{symbol} — Daily Return %",
        xaxis_title= "Date",
        yaxis_title= "Return %",
        height     = 280
    )
 
    return fig
 
 
def comparison_chart(df_all):
    """
    Line chart comparing close prices of ALL 5 stocks.
    Each stock gets its own coloured line.
    Shows relative performance side by side.
    """
 
    colours = {
        "AAPL":  "#4C9BE8",
        "MSFT":  "#F5A623",
        "GOOGL": "#2ECC71",
        "AMZN":  "#9B59B6",
        "TSLA":  "#E74C3C"
    }
 
    fig = go.Figure()
 
    for symbol in df_all["symbol"].unique():
        df_sym = df_all[df_all["symbol"] == symbol].copy()
 
        fig.add_trace(go.Scatter(
            x    = df_sym["date"],
            y    = df_sym["close"],
            name = symbol,
            line = dict(
                color = colours.get(symbol, "#FFFFFF"),
                width = 2
            )
        ))
 
    fig.update_layout(
        title      = "All Stocks — Close Price Comparison",
        xaxis_title= "Date",
        yaxis_title= "Price (USD)",
        hovermode  = "x unified",
        height     = 380
    )
 
    return fig


def main():
 
    # ── HEADER ───────────────────────────────────────────────
    st.title("📈 Stock Market Pipeline Dashboard")
    st.caption("Data from Alpha Vantage → PostgreSQL → PySpark → Gold Layer")
    st.divider()
 
    # ── LOAD DATA ────────────────────────────────────────────
    with st.spinner("Loading data from database..."):
        df_all    = load_all_data()
        df_latest = load_latest()
 
    if df_all.empty:
        st.error("No data found in gold_stock_metrics. Run the pipeline first.")
        st.code("python inject.py\npython spark_transform.py")
        return
 
    # ── SIDEBAR — stock selector ──────────────────────────────
    st.sidebar.title("Controls")
    st.sidebar.markdown("---")
 
    symbols       = sorted(df_all["symbol"].unique().tolist())
    selected      = st.sidebar.selectbox(
        "Select Stock",
        options  = symbols,
        index    = 0
    )
 
    # date range filter
    min_date = df_all["date"].min()
    max_date = df_all["date"].max()
 
    date_range = st.sidebar.date_input(
        "Date Range",
        value   = (min_date, max_date),
        min_value = min_date,
        max_value = max_date
    )
 
    # last refreshed time
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data range: {min_date} → {max_date}")
    st.sidebar.caption(f"Total rows: {len(df_all)}")
 
    # apply filters
    df_selected = df_all[df_all["symbol"] == selected].copy()
 
    if len(date_range) == 2:
        df_selected = df_selected[
            (df_selected["date"] >= date_range[0]) &
            (df_selected["date"] <= date_range[1])
        ]
 
    # ── SECTION 1 — metric cards ──────────────────────────────
    st.subheader("Latest Snapshot — All Stocks")
 
    cols = st.columns(len(df_latest))
 
    for i, row in df_latest.iterrows():
        with cols[i]:
            daily_ret = row["daily_return"]
            ret_str   = f"{daily_ret:+.2f}%" if daily_ret is not None else "N/A"
            
            sig       = signal_colour(row["signal"])
 
            st.metric(
                label      = f"{sig} {row['symbol']}",
                value      = f"${row['close']:.2f}",
                delta      = ret_str        # shows green arrow if positive
            )
            st.caption(f"Vol: {format_volume(row['volume'])}")
            st.caption(f"Signal: {row['signal']}")
 
    st.divider()
 
    # ── SECTION 2 — price chart with moving averages ──────────
    st.subheader(f"{selected} — Detailed View")
 
    if df_selected.empty:
        st.warning("No data for selected filters.")
    else:
        st.plotly_chart(
            price_chart(df_selected, selected),
            use_container_width = True     # fill full page width
        )
 
        # ── SECTION 3 — volume and return side by side ────────
        col_left, col_right = st.columns(2)
 
        with col_left:
            st.plotly_chart(
                volume_chart(df_selected, selected),
                use_container_width = True
            )
 
        with col_right:
            st.plotly_chart(
                daily_return_chart(df_selected, selected),
                use_container_width = True
            )
 
    st.divider()
 
    # ── SECTION 4 — all stocks comparison ────────────────────
    st.subheader("All Stocks — Comparison")
    st.plotly_chart(
        comparison_chart(df_all),
        use_container_width = True
    )
 
    st.divider()
 
    # ── SECTION 5 — raw data table ───────────────────────────
    st.subheader(f"{selected} — Raw Data Table")
 
    show_cols = [
        "date", "close", "Sma_5d", "Sma_20d",
        "daily_return", "daily_range", "signal", "volume"
    ]
 
    st.dataframe(
        df_selected[show_cols]
            .sort_values("date", ascending=False)
            .reset_index(drop=True),
        use_container_width = True,
        height              = 300
    )
 
 
# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    main()