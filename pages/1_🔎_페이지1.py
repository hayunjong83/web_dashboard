import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# 필요한 페이지 설정을 수행한다.
st.set_page_config(
    page_title="미국 주별 인구 대시보드",
    layout="wide",
    initial_sidebar_state="expanded")

# 사용자가 선택할 수 있는 요소를 사이드바에 배치한다.
with st.sidebar:
  # 사이드바에 제목을 추가한다.
  st.title("2010~2019 미국 주별 인구")

  # 연도를 선택할 수 있게한다.
  years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
  selected_year = st.selectbox('연도 선택', years)

# 데이터를 불러온다. 데이터는 대시보드가 구현된 1_페이지_1.py에 대한 경로가 아니다.
# 멀티페이지를 실행하는 Dashboard.py에 대한 상대경로로 불러야한다.
path = "./example_data/ex1.csv"
df = pd.read_csv(path)

# 크게 세 개의 영역으로 나눠 대시보드 내용을 구성한다.
# 이 때, 비율은 임의로 [1.5, 4.5, 2]의 비율로 설정한다.
col = st.columns([1.5, 4.5, 2])

with col[0]:
  # 2010년이 아닌 경우에는, 이전 연도와의 인구수 변화를 구한다.
  if selected_year != "2010":
    df_selected_year = df[df["year"] == selected_year].reset_index()
    df_previous_year = df[df["year"] == (selected_year-1)].reset_index()
    df_selected_year["difference"] = df_selected_year["population"] - df_previous_year["population"]

    # 인구증가가 5만명보다 큰 주들을 선택하고 비율을 구한다.
    df_increase = df_selected_year[df_selected_year["difference"] > 50000]
    df_increase_ratio = round(len(df_increase) / len(df_selected_year) * 100)
    # 인구감소가 5만명보다 큰 주들을 선택
    df_decrease = df_selected_year[df_selected_year["difference"] < -50000]
    df_decrease_ratio = round(len(df_decrease) / len(df_selected_year) * 100)

    # 도넛차트를 그리기 위한 임의의 데이터프레임을 만들어준다.
    st.subheader("인구증가 주 비율")
    new_df_increase = pd.DataFrame({
      "표현값" : ["증가 비율", "나머지 비율"],
      "value" : [df_increase_ratio, 100- df_increase_ratio]
    })
    increase_dount = alt.Chart(new_df_increase).mark_arc(innerRadius=40, cornerRadius=25).encode(
      theta = "value", color = alt.Color("표현값:N", legend = None)
    ).properties(width=130, height=130)
    text = increase_dount.mark_text(align='center', fontSize=30).encode(text=alt.value(f'{df_increase_ratio} %'))
    st.altair_chart(increase_dount + text)

    # 동일한 방식을 감소한 주에 대해서도 적용한다.
    st.subheader("인구감소 주 비율")
    new_df_decrease = pd.DataFrame({
      "표현값" : ["감소 비율", "나머지 비율"],
      "value" : [df_decrease_ratio, 100- df_decrease_ratio]
    })
    decrease_dount = alt.Chart(new_df_decrease).mark_arc(innerRadius=40, cornerRadius=25).encode(
      theta = "value", color = alt.Color("표현값:N", legend = None)
    ).properties(width=130, height=130)
    text = decrease_dount.mark_text(align='center', fontSize=30).encode(text=alt.value(f'{df_decrease_ratio} %'))
    st.altair_chart(decrease_dount + text)


with col[1]:
  st.subheader(f"{selected_year}년 전체 인구수")
  # 선택된 연도의 인구 데이터만 추출한다.
  # 컬럼명 year가 사이드바에서 선택된 selected_year와 동일한 데이터를 추출한다.
  df_selected_year = df[df["year"] == selected_year]
  choropleth = px.choropleth(
    df_selected_year,    # 사용할 데이터프레임
    locations = "states_code",      # 사용할 데이터프레임에서 위치를 구분하는 컬럼명
    locationmode= "USA-states",      # 주 코드를 사용해 구분하기 위한 지도 모드(위치해석방식)
    color = "population",           # 단계구분도에서 색상으로 나타낼 컬럼명
    scope = "usa",                  # 미국만 그린다.
    labels = {"population": "주별인구"}   # 나타낼 레이블명
  )

  st.plotly_chart(choropleth)

  heatmap = alt.Chart(df).mark_rect().encode(
    x = alt.X('states'), y = alt.Y('year:O'), color = alt.Color('population') 
  ).properties()

  st.altair_chart(heatmap)

with col[2]:
  st.subheader('인구수 상위 주')
  df_selected_year = df_selected_year.sort_values(by="population", ascending=False)

  st.dataframe(df_selected_year,
              column_order=("states", "population"),
              hide_index=True,
              width=None,
              column_config={
                "states": st.column_config.TextColumn("States",),
                "population": st.column_config.ProgressColumn(
                  "Population",
                      format="%f",
                      min_value=0,
                      max_value=max(df_selected_year.population),
                    )}
                )