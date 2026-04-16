"""공실관리 대시보드 — Streamlit (JSON 기반) v3 — 기존 Flask 디자인 반영"""
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ── 페이지 설정 ──────────────────────────────
st.set_page_config(page_title="공실관리 대시보드", layout="wide", initial_sidebar_state="expanded")

COLORS = ['#4285F4','#EA4335','#FBBC04','#34A853','#FF6D01','#46BDC6','#7B61FF','#F538A0','#00ACC1','#8D6E63']

# ── 기존 Flask CSS 반영 ─────────────────────
st.markdown("""
<style>
    /* 전역 폰트 & 배경 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    
    *, *::before, *::after { box-sizing: border-box; }
    
    .stApp {
        background: #f0f2f5;
        font-family: 'Noto Sans KR', 'Malgun Gothic', '맑은 고딕', sans-serif;
    }
    
    /* Streamlit 기본 여백 제거 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* ── 사이드바 ──────────────────────── */
    [data-testid="stSidebar"] {
        background: #fff;
        border-right: 1px solid #e8eaed;
        width: 300px;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 20px;
    }
    
    /* 사이드바 라디오 → 메뉴 스타일 */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 10px 14px !important;
        border-radius: 8px !important;
        border: 1.5px solid transparent !important;
        font-size: 13px !important;
        color: #555 !important;
        background: transparent !important;
        cursor: pointer;
        transition: all 0.15s;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: #f5f7ff !important;
        border-color: #e0e4f0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
        background: #4a6cf7 !important;
        color: #fff !important;
        font-weight: 600 !important;
        border-color: #4a6cf7 !important;
    }
    
    /* ── KPI 카드 ──────────────────────── */
    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 18px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #888 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #1a1a2e !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
    }
    
    /* ── 탭 ────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #f0f0f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-size: 13px;
        color: #888;
        font-weight: 500;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #4a6cf7;
    }
    .stTabs [aria-selected="true"] {
        color: #4a6cf7 !important;
        font-weight: 700 !important;
        border-bottom-color: #4a6cf7 !important;
    }
    
    /* ── 데이터프레임 (테이블) ──────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #e8eaed;
        border-radius: 10px;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] table {
        font-size: 13px;
    }
    [data-testid="stDataFrame"] th {
        background: #f8f9fb !important;
        padding: 10px 12px !important;
        font-weight: 600 !important;
        color: #555 !important;
        border-bottom: 2px solid #e8eaed !important;
    }
    [data-testid="stDataFrame"] td {
        padding: 9px 12px !important;
        color: #444 !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }
    
    /* ── 필터 프리셋 버튼 ──────────────── */
    .preset-btns {
        display: flex;
        gap: 6px;
        margin: 8px 0;
    }
    .preset-btn {
        flex: 1;
        padding: 7px 0;
        font-size: 12px;
        font-family: inherit;
        border: 1.5px solid #e0e0e0;
        border-radius: 8px;
        background: #fff;
        color: #555;
        cursor: pointer;
        transition: all 0.15s;
        text-align: center;
    }
    .preset-btn:hover { border-color: #4a6cf7; color: #4a6cf7; }
    .preset-btn.active {
        background: #4a6cf7; color: #fff; border-color: #4a6cf7;
    }
    
    /* ── 주차 비교 그리드 ──────────────── */
    .week-compare-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 16px;
        margin-top: 16px;
    }
    .week-compare-grid h4 {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
        padding: 8px 12px;
        border-radius: 8px;
    }
    .week-compare-grid h4.prev { background: #f5f5f5; color: #888; }
    .week-compare-grid h4.curr { background: #e8f0fe; color: #4285F4; }
    .week-compare-grid h4.diff { background: #e6f4ea; color: #34A853; }
    
    .week-compare-grid table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: #fff;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e8eaed;
    }
    .week-compare-grid th {
        background: #f8f9fb;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        color: #555;
        border-bottom: 2px solid #e8eaed;
        white-space: nowrap;
    }
    .week-compare-grid td {
        padding: 9px 12px;
        border-bottom: 1px solid #f0f0f0;
        color: #444;
        white-space: nowrap;
    }
    
    /* ── 헤더 ──────────────────────────── */
    .page-header h2 {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 4px;
    }
    .page-header p {
        font-size: 13px;
        color: #888;
    }
    
    /* ── 유저 뱃지 ─────────────────────── */
    .user-badge {
        font-size: 12px;
        font-weight: 600;
        color: #4a6cf7;
        background: #f0f3ff;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
    }
    
    /* ── 필터 라벨 ─────────────────────── */
    .filter-label {
        font-size: 11px;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 6px;
    }
    
    /* ── selectbox 스타일 ───────────────── */
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #e0e0e0 !important;
        font-size: 13px !important;
    }
    
    /* ── 에러/경고 메시지 ──────────────── */
    .error-msg {
        background: #fff5f5;
        border: 1px solid #ffcdd2;
        border-radius: 10px;
        padding: 16px 20px;
        color: #c62828;
        font-size: 13px;
    }
    
    /* ── 반응형 ────────────────────────── */
    @media (max-width: 1200px) {
        .week-compare-grid { grid-template-columns: 1fr; }
    }
    
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ──────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    with open("data/dashboard_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    DATA = load_data()
except FileNotFoundError:
    st.error("data/dashboard_data.json 파일이 없습니다. export_data.py를 먼저 실행하세요.")
    st.stop()


def to_df(key):
    d = DATA.get(key, {"columns": [], "data": []})
    if not d["data"]:
        return pd.DataFrame()
    return pd.DataFrame(d["data"])


def num_fmt(n):
    if n is None or pd.isna(n):
        return "-"
    return f"{int(n):,}"


def pct_fmt(n):
    if n is None or pd.isna(n):
        return "-"
    return f"{n:.1f}%"


def diff_color(v):
    if v > 0:
        return f'<span style="color:#EA4335;font-weight:600">+{int(v):,}</span>'
    if v < 0:
        return f'<span style="color:#4285F4;font-weight:600">{int(v):,}</span>'
    return '<span style="color:#888">0</span>'


def diff_pct_color(cur, prev):
    if not prev or prev == 0:
        return '-'
    pct = (cur - prev) / prev * 100
    if pct > 0:
        return f'<span style="color:#EA4335;font-weight:600">+{pct:.1f}%</span>'
    if pct < 0:
        return f'<span style="color:#4285F4;font-weight:600">{pct:.1f}%</span>'
    return '<span style="color:#888">0%</span>'


def render_html_table(headers, rows):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="data-table" style="width:100%;border-collapse:collapse;font-size:13px;background:#fff;border-radius:10px;overflow:hidden;border:1px solid #e8eaed;"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def week_compare_html(prev_rows, cur_rows, label_key, value_keys, prev_label, cur_label):
    html = '<div class="week-compare-grid">'

    # 전주
    headers = [label_key] + value_keys
    prev_tr = [[r.get(label_key, '')] + [num_fmt(r.get(k, 0)) for k in value_keys] for r in prev_rows]
    html += f'<div><h4 class="prev">{prev_label}</h4>{render_html_table(headers, prev_tr)}</div>'

    # 현재
    cur_tr = [[r.get(label_key, '')] + [num_fmt(r.get(k, 0)) for k in value_keys] for r in cur_rows]
    html += f'<div><h4 class="curr">{cur_label}</h4>{render_html_table(headers, cur_tr)}</div>'

    # 증감
    prev_map = {r[label_key]: r for r in prev_rows}
    diff_h = [label_key]
    for k in value_keys:
        diff_h += [k, '증감률']
    diff_tr = []
    for r in cur_rows:
        p = prev_map.get(r.get(label_key, ''), {})
        cells = [r.get(label_key, '')]
        for k in value_keys:
            cv = r.get(k, 0) or 0
            pv = p.get(k, 0) or 0
            cells.append(diff_color(cv - pv))
            cells.append(diff_pct_color(cv, pv))
        diff_tr.append(cells)
    html += f'<div><h4 class="diff">증감</h4>{render_html_table(diff_h, diff_tr)}</div>'
    html += '</div>'
    return html


exported_at = DATA.get("_exported_at", "알 수 없음")

# ── 사이드바 ─────────────────────────────────
with st.sidebar:
    st.markdown('<h1 style="font-size:17px;font-weight:800;color:#1a1a2e;">공실 모니터링</h1>', unsafe_allow_html=True)
    st.caption(f"데이터 기준: {exported_at}")

    st.markdown('<div class="filter-label">메뉴</div>', unsafe_allow_html=True)
    menu = st.radio("메뉴", [
        "공실 현황 (서울)",
        "전국 현황",
        "가드니 공실공유",
        "매물 확보",
        "매출 분석",
        "회원 분석",
        "구독 현황",
    ], label_visibility="collapsed")

    st.divider()
    st.caption("💡 데이터 갱신: export_data.py 실행 후 push")


# ═══════════════════════════════════════════════
# 공실 현황
# ═══════════════════════════════════════════════
if menu == "공실 현황 (서울)":
    st.markdown('<div class="page-header"><h2>공실 현황 (서울)</h2><p>지역별 라이브 매물 현황과 주간 비교를 확인합니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["종합 현황", "주간 비교"])

    with tab1:
        df = to_df("vacancy_snapshot")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            total_res = int(df["주거"].sum())
            total_com = int(df["상업"].sum())
            total_all = int(df["전체"].sum())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("전체 라이브", num_fmt(total_all))
            c2.metric("주거", num_fmt(total_res), f"{total_res/total_all*100:.1f}%")
            c3.metric("상업", num_fmt(total_com), f"{total_com/total_all*100:.1f}%")
            c4.metric("지역 수", f"{len(df)}개 구")

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["지역"], y=df["주거"], name="주거", marker_color=COLORS[0]))
            fig.add_trace(go.Bar(x=df["지역"], y=df["상업"], name="상업", marker_color=COLORS[1]))
            fig.update_layout(
                barmode="group", title=f"지역별 라이브 매물 ({exported_at[:10]} 기준)",
                height=420, paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15),
                margin=dict(l=50, r=30, t=40, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)

            # HTML 테이블
            headers = ['지역', '주거', '상업', '전체']
            rows = [[r['지역'], num_fmt(r['주거']), num_fmt(r['상업']), num_fmt(r['전체'])] for _, r in df.iterrows()]
            rows.append([f'<b>합계</b>', f'<b>{num_fmt(total_res)}</b>', f'<b>{num_fmt(total_com)}</b>', f'<b>{num_fmt(total_all)}</b>'])
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        df_cur = to_df("vacancy_snapshot")
        df_prev = to_df("vacancy_snapshot_prev")

        if df_cur.empty:
            st.warning("데이터가 없습니다.")
        else:
            cur_total = int(df_cur["전체"].sum())
            prev_total = int(df_prev["전체"].sum()) if not df_prev.empty else 0
            diff = cur_total - prev_total

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("현재", num_fmt(cur_total))
            c2.metric("전주", num_fmt(prev_total))
            c3.metric("증감", f"{diff:+,}")
            c4.metric("증감률", f"{diff/prev_total*100:+.1f}%" if prev_total else "-")

            if not df_prev.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_prev["지역"], y=df_prev["전체"], name="전주", marker_color="#ddd"))
                fig.add_trace(go.Bar(x=df_cur["지역"], y=df_cur["전체"], name="현재", marker_color=COLORS[0]))
                fig.update_layout(
                    barmode="group", title="주간 비교 — 지역별 전체 매물", height=420,
                    paper_bgcolor='transparent', plot_bgcolor='transparent',
                    font=dict(family="'Noto Sans KR', sans-serif", size=12),
                    legend=dict(orientation='h', y=-0.15),
                    margin=dict(l=50, r=30, t=40, b=50)
                )
                st.plotly_chart(fig, use_container_width=True)

                prev_rows = [{'지역': r['지역'], '주거': r.get('주거', 0), '상업': r.get('상업', 0), '전체': r.get('전체', 0)} for _, r in df_prev.iterrows()]
                cur_rows = [{'지역': r['지역'], '주거': r.get('주거', 0), '상업': r.get('상업', 0), '전체': r.get('전체', 0)} for _, r in df_cur.iterrows()]
                st.markdown(week_compare_html(prev_rows, cur_rows, '지역', ['주거', '상업', '전체'], '전주', '현재'), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 전국 현황
# ═══════════════════════════════════════════════
elif menu == "전국 현황":
    st.markdown('<div class="page-header"><h2>전국 현황</h2><p>서울/경기/인천/대구/부산/울산/광주/전주/진주 등 전국의 라이브 매물 현황입니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["종합 현황", "지역 비교"])

    with tab1:
        df = to_df("nationwide_snapshot")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            total_rental = int(df["임대건수"].sum())
            total_sale = int(df["매매건수"].sum())
            total_all = int(df["전체"].sum())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("전국 임대", num_fmt(total_rental))
            c2.metric("전국 매매", num_fmt(total_sale))
            c3.metric("전국 전체", num_fmt(total_all))
            c4.metric("지역 수", f"{len(df)}개")

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["지역"], y=df["임대건수"], name="임대", marker_color=COLORS[0]))
            fig.add_trace(go.Bar(x=df["지역"], y=df["매매건수"], name="매매", marker_color=COLORS[1]))
            fig.update_layout(
                barmode="group", title=f"지역별 라이브 매물 ({exported_at[:10]} 기준)", height=420,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            headers = ['지역', '임대', '매매', '전체']
            rows = [[r['지역'], num_fmt(r['임대건수']), num_fmt(r['매매건수']), num_fmt(r['전체'])] for _, r in df.iterrows()]
            rows.append([f'<b>전국합계</b>', f'<b>{num_fmt(total_rental)}</b>', f'<b>{num_fmt(total_sale)}</b>', f'<b>{num_fmt(total_all)}</b>'])
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        df = to_df("nationwide_snapshot")
        if not df.empty:
            seoul = df[df["지역"] == "서울"]
            local = df[(df["지역"] != "서울") & (~df["지역"].str.contains("⚠", na=False))]

            seoul_total = int(seoul["전체"].sum()) if not seoul.empty else 0
            local_total = int(local["전체"].sum())
            grand = seoul_total + local_total

            c1, c2, c3 = st.columns(3)
            c1.metric("서울", num_fmt(seoul_total), f"{seoul_total/grand*100:.1f}%" if grand else "-")
            c2.metric("지방", num_fmt(local_total), f"{local_total/grand*100:.1f}%" if grand else "-")
            c3.metric("비율", f"{seoul_total/local_total:.2f} : 1" if local_total else "-", "서울:지방")

            fig = go.Figure(go.Pie(
                labels=["서울", "지방"], values=[seoul_total, local_total],
                hole=0.4, marker_colors=[COLORS[0], COLORS[1]]
            ))
            fig.update_layout(title="서울 vs 지방 공실 비중", height=400, paper_bgcolor='transparent')
            st.plotly_chart(fig, use_container_width=True)

            headers = ['지역', '임대', '매매', '전체']
            rows = [[r['지역'], num_fmt(r['임대건수']), num_fmt(r['매매건수']), num_fmt(r['전체'])] for _, r in local.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 가드니 공실공유
# ═══════════════════════════════════════════════
elif menu == "가드니 공실공유":
    st.markdown('<div class="page-header"><h2>가드니 공실공유</h2><p>가드니 부동산의 공실공유 접수/완료 현황입니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["지역별 현황", "알림톡/콜"])

    with tab1:
        df = to_df("gardni_region")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            total_req = int(df["총접수"].sum())
            total_done = int(df["거래완료"].sum())

            c1, c2, c3 = st.columns(3)
            c1.metric("총 접수", num_fmt(total_req))
            c2.metric("거래완료", num_fmt(total_done))
            c3.metric("완료율", pct_fmt(total_done/total_req*100 if total_req else 0))

            fig = go.Figure()
            for i, col in enumerate(["총접수", "거래완료", "불가"]):
                if col in df.columns:
                    fig.add_trace(go.Bar(x=df["지역"], y=df[col], name=col, marker_color=COLORS[i]))
            fig.update_layout(
                barmode="group", title="가드니 지역별 공실공유", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            # 주차 비교
            weeks = DATA.get("_weeks", [])
            if weeks:
                st.markdown('<div class="filter-label" style="margin-top:20px;">주차 선택</div>', unsafe_allow_html=True)
                sel = st.selectbox("주차", range(len(weeks)), format_func=lambda i: weeks[i]["label"], label_visibility="collapsed")
                cur_week = weeks[sel]
                cur_key = f"gardni_week_{cur_week['start'].replace('-','')}"
                df_cur_wk = to_df(cur_key)

                if not df_cur_wk.empty:
                    cur_rows = df_cur_wk.to_dict('records')
                    prev_rows = []
                    prev_label = "전주 없음"
                    if sel + 1 < len(weeks):
                        prev_week = weeks[sel + 1]
                        prev_key = f"gardni_week_{prev_week['start'].replace('-','')}"
                        df_prev_wk = to_df(prev_key)
                        if not df_prev_wk.empty:
                            prev_rows = df_prev_wk.to_dict('records')
                            prev_label = f"전주 ({prev_week['label']})"

                    cols = list(df_cur_wk.columns)
                    label_key = cols[0]
                    value_keys = [c for c in cols[1:] if df_cur_wk[c].dtype in ['int64', 'float64']]
                    st.markdown(week_compare_html(prev_rows, cur_rows, label_key, value_keys, prev_label, f"현재 ({cur_week['label']})"), unsafe_allow_html=True)

            # 전체 기간 테이블
            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else r[c] for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        df = to_df("gardni_channel")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"] and c != "총건수"]
            if num_cols:
                labels = [f"{r[df.columns[0]]} - {c}" for _, r in df.iterrows() for c in num_cols]
                values = [r[c] for _, r in df.iterrows() for c in num_cols]
                fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4, marker_colors=COLORS))
                fig.update_layout(title="알림톡/콜상담 현황", height=400, paper_bgcolor='transparent')
                st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 매물 확보
# ═══════════════════════════════════════════════
elif menu == "매물 확보":
    st.markdown('<div class="page-header"><h2>매물 확보</h2><p>채널별 공실 확보 및 현황입니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["채널별", "추이"])

    with tab1:
        df = to_df("acquisition_channel")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            cols = list(df.columns)
            label_key = cols[0]
            value_key = [c for c in cols if df[c].dtype in ["int64", "float64"]][0]

            total_row = df[df[label_key] == "공실확보(전체)"]
            done_row = df[df[label_key] == "거래완료"]
            chart_df = df[~df[label_key].isin(["공실확보(전체)", "거래완료"])]
            channel_total = int(chart_df[value_key].sum())

            c1, c2, c3 = st.columns(3)
            c1.metric("총 공실확보", num_fmt(total_row[value_key].iloc[0]) if not total_row.empty else "-")
            c2.metric("거래완료", num_fmt(done_row[value_key].iloc[0]) if not done_row.empty else "-")
            c3.metric("채널합계", num_fmt(channel_total), "인바운드+방내놓기+앱/웹+B2B")

            fig = go.Figure(go.Bar(
                x=chart_df[label_key], y=chart_df[value_key],
                marker_color=COLORS[:len(chart_df)],
                text=chart_df[value_key].apply(lambda x: f"{int(x):,}"),
                textposition="outside"
            ))
            fig.update_layout(
                title="채널별 공실확보 현황", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12)
            )
            st.plotly_chart(fig, use_container_width=True)

            # 주차 비교
            weeks = DATA.get("_weeks", [])
            if weeks:
                st.markdown('<div class="filter-label" style="margin-top:20px;">주차 선택</div>', unsafe_allow_html=True)
                sel = st.selectbox("주차", range(len(weeks)), format_func=lambda i: weeks[i]["label"], key="acq_week", label_visibility="collapsed")
                cur_week = weeks[sel]
                cur_key = f"acquisition_week_{cur_week['start'].replace('-','')}"
                df_cur_wk = to_df(cur_key)

                if not df_cur_wk.empty:
                    cur_rows = df_cur_wk.to_dict('records')
                    prev_rows = []
                    prev_label = "전주 없음"
                    if sel + 1 < len(weeks):
                        prev_week = weeks[sel + 1]
                        prev_key = f"acquisition_week_{prev_week['start'].replace('-','')}"
                        df_prev_wk = to_df(prev_key)
                        if not df_prev_wk.empty:
                            prev_rows = df_prev_wk.to_dict('records')
                            prev_label = f"전주 ({prev_week['label']})"

                    wk_cols = list(df_cur_wk.columns)
                    wk_label = wk_cols[0]
                    wk_vals = [c for c in wk_cols[1:] if df_cur_wk[c].dtype in ['int64', 'float64']]
                    st.markdown(week_compare_html(prev_rows, cur_rows, wk_label, wk_vals, prev_label, f"현재 ({cur_week['label']})"), unsafe_allow_html=True)

            headers = cols
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        unit = st.radio("단위", ["월별", "주별"], horizontal=True)
        key = "acquisition_trend_month" if unit == "월별" else "acquisition_trend_week"
        df = to_df(key)

        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            cols = list(df.columns)
            x_col = cols[0]
            num_cols = [c for c in cols if df[c].dtype in ["int64", "float64"]]

            fig = go.Figure()
            for i, c in enumerate(num_cols):
                fig.add_trace(go.Scatter(
                    x=df[x_col], y=df[c], name=c, mode="lines+markers",
                    line=dict(color=COLORS[i % len(COLORS)], width=2)
                ))
            fig.update_layout(
                title=f"매물 확보 추이 ({unit})", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            headers = cols
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 매출 분석
# ═══════════════════════════════════════════════
elif menu == "매출 분석":
    st.markdown('<div class="page-header"><h2>매출 분석</h2><p>월별 매출, 결제수단별, 상품별 분석입니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["월별 종합", "결제수단별", "상품별"])

    with tab1:
        df = to_df("revenue_monthly")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            total_rev = int(df["총매출"].sum())
            total_cnt = int(df["총결제건수"].sum())
            avg_rate = df["성공률"].mean()
            total_mem = int(df["결제회원수"].sum())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("총 매출", f"{num_fmt(total_rev)}원")
            c2.metric("총 결제건수", num_fmt(total_cnt))
            c3.metric("평균 성공률", pct_fmt(avg_rate))
            c4.metric("결제 회원수", num_fmt(total_mem))

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=df["결제월"], y=df["총매출"], name="총매출", marker_color=COLORS[0]), secondary_y=False)
            fig.add_trace(go.Scatter(x=df["결제월"], y=df["성공률"], name="성공률(%)", mode="lines+markers",
                                     line=dict(color=COLORS[1], width=2)), secondary_y=True)
            fig.update_layout(
                title="월별 매출 추이", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            fig.update_yaxes(title_text="매출(원)", secondary_y=False)
            fig.update_yaxes(title_text="성공률(%)", range=[90, 100], secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

            headers = ['결제월', '총결제건수', '성공건수', '실패건수', '총매출', '건당평균', '회원수', '성공률']
            rows = [[r['결제월'], num_fmt(r['총결제건수']), num_fmt(r['성공건수']), num_fmt(r['실패건수']),
                      num_fmt(r['총매출']), num_fmt(r['건당평균매출']), num_fmt(r['결제회원수']), pct_fmt(r['성공률'])]
                     for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        df = to_df("revenue_method")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            if "결제월" in df.columns and "결제수단" in df.columns:
                methods = df["결제수단"].unique()
                fig = go.Figure()
                for i, m in enumerate(methods):
                    f_df = df[df["결제수단"] == m]
                    fig.add_trace(go.Bar(x=f_df["결제월"], y=f_df["총매출"], name=m, marker_color=COLORS[i % len(COLORS)]))
                fig.update_layout(
                    barmode="stack", title="결제수단별 매출", height=400,
                    paper_bgcolor='transparent', plot_bgcolor='transparent',
                    font=dict(family="'Noto Sans KR', sans-serif", size=12),
                    legend=dict(orientation='h', y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab3:
        df = to_df("revenue_product")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            if "결제월" in df.columns and "상품명" in df.columns:
                product_totals = df.groupby("상품명")["총매출"].sum().sort_values(ascending=False)
                top5 = product_totals.head(5).index.tolist()
                top_df = df[df["상품명"].isin(top5)]

                fig = go.Figure()
                for i, p in enumerate(top5):
                    f_df = top_df[top_df["상품명"] == p]
                    fig.add_trace(go.Bar(x=f_df["결제월"], y=f_df["총매출"], name=str(p), marker_color=COLORS[i % len(COLORS)]))
                fig.update_layout(
                    barmode="stack", title="상품별 매출 TOP5", height=400,
                    paper_bgcolor='transparent', plot_bgcolor='transparent',
                    font=dict(family="'Noto Sans KR', sans-serif", size=12),
                    legend=dict(orientation='h', y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 회원 분석
# ═══════════════════════════════════════════════
elif menu == "회원 분석":
    st.markdown('<div class="page-header"><h2>회원 분석</h2><p>신규/기존 회원, 활성화율, 전환율 분석입니다.</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["신규/기존", "활성화율", "가입전환", "TOP5 상품"])

    with tab1:
        df = to_df("member_new_vs_existing")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]
            fig = go.Figure()
            for i, c in enumerate(num_cols):
                fig.add_trace(go.Bar(x=df["결제월"], y=df[c], name=c, marker_color=COLORS[i % len(COLORS)]))
            fig.update_layout(
                barmode="group", title="신규/기존 회원 매출", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab2:
        df = to_df("member_activation")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]
            fig = go.Figure()
            for i, c in enumerate(num_cols):
                fig.add_trace(go.Scatter(x=df[df.columns[0]], y=df[c], name=c, mode="lines+markers",
                                         line=dict(color=COLORS[i % len(COLORS)], width=2)))
            fig.update_layout(
                title="회원 활성화율", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab3:
        df = to_df("member_conversion")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]
            fig = go.Figure()
            for i, c in enumerate(num_cols):
                fig.add_trace(go.Scatter(x=df[df.columns[0]], y=df[c], name=c, mode="lines+markers",
                                         line=dict(color=COLORS[i % len(COLORS)], width=2)))
            fig.update_layout(
                title="가입 전환율", height=400,
                paper_bgcolor='transparent', plot_bgcolor='transparent',
                font=dict(family="'Noto Sans KR', sans-serif", size=12),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)

    with tab4:
        df = to_df("member_top5")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            if "상품명" in df.columns and "회원구분" in df.columns:
                product_totals = df.groupby("상품명")["총매출"].sum().sort_values(ascending=False)
                top5 = product_totals.head(5).index.tolist()

                member_types = df["회원구분"].unique()
                fig = go.Figure()
                for i, mt in enumerate(member_types):
                    subset = df[(df["회원구분"] == mt) & (df["상품명"].isin(top5))]
                    by_prod = subset.groupby("상품명")["총매출"].sum()
                    fig.add_trace(go.Bar(
                        y=[str(p) for p in top5], x=[by_prod.get(p, 0) for p in top5],
                        name=mt, orientation="h", marker_color=COLORS[i % len(COLORS)]
                    ))
                fig.update_layout(
                    barmode="group", title="TOP5 상품별 매출", height=400,
                    paper_bgcolor='transparent', plot_bgcolor='transparent',
                    font=dict(family="'Noto Sans KR', sans-serif", size=12),
                    legend=dict(orientation='h', y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

            headers = list(df.columns)
            rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
            st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# 구독 현황
# ═══════════════════════════════════════════════
elif menu == "구독 현황":
    st.markdown('<div class="page-header"><h2>구독 현황</h2><p>정기결제 현황 및 추이입니다.</p></div>', unsafe_allow_html=True)

    df = to_df("subscription_monthly")

    if df.empty:
        st.info("구독(BILL_MONTHLY_INFO) 데이터가 없습니다. 매출 기반 정기결제 현황을 표시합니다.")

        df_rev = to_df("revenue_monthly")
        df_method = to_df("revenue_method")

        if not df_method.empty:
            sub_methods = ["토스_정기결제", "토스_정기결제_자동"]
            sub_df = df_method[df_method["결제수단"].isin(sub_methods)]

            total_sub_rev = int(sub_df["총매출"].sum()) if not sub_df.empty else 0
            total_rev = int(df_rev["총매출"].sum()) if not df_rev.empty else 0
            sub_share = (total_sub_rev / total_rev * 100) if total_rev else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("정기결제 매출", f"{num_fmt(total_sub_rev)}원", f"전체 {sub_share:.1f}%")
            c2.metric("정기결제 건수", num_fmt(int(sub_df["성공건수"].sum())) if not sub_df.empty else "-")
            c3.metric("비중", f"{sub_share:.1f}%")

            if not df_rev.empty:
                months = sorted(df_rev["결제월"].unique())
                sub_by_month = sub_df.groupby("결제월")["총매출"].sum() if not sub_df.empty else pd.Series(dtype=float)

                fig = go.Figure()
                fig.add_trace(go.Bar(x=months, y=[int(df_rev[df_rev["결제월"]==m]["총매출"].sum()) for m in months],
                                     name="전체 매출", marker_color="#e0e0e0"))
                fig.add_trace(go.Bar(x=months, y=[int(sub_by_month.get(m, 0)) for m in months],
                                     name="정기결제 매출", marker_color=COLORS[4]))
                fig.update_layout(
                    barmode="overlay", title="월별 정기결제 매출 비중", height=400,
                    paper_bgcolor='transparent', plot_bgcolor='transparent',
                    font=dict(family="'Noto Sans KR', sans-serif", size=12),
                    legend=dict(orientation='h', y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

                headers = ['결제월', '전체매출', '정기결제매출', '비중(%)']
                rows = [[m, num_fmt(int(df_rev[df_rev["결제월"]==m]["총매출"].sum())),
                          num_fmt(int(sub_by_month.get(m, 0))),
                          f'{sub_by_month.get(m, 0) / df_rev[df_rev["결제월"]==m]["총매출"].sum() * 100:.1f}%'
                          if df_rev[df_rev["결제월"]==m]["총매출"].sum() > 0 else '-']
                         for m in months]
                st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)
    else:
        num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]
        label_col = [c for c in df.columns if c not in num_cols][0] if any(c not in num_cols for c in df.columns) else df.columns[0]

        priority = ["구독건수", "예상월매출", "결제완료수", "정기결제성공률"]
        chart_cols = [c for c in priority if c in num_cols]
        if not chart_cols:
            chart_cols = num_cols[:4]

        if len(df) > 0:
            last = df.iloc[-1]
            cols_st = st.columns(len(chart_cols))
            for i, c in enumerate(chart_cols):
                cols_st[i].metric(c, num_fmt(last[c]), "최근 월 기준")

        fig = go.Figure()
        for i, c in enumerate(chart_cols):
            is_rev = "매출" in c or "금액" in c
            if is_rev:
                fig.add_trace(go.Bar(x=df[label_col], y=df[c], name=c, marker_color=COLORS[i % len(COLORS)]))
            else:
                fig.add_trace(go.Scatter(x=df[label_col], y=df[c], name=c, mode="lines+markers",
                                         line=dict(color=COLORS[i % len(COLORS)], width=2)))
        fig.update_layout(
            title="구독 월별 추이", height=420,
            paper_bgcolor='transparent', plot_bgcolor='transparent',
            font=dict(family="'Noto Sans KR', sans-serif", size=12),
            legend=dict(orientation='h', y=-0.15)
        )
        st.plotly_chart(fig, use_container_width=True)

        headers = list(df.columns)
        rows = [[num_fmt(r[c]) if isinstance(r[c], (int, float)) else (r[c] or '') for c in headers] for _, r in df.iterrows()]
        st.markdown(render_html_table(headers, rows), unsafe_allow_html=True)
