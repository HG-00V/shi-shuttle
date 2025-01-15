import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time as tm

# 셔틀 노선 데이터 (운행시간 및 정류장 포함)
shuttle_data = {
    "노선": ["A", "C", "J1", "J2", "K"],
    "운행시간": [
        ["10:02", "10:32", "11:02", "11:32", "12:02", "12:32", "13:02", "13:32", "14:02", "14:32", "15:02", "15:32", "16:02"],  # A
        ["10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00"],  # C
        ["10:40", "11:10", "11:40", "12:10", "12:40", "13:10", "13:40", "14:10", "14:40", "15:10", "15:40", "16:10"],  # J1
        ["10:50", "11:20", "11:50", "12:20", "12:50", "13:20", "13:50", "14:20", "14:50", "15:20", "15:50", "16:20"],  # J2
        ["10:25", "10:55", "11:25", "11:55", "12:25", "12:55", "13:25", "13:55", "14:25", "14:55", "15:25", "15:55"],  # K
    ],
    "정류장": [
        ["가로지식당", "여객선공장", "회사정문", "공장정문", "설계1관", "한마음관", "3도크헤드", "D식당", "피솔관", "G3도크입구","사곡공장"],  # A
        ["가로지식당", "여객선공장", "회사정문", "의장관", "B식당", "1도크헤드", "선각공장", "A식당", "LNG관", "K안벽"],  # C
        ["사곡공장", "G3도크입구", "피솔관", "D식당", "6안벽관", "J안벽"],  # J1
        ["가로지식당", "여객선공장", "회사정문", "공장정문", "설계1관", "해양삼거리", "C2식당", "해양관", "6안벽관","J안벽"],  # J2
        ["사곡공장", "G3도크입구", "피솔관", "D식당", "6안벽관", "해양관", "C2식당", "LNG관", "K안벽"],  # K
    ],
    "색상": ["red", "blue","yellow", "pink", "green"]
}

# 데이터프레임으로 변환
shuttle_df = pd.DataFrame(shuttle_data)

# Streamlit UI 설정
st.set_page_config(page_title="셔틀 노선 추천", page_icon=":bus:")
st.header("셔틀 노선 추천 시스템")

# 화면 분할
col1, col2 = st.columns([3, 2])
with col1:
    st.image("사내셔틀노선.jpg")  # 셔틀 노선 사진 경로
with col2:
    # 모든 노선의 정류장을 합치고 중복 제거
    all_stops = set(stop for stops in shuttle_data["정류장"] for stop in stops)

    # 출발지와 도착지 선택
    col3, col4 = st.columns([1, 1])  # 드롭박스 크기 조정
    with col3:
        departure = st.selectbox("출발지 선택", sorted(all_stops))  # 모든 정류장 사용
    with col4:
        arrival = st.selectbox("도착지 선택", sorted(all_stops))  # 모든 정류장 사용

    # 추천 경로 버튼
    if st.button("추천 경로"):
        time_placeholder = st.empty()
        next_bus_placeholder = st.empty()

        # 추천 노선 찾기
        recommended_routes = []
        for index, row in shuttle_df.iterrows():
            # 출발지와 도착지가 모두 포함된 노선만 고려
            if departure in row["정류장"] and arrival in row["정류장"]:
                for time in row["운행시간"]:
                    if time > datetime.now().strftime("%H:%M"):
                        next_bus_time = datetime.strptime(time, "%H:%M")
                        current_time_dt = datetime.now()
                        time_diff = next_bus_time - current_time_dt
                        recommended_routes.append((row["노선"], time, row["색상"], time_diff))
                        break

        if not recommended_routes:
            # 환승 고려
            for index, row in shuttle_df.iterrows():
                if departure in row["정류장"]:
                    for transfer_stop in row["정류장"]:
                        if transfer_stop != departure:
                            for index2, row2 in shuttle_df.iterrows():
                                if transfer_stop in row2["정류장"] and arrival in row2["정류장"]:
                                    for time in row["운행시간"]:
                                        if time > datetime.now().strftime("%H:%M"):
                                            next_bus_time = datetime.strptime(time, "%H:%M")
                                            current_time_dt = datetime.now()
                                            time_diff = next_bus_time - current_time_dt
                                            # 가장 가까운 환승지 찾기
                                            transfer_time_diff = abs(row["정류장"].index(transfer_stop) - row["정류장"].index(departure))
                                            recommended_routes.append((row["노선"], time, row["색상"], time_diff, transfer_stop, row2["노선"], transfer_time_diff))
                                            break

        if recommended_routes:
            # 가장 빠른 버스 및 가장 가까운 환승지 찾기
            fastest_route = min(recommended_routes, key=lambda x: (x[3], x[6]))
            while True:
                current_time = datetime.now()
                time_diff = datetime.strptime(fastest_route[1], "%H:%M") - current_time
                time_placeholder.write(f"현재 시간: {current_time.strftime('%H:%M:%S')}")
                if len(fastest_route) == 4:
                    next_bus_placeholder.markdown(
                        f"<span style='color: {fastest_route[2]};'>"
                        f"가장 빠른 버스: 노선 {fastest_route[0]}<br>"
                        f"다음 출발 시간: {fastest_route[1]}<br>"
                        f"남은 시간: {time_diff.seconds // 60}분 {time_diff.seconds % 60}초</span>",
                        unsafe_allow_html=True
                    )
                else:
                    next_bus_placeholder.markdown(
                        f"<span style='color: {fastest_route[2]};'>"
                        f"환승 필요: 노선 {fastest_route[0]} -> {fastest_route[5]}<br>"
                        f"환승지: {fastest_route[4]}<br>"
                        f"다음 출발 시간: {fastest_route[1]}<br>"
                        f"남은 시간: {time_diff.seconds // 60}분 {time_diff.seconds % 60}초</span>",
                        unsafe_allow_html=True
                    )
                tm.sleep(1)
        else:
            st.warning("선택한 출발지와 도착지를 포함하는 셔틀노선이 없습니다.")

# 경계선 추가
st.markdown("<hr style='border: 2px solid blue;'>", unsafe_allow_html=True)