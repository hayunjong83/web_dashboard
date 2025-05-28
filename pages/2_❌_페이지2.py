import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")

@st.cache_data
def load_dataset2():
  path = "./data/data2.csv"
  df = pd.read_csv(path)
  df = df.rename(columns={
      "자치구별(2)": "자치구", 
      "2024": "선거인수", 
      "2024.1": "총투표자", 
      "2024.2": "투표율"
      })
  df["투표율"] = pd.to_numeric(df["투표율"], errors='coerce')
  df["선거인수"] = pd.to_numeric(df["선거인수"], errors="coerce")
  df["총투표자"] = pd.to_numeric(df["총투표자"], errors="coerce")
  df = df[df["자치구"].notna()]
  return df

df = load_dataset2()

with open("./data/seoul_municipalities_geo_simple.json", encoding="utf-8") as f:
    geojson = json.load(f)

st.title("🗳️ 2024년 서울시 국회의원 선거 결과 분석 대시보드")

col1, col2 = st.columns([7, 3])
with col2:
  selected_metric = st.radio("지도에 표시할 항목을 선택하세요:",
                            ["투표율", "선거인수", "총투표자"], horizontal=True)

  gu_list = ["전체"] + df["자치구"].unique().tolist()
  selected_gu = st.selectbox("자치구 선택", gu_list)

  if selected_gu != "전체":
    gu_row = df[df["자치구"] == selected_gu].iloc[0]
    total_row = df[df["자치구"] == "소계"].iloc[0]

    # st.subheader(f"📊 {selected_gu} 상세 정보")

    st.metric(f"{selected_metric}", f"{gu_row[selected_metric]:,.1f}" if selected_metric == "투표율"
  else f"{int(gu_row[selected_metric]):,}")
    
    small_col1, small_col2 = st.columns(2)
    with small_col1:
      seoul_avg = total_row[selected_metric]
      delta = gu_row[selected_metric] - seoul_avg
      st.metric("서울시 평균 대비", f"{delta:+.1f}" if selected_metric == "투표율" else f"{int(delta):+,.0f}",
                delta_color="inverse")
    with small_col2:
    # ③ 서울 전체 vs 선택 구 비교 그래프
      compare_df = pd.DataFrame({
          "항목": [selected_metric],
          "서울시 전체": [seoul_avg],
          f"{selected_gu}": [gu_row[selected_metric]]
      })
      fig_bar = go.Figure(data=[
          go.Bar(name="서울시 전체", x=compare_df["항목"], y=compare_df["서울시 전체"], marker_color="gray"),
          go.Bar(name=selected_gu, x=compare_df["항목"], y=compare_df[selected_gu], marker_color="steelblue")
      ])
      fig_bar.update_layout(barmode='group', height=400)
      st.plotly_chart(fig_bar, use_container_width=True)


with col1: 
  st.subheader(f"📍 서울시 자치구별 {selected_metric}")
  map_df = df[df["자치구"] != "소계"]
  if selected_gu == "전체" or selected_gu == "소계":
     map_df = df[df["자치구"] != "소계"]
  else:
     map_df = df[df["자치구"] == selected_gu]

  fig = px.choropleth_mapbox(
      map_df,
      geojson=geojson,
      locations="자치구",
      featureidkey="properties.name",
      color=selected_metric,
      hover_data=["자치구", selected_metric],
      mapbox_style="carto-positron",
      center={"lat": 37.5665, "lon": 126.9780},
      zoom=9.5,
      color_continuous_scale="Blues",
      height=600
  )
  st.plotly_chart(fig, use_container_width=True)


below_col1, below_col2 = st.columns([3, 5])
with below_col1:
  st.subheader("📌 자치구별 비교")
  selected_gus = st.multiselect("여러 자치구를 선택해 비교해보세요:",
                                df[df["자치구"] != "소계"]["자치구"].unique(),
                                default=["종로구", "강남구"])

with below_col2:
  if selected_gus:
      multi_df = df[df["자치구"].isin(selected_gus)]
      fig_multi = px.bar(multi_df,
                        x="자치구",
                        y=selected_metric,
                        color="자치구",
                        title=f"{selected_metric} 비교",
                        height=400)
      st.plotly_chart(fig_multi, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📁 전체 데이터 다운로드", data=csv, file_name="서울시_투표현황_2024.csv", mime='text/csv')
