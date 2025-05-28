import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 페이지를 넓게 사용하기 위하여, 좌우 여백을 없앤다.
st.set_page_config(layout="wide")

# 데이터를 불러오는 함수
# @st.cache_data를 붙여두면, 새로고침시마다 불러온 데이터를 그대로 사용할 수 있어서 연산 시간이 줄어들 수 있다.
@st.cache_data
def load_dataset1():
  # 데이터경로는 메인실행파일인 Dashboard.py에 대한 경로여야 한다.
  path= './data/data1.csv'
  # 주요 데이터의 데이터타입 변화
  df = pd.read_csv(path)
  df["연도"] = df["연도"].astype(int)
  df["사업체수(개)"] = df["사업체수(개)"].astype(int)
  df["종사자수(명)"] = df["종사자수(명)"].astype(int)
  df["매출액(백만원)"] = df["매출액(백만원)"].astype(int)
  return df

df = load_dataset1()

# 대시보드의 제목
st.title("2016년~2023년 지역별 외식산업현황")
st.markdown(""" 
            [외식산업통계](https://www.atfis.or.kr/fip/front/M000000268/stats/service.do)에 근거하여
            2016년~2023년 사이의 외식산업의 주요 지표 변화를 지역별로 살펴볼 수 있습니다.""")

# 항목 1 - 주요지표를 특정 자역 그리고 연도 구간에 대하여 비교한다.
# 주요 지표 종류 : 사업체수(개), 종사자수(명), 매출액(백만원)
# 선택 가능 연도 : 2016 ~ 2023
# 선택 가능한 지역 : 전국 + 17개 주요시도
regions = [
    "전국", "서울특별시", "부산광역시", "대구광역시", "인천광역시",
    "광주광역시", "대전광역시", "울산광역시", "세종특별자치시",
    "경기도", "강원도", "충청북도", "충청남도", "전라북도",
    "전라남도", "경상북도", "경상남도", "제주특별자치도"
    ]

# 사이드바에 항목 1을 위한 연도와 지역을 선택한다.
with st.sidebar:
  st.title("📅 필터 선택")
  section1_years = st.slider( "연도 선택",min_value=2016, max_value=2023, value=(2016, 2023))
  section1_region = st.selectbox( "지역 선택", regions)

  # 선택된 연도와 지역을 기반으로 데이터를 필터링한다.
  filtered = df[
    (df["연도"] >= section1_years[0]) & (df["연도"] <= section1_years[1]) &
    (df["지역"] == section1_region)
    ]
  
  # 선택된 데이터의 인덱스를 "연도"로 설정해서, 그래프에서 레이블로 나타나게 한다.
  grouped = filtered.copy().reset_index()
  grouped.set_index("연도", inplace=True)

st.divider()
st.subheader(f"📊{section1_years[0]}년 ~ {section1_years[1]}년 주요 지표 변화")
s1_col1, s1_col2, s1_col3 = st.columns(3)
# 그래프는 st.bar_chart()를 이용하여 간단하게 그려준다.
with s1_col1:
  st.markdown("#### 사업체수(개)")
  st.bar_chart(grouped["사업체수(개)"])

with s1_col2:
  st.markdown("#### 종사자수(명)")
  st.bar_chart(grouped["종사자수(명)"])

with s1_col3:
  st.markdown("#### 매출액(백만원)")
  st.bar_chart(grouped["매출액(백만원)"])

st.divider()
st.subheader(f"🌍시도별 외식산업 현황")
s2_col1, s2_col2, = st.columns(2)
with s2_col1 :
  section2_year = st.selectbox("연도 선택", sorted(df["연도"].unique(), reverse=True))
with s2_col2:
  section2_metric = st.radio("항목 선택", ["사업체수(개)", "종사자수(명)", "매출액(백만원)"], horizontal=True)

filtered = df[(df["연도"] == section2_year)]
# 시도 구분 데이터를 불러온다.
with open("./data/korea-geo.json", encoding="utf-8") as f:
    geojson = json.load(f)

map_col, table_col = st.columns([1, 1])

with map_col:
  st.markdown(f"#### 🗺️ {section2_year}년 {section2_metric}의 지역별 분포")
  fig = px.choropleth_map(
      filtered,
      geojson=geojson,
      locations="지역",                  # 데이터프레임에서 지역을 나타내는 컬럼명 - 데이터에 맞춰 변경
      featureidkey="properties.name",   # 지도 데이터에서 지역을 나타내는 속성명 - 변경하지 않는다.
      color=section2_metric,            # 색상으로 구분하려는 주요 지표 : 라디오버튼에서 선택된다.
      hover_name="지역",                 # 데이터프레임에서 지역을 나타내는 컬럼명 - 데이터에 맞춰 변경
      map_style="carto-positron",
      color_continuous_scale="YlOrRd",
      center={"lat": 36.5, "lon": 127.8},
      zoom=5.5,
      opacity=0.8,
      height=700
  )

  st.plotly_chart(fig, use_container_width=True)

with table_col:
  st.markdown(f"#### 🗺️ {section2_year}년 {section2_metric}의 지역별 분포표")
  display_df = filtered[["지역", section2_metric]].sort_values(by=section2_metric, ascending=False)
  display_df = display_df.reset_index(drop=True)
  st.dataframe(display_df, use_container_width=True, height=500)
