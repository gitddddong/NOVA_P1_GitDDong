import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ======================================================================
# 0. 초기 설정: 한글 폰트 및 마이너스 기호
# ======================================================================
try:
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("Malgun Gothic 폰트가 시스템에 설치되어 있지 않습니다.")

print(">>> 분석을 시작합니다.")

try:
    # ======================================================================
    # 1. 최종 혼잡도 계산 및 파일 저장
    # ======================================================================
    print("\n>>> [단계 1/4] '최종 혼잡도'를 계산합니다...")

    # --- 데이터 불러오기 ---
    df_vol = pd.read_csv('volume.csv', encoding='utf-8', skiprows=8, header=None)
    df_bus_truck = pd.read_csv('BUSVolume(LINK).csv', encoding='utf-8', skiprows=8, header=None)

    # --- 데이터 전처리 및 결합 ---
    info_cols_indices = [0, 2, 3, 5, 6]
    hourly_volume_cols_indices = list(range(8, 32))
    df_analysis_cong = df_vol[info_cols_indices + hourly_volume_cols_indices].copy()
    info_col_names = ['LINK ID', '도로등급', '도로명', '연장(km)', '차선수']
    hourly_volume_col_names = [f'volume_{i}' for i in range(24)]
    df_analysis_cong.columns = info_col_names + hourly_volume_col_names

    df_heavy_vol = df_bus_truck[[0, 7, 32]].copy()
    df_heavy_vol.columns = ['LINK ID', 'Bus_Volume', 'Truck_Volume']
    df_analysis_cong = pd.merge(df_analysis_cong, df_heavy_vol, on='LINK ID')

    for col in df_analysis_cong.columns:
        if col not in ['도로등급', '도로명']:
            df_analysis_cong[col] = pd.to_numeric(df_analysis_cong[col], errors='coerce')
    df_analysis_cong.dropna(inplace=True)
    df_analysis_cong['LINK ID'] = df_analysis_cong['LINK ID'].astype(int)

    # --- 최종 실질적 수용 능력 계산 ---
    volume_cols = [f'volume_{i}' for i in range(24)]
    df_analysis_cong['Total_Volume'] = df_analysis_cong[volume_cols].sum(axis=1)
    df_analysis_cong['Stat_Capacity'] = df_analysis_cong[volume_cols].quantile(q=0.95, axis=1)
    avg_length = df_analysis_cong['연장(km)'].mean()
    df_analysis_cong['W_length'] = df_analysis_cong['연장(km)'] / avg_length
    avg_lanes_by_road = df_analysis_cong.groupby('도로명')['차선수'].transform('mean')
    df_analysis_cong['W_lanes'] = df_analysis_cong['차선수'] / avg_lanes_by_road
    class_weights = {'고속도로': 1.5, '도시고속도로': 1.5, '일반국도': 1.2, '특별광역시도': 1.2, '국가지원지방도': 1.0, '지방도': 1.0, '시군도': 1.0,
                     '연결로': 1.0}
    df_analysis_cong['W_class'] = df_analysis_cong['도로등급'].map(class_weights).fillna(1.0)
    PCE = 2.0
    df_analysis_cong['P_heavy'] = (df_analysis_cong['Bus_Volume'] + df_analysis_cong['Truck_Volume']) / \
                                  df_analysis_cong['Total_Volume']
    df_analysis_cong['W_heavy'] = 1 / (1 + df_analysis_cong['P_heavy'] * (PCE - 1))
    df_analysis_cong.fillna({'W_heavy': 1.0}, inplace=True)
    df_analysis_cong['Final_Capacity'] = df_analysis_cong['Stat_Capacity'] * df_analysis_cong['W_length'] * \
                                         df_analysis_cong['W_lanes'] * df_analysis_cong['W_class'] * df_analysis_cong[
                                             'W_heavy']
    df_analysis_cong['Final_Capacity'] = df_analysis_cong['Final_Capacity'].replace(0, np.nan)
    df_analysis_cong.dropna(subset=['Final_Capacity'], inplace=True)

    # --- 시간당 최종 혼잡도 계산 및 파일 저장 ---
    final_congestion_cols = []
    for i in range(24):
        final_col_name = f'Final_Congestion_Hour_{i}'
        df_analysis_cong[final_col_name] = df_analysis_cong[f'volume_{i}'] / df_analysis_cong['Final_Capacity']
        final_congestion_cols.append(final_col_name)

    df_cong_result = df_analysis_cong[['LINK ID'] + final_congestion_cols]
    df_cong_result.to_csv('ultimate_final_hourly_congestion.csv', index=False, encoding='utf-8-sig')
    print("✅ 'ultimate_final_hourly_congestion.csv' 파일 저장 완료")

    # ======================================================================
    # 2. 최종 CO₂ 배출량 계산 및 파일 저장
    # ======================================================================
    print("\n>>> [단계 2/4] '최종 CO₂ 배출량'을 계산합니다...")

    # --- 데이터 불러오기 ---
    df_co2_raw = pd.read_csv('CongestIndex(LINK).csv', encoding='utf-8', skiprows=8, header=None)

    # --- 차종별 데이터 추출 및 결합 ---
    car_cols = [0, 32] + list(range(33, 57));
    df_car = df_vol[car_cols].copy();
    df_car.columns = ['LINK ID', 'Total_Volume_Car'] + [f'Volume_Car_{i}' for i in range(24)]
    bus_cols = [0, 7] + list(range(8, 32));
    df_bus = df_bus_truck[bus_cols].copy();
    df_bus.columns = ['LINK ID', 'Total_Volume_Bus'] + [f'Volume_Bus_{i}' for i in range(24)]
    truck_cols = [0, 32] + list(range(33, 57));
    df_truck = df_bus_truck[truck_cols].copy();
    df_truck.columns = ['LINK ID', 'Total_Volume_Truck'] + [f'Volume_Truck_{i}' for i in range(24)]
    df_co2_daily = df_co2_raw[[0, 8, 9, 10]].copy();
    df_co2_daily.columns = ['LINK ID', 'Total_CO2_Car', 'Total_CO2_Bus', 'Total_CO2_Truck']

    df_merged_co2 = pd.merge(df_car, df_bus, on='LINK ID');
    df_merged_co2 = pd.merge(df_merged_co2, df_truck, on='LINK ID');
    df_merged_co2 = pd.merge(df_merged_co2, df_co2_daily, on='LINK ID')
    for col in df_merged_co2.columns:
        if col != 'LINK ID': df_merged_co2[col] = pd.to_numeric(df_merged_co2[col], errors='coerce')
    df_merged_co2.dropna(inplace=True);
    df_merged_co2['LINK ID'] = df_merged_co2['LINK ID'].astype(int)

    # --- 시간당 CO₂ 배출량 계산 및 파일 저장 ---
    final_hourly_co2_cols = []
    df_merged_co2 = df_merged_co2[df_merged_co2['Total_Volume_Car'] > 0];
    df_merged_co2 = df_merged_co2[df_merged_co2['Total_Volume_Bus'] > 0];
    df_merged_co2 = df_merged_co2[df_merged_co2['Total_Volume_Truck'] > 0]
    for i in range(24):
        co2_car_hour = (df_merged_co2['Total_CO2_Car'] / df_merged_co2['Total_Volume_Car']) * df_merged_co2[
            f'Volume_Car_{i}']
        co2_bus_hour = (df_merged_co2['Total_CO2_Bus'] / df_merged_co2['Total_Volume_Bus']) * df_merged_co2[
            f'Volume_Bus_{i}']
        co2_truck_hour = (df_merged_co2['Total_CO2_Truck'] / df_merged_co2['Total_Volume_Truck']) * df_merged_co2[
            f'Volume_Truck_{i}']
        final_col_name = f'Final_CO2_Hour_{i}'
        df_merged_co2[final_col_name] = co2_car_hour + co2_bus_hour + co2_truck_hour
        final_hourly_co2_cols.append(final_col_name)

    df_co2_result = df_merged_co2[['LINK ID'] + final_hourly_co2_cols]
    df_co2_result.to_csv('final_hourly_co2_emissions.csv', index=False, encoding='utf-8-sig')
    print("✅ 'final_hourly_co2_emissions.csv' 파일 저장 완료")

    # ======================================================================
    # 3. 분석 및 시각화
    # ======================================================================
    print("\n>>> [단계 3/4] 시각화 및 분석을 시작합니다...")

    # --- 혼잡도 분석 및 시각화 ---
    print("\n--- 최종 혼잡도 분석 ---")
    avg_hourly_congestion = df_cong_result[final_congestion_cols].mean()
    plt.figure(figsize=(15, 7));
    avg_hourly_congestion.index = [f'{i}~{i + 1}시' for i in range(24)];
    avg_hourly_congestion.plot(kind='line', marker='o', color='purple')
    plt.title('전체 도로의 시간대별 평균 최종 혼잡도');
    plt.xlabel('시간대');
    plt.ylabel('평균 최종 혼잡도 점수');
    plt.axhline(y=1.0, color='red', linestyle='--', label='혼잡 임계점 (1.0)');
    plt.xticks(rotation=45);
    plt.grid(True, alpha=0.6);
    plt.legend();
    plt.tight_layout();
    plt.show()

    df_cong_result['avg_daily_congestion'] = df_cong_result[final_congestion_cols].mean(axis=1)
    top_10_cong_links = df_cong_result.sort_values(by='avg_daily_congestion', ascending=False).head(10)
    print("\n[하루 평균 최종 혼잡도 TOP 10]\n", top_10_cong_links[['LINK ID', 'avg_daily_congestion']])
    plt.figure(figsize=(12, 8));
    top_10_cong_links_sorted = top_10_cong_links.sort_values(by='avg_daily_congestion', ascending=True);
    plt.barh(top_10_cong_links_sorted['LINK ID'].astype(str), top_10_cong_links_sorted['avg_daily_congestion'],
             color='tomato')
    plt.title('하루 평균 최종 혼잡도 TOP 10 도로 링크');
    plt.xlabel('평균 최종 혼잡도 점수');
    plt.ylabel('LINK ID');
    plt.grid(True, axis='x', alpha=0.6);
    plt.tight_layout();
    plt.show()

    # --- CO₂ 배출량 분석 및 시각화 ---
    print("\n--- 최종 CO₂ 배출량 분석 ---")
    avg_hourly_co2 = df_co2_result[final_hourly_co2_cols].mean()
    plt.figure(figsize=(15, 7));
    avg_hourly_co2.index = [f'{i}~{i + 1}시' for i in range(24)];
    avg_hourly_co2.plot(kind='line', marker='o', color='green')
    plt.title('전체 도로의 시간대별 평균 CO₂ 배출량');
    plt.xlabel('시간대');
    plt.ylabel('평균 CO₂ 배출량');
    plt.xticks(rotation=45);
    plt.grid(True, alpha=0.6);
    plt.tight_layout();
    plt.show()

    df_co2_result['avg_daily_co2'] = df_co2_result[final_hourly_co2_cols].mean(axis=1)
    top_10_co2_links = df_co2_result.sort_values(by='avg_daily_co2', ascending=False).head(10)
    print("\n[하루 평균 CO₂ 배출량 TOP 10]\n", top_10_co2_links[['LINK ID', 'avg_daily_co2']])
    plt.figure(figsize=(12, 8));
    top_10_co2_links_sorted = top_10_co2_links.sort_values(by='avg_daily_co2', ascending=True);
    plt.barh(top_10_co2_links_sorted['LINK ID'].astype(str), top_10_co2_links_sorted['avg_daily_co2'], color='olive')
    plt.title('하루 평균 CO₂ 배출량 TOP 10 도로 링크');
    plt.xlabel('평균 CO₂ 배출량');
    plt.ylabel('LINK ID');
    plt.grid(True, axis='x', alpha=0.6);
    plt.tight_layout();
    plt.show()

    # ======================================================================
    # 4. 사분면 분석 (최종 연관 분석)
    # ======================================================================
    print("\n>>> [단계 4/4] '사분면 분석'으로 두 지표를 연관 분석합니다...")

    df_quadrant = pd.merge(df_cong_result[['LINK ID', 'avg_daily_congestion']],
                           df_co2_result[['LINK ID', 'avg_daily_co2']], on='LINK ID')
    congestion_threshold = df_quadrant['avg_daily_congestion'].mean()
    co2_threshold = df_quadrant['avg_daily_co2'].mean()


    def classify_quadrant(row):
        is_high_congestion = row['avg_daily_congestion'] > congestion_threshold
        is_high_co2 = row['avg_daily_co2'] > co2_threshold
        if is_high_congestion and is_high_co2:
            return '1사분면: 최악의 구간'
        elif is_high_congestion and not is_high_co2:
            return '2사분면: 숨은 병목 구간'
        elif not is_high_congestion and is_high_co2:
            return '3사분면: 효율적인 간선도로'
        else:
            return '4사분면: 양호한 구간'


    df_quadrant['quadrant'] = df_quadrant.apply(classify_quadrant, axis=1)

    print("\n[사분면별 도로 개수]\n", df_quadrant['quadrant'].value_counts())
    df_quadrant.to_csv('quadrant_analysis.csv', index=False, encoding='utf-8-sig')
    print("✅ 'quadrant_analysis.csv' 파일 저장 완료")

    plt.figure(figsize=(14, 10))
    colors = {'1사분면: 최악의 구간': 'red', '2사분면: 숨은 병목 구간': 'orange', '3사분면: 효율적인 간선도로': 'skyblue',
              '4사분면: 양호한 구간': 'limegreen'}
    for quadrant, color in colors.items():
        subset = df_quadrant[df_quadrant['quadrant'] == quadrant]
        plt.scatter(subset['avg_daily_congestion'], subset['avg_daily_co2'], c=color, label=quadrant, alpha=0.6, s=50)

    plt.axvline(x=congestion_threshold, color='grey', linestyle='--', linewidth=1);
    plt.axhline(y=co2_threshold, color='grey', linestyle='--', linewidth=1)
    plt.title('도로 유형 분류를 위한 사분면 분석');
    plt.xlabel('평균 최종 혼잡도 점수 (← 낮음 | 높음 →)');
    plt.ylabel('평균 CO₂ 배출량 (← 적음 | 많음 →)')
    plt.xscale('log');
    plt.yscale('log')
    plt.legend(title='도로 유형');
    plt.grid(True, which="both", ls="--", linewidth=0.5);
    plt.tight_layout();
    plt.show()

    print("\n>>> 모든 분석이 완료되었습니다.")

except FileNotFoundError as e:
    print(f"\n오류: 파일을 찾을 수 없습니다. '{e.filename}' 파일이 스크립트와 같은 폴더에 있는지 확인해주세요.")
    print("volume.csv, BUSVolume(LINK).csv, CongestIndex(LINK).csv 3개 파일이 모두 필요합니다.")
except Exception as e:
    print(f"\n처리 중 오류 발생: {e}")