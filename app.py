"""공실관리 대시보드 — Streamlit (JSON 기반)"""
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── 페이지 설정 ──────────────────────────────
st.set_page_config(page_title="공실관리 대시보드", layout="wide", initial_sidebar_state="expanded")

COLORS = ['#4285F4','#EA4335','#FBBC04','#34A853','#FF6D01','#46BDC6','#7B61FF','#F538A0','#00ACC1','#8D6E63']

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

exported_at = DATA.get("_exported_at", "알 수 없음")

# ── 사이드바 ─────────────────────────────────
with st.sidebar:
    st.title("공실 모니터링")
    st.caption(f"데이터 기준: {exported_at}")

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
    st.caption("💡 데이터 갱신이 필요하면\nexport_data.py 실행 후 push")


# ═══════════════════════════════════════════════
# 공실 현황
# ═══════════════════════════════════════════════
if menu == "공실 현황 (서울)":
    st.header("공실 현황 (서울)")
    st.caption("지역별 라이브 매물 현황과 주간 비교를 확인합니다.")

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
            fig.update_layout(barmode="group", title="지역별 라이브 매물", height=420)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        df_cur = to_df("vacancy_snapshot")
        df_prev = to_df("vacancy_snapshot_prev")

        if df_cur.empty:
            st.warning("데이터가 없습니다.")
        else:
            cur_total = int(df_cur["전체"].sum())
            prev_total = int(df_prev["전체"].sum()) if not df_prev.empty else 0
            diff = cur_total - prev_total

            c1, c2, c3 = st.columns(3)
            c1.metric("현재", num_fmt(cur_total))
            c2.metric("전주", num_fmt(prev_total))
            c3.metric("증감", f"{diff:+,}", f"{diff/prev_total*100:+.1f}%" if prev_total else "-")

            if not df_prev.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_prev["지역"], y=df_prev["전체"], name="전주", marker_color="#ddd"))
                fig.add_trace(go.Bar(x=df_cur["지역"], y=df_cur["전체"], name="현재", marker_color=COLORS[0]))
                fig.update_layout(barmode="group", title="주간 비교", height=420)
                st.plotly_chart(fig, use_container_width=True)

                merged = pd.merge(df_prev, df_cur, on="지역", suffixes=("_전주", "_현재"), how="outer").fillna(0)
                for col in ["주거", "상업", "전체"]:
                    merged[f"{col}_증감"] = merged[f"{col}_현재"].astype(int) - merged[f"{col}_전주"].astype(int)
                st.dataframe(merged, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# 전국 현황
# ═══════════════════════════════════════════════
elif menu == "전국 현황":
    st.header("전국 현황")
    st.caption("서울/경기/인천/대구/부산/울산/광주/전주/진주 등 전국의 라이브 매물 현황입니다.")

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
            fig.update_layout(barmode="group", title="지역별 라이브 매물", height=420)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        df = to_df("nationwide_snapshot")
        if not df.empty:
            seoul = df[df["지역"] == "서울"]
            local = df[(df["지역"] != "서울") & (~df["지역"].str.contains("⚠", na=False))]

            seoul_total = int(seoul["전체"].sum()) if not seoul.empty else 0
            local_total = int(local["전체"].sum())

            c1, c2, c3 = st.columns(3)
            c1.metric("서울", num_fmt(seoul_total), f"{seoul_total/(seoul_total+local_total)*100:.1f}%")
            c2.metric("지방", num_fmt(local_total), f"{local_total/(seoul_total+local_total)*100:.1f}%")
            c3.metric("비율", f"{seoul_total/local_total:.2f} : 1" if local_total else "-", "서울:지방")

            fig = go.Figure(go.Pie(
                labels=["서울", "지방"], values=[seoul_total, local_total],
                hole=0.4, marker_colors=[COLORS[0], COLORS[1]]
            ))
            fig.update_layout(title="서울 vs 지방 공실 비중", height=400)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(local, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# 가드니 공실공유
# ═══════════════════════════════════════════════
elif menu == "가드니 공실공유":
    st.header("가드니 공실공유")
    st.caption("가드니 부동산의 공실공유 접수/완료 현황입니다.")

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
            fig.update_layout(barmode="group", title="가드니 지역별 공실공유", height=400)
            st.plotly_chart(fig, use_container_width=True)

            # 주차 비교
            weeks = DATA.get("_weeks", [])
            if weeks:
                st.subheader("주차별 비교")
                sel = st.selectbox("주차 선택", range(len(weeks)), format_func=lambda i: weeks[i]["label"])
                cur_week = weeks[sel]
                cur_key = f"gardni_week_{cur_week['start'].replace('-','')}"
                df_cur_wk = to_df(cur_key)

                prev_key = None
                if sel + 1 < len(weeks):
                    prev_week = weeks[sel + 1]
                    prev_key = f"gardni_week_{prev_week['start'].replace('-','')}"

                if not df_cur_wk.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**현재 ({cur_week['label']})**")
                        st.dataframe(df_cur_wk, use_container_width=True, hide_index=True)
                    with col2:
                        if prev_key:
                            df_prev_wk = to_df(prev_key)
                            st.markdown(f"**전주 ({weeks[sel+1]['label']})**")
                            st.dataframe(df_prev_wk, use_container_width=True, hide_index=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        df = to_df("gardni_channel")
        if df.empty:
            st.warning("데이터가 없습니다.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"] and c != "총건수"]
            if num_cols:
                fig = go.Figure(go.Pie(
                    labels=[f"{r[df.columns[0]]} - {c}" for _, r in df.iterrows() for c in num_cols],
                    values=[r[c] for _, r in df.iterrows() for c in num_cols],
                    hole=0.4, marker_colors=COLORS
                ))
                fig.update_layout(title="알림톡/콜상담 현황", height=400)
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════
# 매물 확보
# ═══════════════════════════════════════════════
elif menu == "매물 확보":
    st.header("매물 확보")
    st.caption("채널별 공실 확보 및 현황입니다.")

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

            c1, c2 = st.columns(2)
            c1.metric("총 공실확보", num_fmt(total_row[value_key].iloc[0]) if not total_row.empty else "-")
            c2.metric("거래완료", num_fmt(done_row[value_key].iloc[0]) if not done_row.empty else "-")

            fig = go.Figure(go.Bar(
                x=chart_df[label_key], y=chart_df[value_key],
                marker_color=COLORS[:len(chart_df)],
                text=chart_df[value_key].apply(lambda x: f"{int(x):,}"),
                textposition="outside"
            ))
            fig.update_layout(title="채널별 공실확보 현황", height=400)
            st.plotly_chart(fig, use_container_width=True)

            # 주차 비교
            weeks = DATA.get("_weeks", [])
            if weeks:
                st.subheader("주차별 비교")
                sel = st.selectbox("주차 선택", range(len(weeks)), format_func=lambda i: weeks[i]["label"], key="acq_week")
                cur_week = weeks[sel]
                cur_key = f"acquisition_week_{cur_week['start'].replace('-','')}"
                df_cur_wk = to_df(cur_key)

                if not df_cur_wk.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**현재 ({cur_week['label']})**")
                        st.dataframe(df_cur_wk, use_container_width=True, hide_index=True)
                    with col2:
                        if sel + 1 < len(weeks):
                            prev_week = weeks[sel + 1]
                            prev_key = f"acquisition_week_{prev_week['start'].replace('-','')}"
                            df_prev_wk = to_df(prev_key)
                            st.markdown(f"**전주 ({weeks[sel+1]['label']})**")
                            st.dataframe(df_prev_wk, use_container_width=True, hide_index=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

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
            fig.update_layout(title=f"매물 확보 추이 ({unit})", height=400)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# 매출 분석
# ═══════════════════════════════════════════════
elif menu == "매출 분석":
    st.header("매출 분석")
    st.caption("월별 매출, 결제수단별, 상품별 분석입니다.")

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
            fig.update_layout(title="월별 매출 추이", height=400)
            fig.update_yaxes(title_text="매출(원)", secondary_y=False)
            fig.update_yaxes(title_text="성공률(%)", range=[90, 100], secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

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
                fig.update_layout(barmode="stack", title="결제수단별 매출", height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

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
                    fig.add_trace(go.Bar(x=f_df["결제월"], y=f_df["총매출"], name=p, marker_color=COLORS[i % len(COLORS)]))
                fig.update_layout(barmode="stack", title="상품별 매출 TOP5", height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# 회원 분석
# ═══════════════════════════════════════════════
elif menu == "회원 분석":
    st.header("회원 분석")
    st.caption("신규/기존 회원, 활성화율, 전환율 분석입니다.")

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
            fig.update_layout(barmode="group", title="신규/기존 회원 매출", height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

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
            fig.update_layout(title="회원 활성화율", height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

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
            fig.update_layout(title="가입 전환율", height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

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
                        y=[p for p in top5], x=[by_prod.get(p, 0) for p in top5],
                        name=mt, orientation="h", marker_color=COLORS[i % len(COLORS)]
                    ))
                fig.update_layout(barmode="group", title="TOP5 상품별 매출", height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# 구독 현황
# ═══════════════════════════════════════════════
elif menu == "구독 현황":
    st.header("구독 현황")
    st.caption("정기결제 현황 및 추이입니다.")

    df = to_df("subscription_monthly")
    df_summary = to_df("subscription_summary")

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
                sub_by_month = sub_df.groupby("결제월")["총매출"].sum() if not sub_df.empty else pd.Series()

                fig = go.Figure()
                fig.add_trace(go.Bar(x=months, y=[df_rev[df_rev["결제월"]==m]["총매출"].sum() for m in months],
                                     name="전체 매출", marker_color="#e0e0e0"))
                fig.add_trace(go.Bar(x=months, y=[sub_by_month.get(m, 0) for m in months],
                                     name="정기결제 매출", marker_color=COLORS[4]))
                fig.update_layout(barmode="overlay", title="월별 정기결제 매출 비중", height=400)
                st.plotly_chart(fig, use_container_width=True)
    else:
        num_cols = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]
        label_col = [c for c in df.columns if c not in num_cols][0] if any(c not in num_cols for c in df.columns) else df.columns[0]

        priority = ["구독건수", "예상월매출", "결제완료수", "정기결제성공률"]
        chart_cols = [c for c in priority if c in num_cols]
        if not chart_cols:
            chart_cols = num_cols[:4]

        if len(df) > 0:
            last = df.iloc[-1]
            cols = st.columns(len(chart_cols))
            for i, c in enumerate(chart_cols):
                cols[i].metric(c, num_fmt(last[c]), "최근 월 기준")

        fig = go.Figure()
        for i, c in enumerate(chart_cols):
            is_rev = "매출" in c or "금액" in c
            if is_rev:
                fig.add_trace(go.Bar(x=df[label_col], y=df[c], name=c, marker_color=COLORS[i % len(COLORS)]))
            else:
                fig.add_trace(go.Scatter(x=df[label_col], y=df[c], name=c, mode="lines+markers",
                                         line=dict(color=COLORS[i % len(COLORS)], width=2)))
        fig.update_layout(title="구독 월별 추이", height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)
