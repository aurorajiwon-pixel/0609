import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 시가총액 Top 10 대시보드",
    page_icon="📈",
    layout="wide",
)

# ── 글로벌 시가총액 Top 10 (2025년 기준) ─────────────────────────────────────
TOP10 = {
    "Apple":      "AAPL",
    "NVIDIA":     "NVDA",
    "Microsoft":  "MSFT",
    "Alphabet":   "GOOGL",
    "Amazon":     "AMZN",
    "Saudi Aramco": "2222.SR",
    "Meta":       "META",
    "TSMC":       "TSM",
    "Berkshire":  "BRK-B",
    "Tesla":      "TSLA",
}

COLORS = px.colors.qualitative.Bold[:10]

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.title("📈 글로벌 시가총액 Top 10 주식 대시보드")
st.caption("Yahoo Finance 데이터 기반 · 최근 1년 주가 변화")

st.divider()

# ── 사이드바 ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")

    period_map = {
        "최근 1개월": "1mo",
        "최근 3개월": "3mo",
        "최근 6개월": "6mo",
        "최근 1년":  "1y",
        "최근 2년":  "2y",
    }
    selected_period_label = st.selectbox(
        "기간 선택", list(period_map.keys()), index=3
    )
    period = period_map[selected_period_label]

    chart_type = st.radio("차트 유형", ["정규화 수익률", "절대 주가", "캔들스틱"])

    selected_tickers = st.multiselect(
        "종목 선택 (기본: 전체)",
        options=list(TOP10.keys()),
        default=list(TOP10.keys()),
    )
    if not selected_tickers:
        st.warning("종목을 1개 이상 선택하세요.")
        st.stop()

    st.divider()
    st.info("데이터 출처: Yahoo Finance\n\nyfinance 라이브러리로 실시간 조회")

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data(tickers: dict, period: str):
    symbols = list(tickers.values())
    raw = yf.download(symbols, period=period, auto_adjust=True, progress=False)
    close = raw["Close"] if "Close" in raw.columns else raw.xs("Close", axis=1, level=0)
    # 컬럼명을 회사명으로 변환
    rev = {v: k for k, v in tickers.items()}
    close.rename(columns=rev, inplace=True)
    return close

@st.cache_data(ttl=600)
def load_single(ticker: str, period: str):
    return yf.download(ticker, period=period, auto_adjust=True, progress=False)

with st.spinner("📡 Yahoo Finance에서 데이터를 불러오는 중..."):
    df_close = load_data(TOP10, period)

# 선택 종목만 필터
df_filtered = df_close[[c for c in selected_tickers if c in df_close.columns]]

# ── 요약 카드 ─────────────────────────────────────────────────────────────────
st.subheader("📊 기간 수익률 요약")

cols = st.columns(5)
for i, name in enumerate(selected_tickers[:10]):
    if name not in df_filtered.columns:
        continue
    series = df_filtered[name].dropna()
    if len(series) < 2:
        continue
    ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
    delta_color = "normal"
    cols[i % 5].metric(
        label=name,
        value=f"${series.iloc[-1]:,.2f}",
        delta=f"{ret:+.1f}%",
    )

st.divider()

# ── 메인 차트 ─────────────────────────────────────────────────────────────────
if chart_type == "정규화 수익률":
    st.subheader(f"📈 정규화 수익률 비교 ({selected_period_label})")
    st.caption("첫 거래일 기준 100으로 정규화한 상대 수익률")

    df_norm = (df_filtered / df_filtered.iloc[0]) * 100

    fig = go.Figure()
    for i, col in enumerate(df_norm.columns):
        fig.add_trace(go.Scatter(
            x=df_norm.index,
            y=df_norm[col],
            name=col,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            hovertemplate=f"<b>{col}</b><br>날짜: %{{x|%Y-%m-%d}}<br>수익률: %{{y:.1f}}<extra></extra>",
        ))

    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        height=520,
        hovermode="x unified",
        xaxis_title="날짜",
        yaxis_title="수익률 지수 (시작=100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "절대 주가":
    st.subheader(f"💵 절대 주가 추이 ({selected_period_label})")

    fig = go.Figure()
    for i, col in enumerate(df_filtered.columns):
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered[col],
            name=col,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            hovertemplate=f"<b>{col}</b><br>날짜: %{{x|%Y-%m-%d}}<br>주가: $%{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(
        height=520,
        hovermode="x unified",
        xaxis_title="날짜",
        yaxis_title="주가 (USD)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    st.plotly_chart(fig, use_container_width=True)

else:  # 캔들스틱
    st.subheader(f"🕯️ 캔들스틱 차트 ({selected_period_label})")
    candle_name = st.selectbox("종목 선택", selected_tickers)
    ticker_sym = TOP10[candle_name]

    with st.spinner(f"{candle_name} 캔들 데이터 로드 중..."):
        df_candle = load_single(ticker_sym, period)

    fig = go.Figure(data=[go.Candlestick(
        x=df_candle.index,
        open=df_candle["Open"].squeeze(),
        high=df_candle["High"].squeeze(),
        low=df_candle["Low"].squeeze(),
        close=df_candle["Close"].squeeze(),
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        name=candle_name,
    )])
    fig.update_layout(
        height=520,
        xaxis_title="날짜",
        yaxis_title="주가 (USD)",
        xaxis_rangeslider_visible=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 수익률 막대 차트 ───────────────────────────────────────────────────────────
st.subheader("📊 종목별 기간 수익률 비교")

returns = {}
for name in selected_tickers:
    if name not in df_filtered.columns:
        continue
    s = df_filtered[name].dropna()
    if len(s) >= 2:
        returns[name] = round((s.iloc[-1] / s.iloc[0] - 1) * 100, 2)

df_ret = pd.DataFrame({"종목": list(returns.keys()), "수익률(%)": list(returns.values())})
df_ret = df_ret.sort_values("수익률(%)", ascending=False)

bar_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df_ret["수익률(%)"]]

fig_bar = go.Figure(go.Bar(
    x=df_ret["종목"],
    y=df_ret["수익률(%)"],
    marker_color=bar_colors,
    text=[f"{v:+.1f}%" for v in df_ret["수익률(%)"]],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>수익률: %{y:.2f}%<extra></extra>",
))
fig_bar.add_hline(y=0, line_color="gray", line_dash="dash", opacity=0.5)
fig_bar.update_layout(
    height=380,
    yaxis_title="수익률 (%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig_bar.update_xaxes(showgrid=False)
fig_bar.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
st.plotly_chart(fig_bar, use_container_width=True)

# ── 상관관계 히트맵 ───────────────────────────────────────────────────────────
if len(selected_tickers) >= 3:
    st.divider()
    st.subheader("🔗 종목 간 수익률 상관관계")

    df_corr = df_filtered.pct_change().dropna().corr()
    fig_heat = go.Figure(go.Heatmap(
        z=df_corr.values,
        x=df_corr.columns.tolist(),
        y=df_corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in df_corr.values],
        texttemplate="%{text}",
        hovertemplate="<b>%{x} × %{y}</b><br>상관계수: %{z:.3f}<extra></extra>",
    ))
    fig_heat.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_heat, use_container_width=True)

# ── 원본 데이터 테이블 ────────────────────────────────────────────────────────
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(
        df_filtered.tail(30).style.format("${:.2f}"),
        use_container_width=True,
    )

st.caption("⚠️ 본 대시보드는 투자 조언이 아닙니다. 투자 결정은 본인의 판단으로 하세요.")
