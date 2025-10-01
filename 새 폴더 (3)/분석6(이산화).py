import pandas as pd
import numpy as np

try:
    # ----------------------------------------------------------------------
    # 1. 데이터 불러오기 (3개 파일)
    # ----------------------------------------------------------------------
    # 전체 및 승용차 교통량 데이터
    df_volume_all = pd.read_csv('volume.csv', encoding='utf-8', skiprows=8, header=None)
    # 버스 및 트럭 교통량 데이터
    df_volume_heavy = pd.read_csv('BUSVolume(LINK).csv', encoding='utf-8', skiprows=8, header=None)
    # 차종별 CO2 데이터
    df_co2 = pd.read_csv('CongestIndex(LINK).csv', encoding='utf-8', skiprows=8, header=None)

    print("✅ 1. 모든 데이터 파일 불러오기 완료")

    # ----------------------------------------------------------------------
    # 2. 차종별 데이터 추출 및 정리
    # ----------------------------------------------------------------------
    # --- 승용차 데이터 ---
    car_cols = [0, 32] + list(range(33, 57))  # LINK ID, 승용차-전일, 승용차-시간별
    df_car = df_volume_all[car_cols].copy()
    df_car.columns = ['LINK ID', 'Total_Volume_Car'] + [f'Volume_Car_{i}' for i in range(24)]

    # --- 버스 데이터 ---
    bus_cols = [0, 7] + list(range(8, 32))  # LINK ID, 버스-전일, 버스-시간별
    df_bus = df_volume_heavy[bus_cols].copy()
    df_bus.columns = ['LINK ID', 'Total_Volume_Bus'] + [f'Volume_Bus_{i}' for i in range(24)]

    # --- 트럭 데이터 ---
    truck_cols = [0, 32] + list(range(33, 57))  # LINK ID, 트럭-전일, 트럭-시간별
    df_truck = df_volume_heavy[truck_cols].copy()
    df_truck.columns = ['LINK ID', 'Total_Volume_Truck'] + [f'Volume_Truck_{i}' for i in range(24)]

    # --- CO2 데이터 ---
    df_co2_daily = df_co2[[0, 8, 9, 10]].copy()  # LINK ID, CO2-승용차, CO2-버스, CO2-트럭
    df_co2_daily.columns = ['LINK ID', 'Total_CO2_Car', 'Total_CO2_Bus', 'Total_CO2_Truck']

    # --- 데이터 병합 ---
    df_merged = pd.merge(df_car, df_bus, on='LINK ID')
    df_merged = pd.merge(df_merged, df_truck, on='LINK ID')
    df_merged = pd.merge(df_merged, df_co2_daily, on='LINK ID')

    # 데이터 타입 변환
    for col in df_merged.columns:
        if col != 'LINK ID':
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
    df_merged.dropna(inplace=True)
    df_merged['LINK ID'] = df_merged['LINK ID'].astype(int)

    print("✅ 2. 차종별 데이터 추출 및 결합 완료")

    # ----------------------------------------------------------------------
    # 3. 차종별 시간당 CO₂ 배출량 계산 후 합산
    # ----------------------------------------------------------------------
    final_hourly_co2_cols = []
    for i in range(24):
        # 0으로 나누는 오류 방지
        df_merged = df_merged[df_merged['Total_Volume_Car'] > 0]
        df_merged = df_merged[df_merged['Total_Volume_Bus'] > 0]
        df_merged = df_merged[df_merged['Total_Volume_Truck'] > 0]

        # 차종별 시간당 CO2 계산
        co2_car_hour = (df_merged['Total_CO2_Car'] / df_merged['Total_Volume_Car']) * df_merged[f'Volume_Car_{i}']
        co2_bus_hour = (df_merged['Total_CO2_Bus'] / df_merged['Total_Volume_Bus']) * df_merged[f'Volume_Bus_{i}']
        co2_truck_hour = (df_merged['Total_CO2_Truck'] / df_merged['Total_Volume_Truck']) * df_merged[
            f'Volume_Truck_{i}']

        # 시간당 총 CO2 배출량 (차종별 합산)
        final_col_name = f'Final_CO2_Hour_{i}'
        df_merged[final_col_name] = co2_car_hour + co2_bus_hour + co2_truck_hour
        final_hourly_co2_cols.append(final_col_name)

    print("✅ 3. 시간당 최종 CO₂ 배출량 계산 완료")

    # ----------------------------------------------------------------------
    # 4. 최종 결과 저장
    # ----------------------------------------------------------------------
    df_final_result = df_merged[['LINK ID'] + final_hourly_co2_cols]
    output_filename = 'final_hourly_co2_emissions.csv'
    df_final_result.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"✅ 전체 결과가 '{output_filename}' 파일로 저장되었습니다.")
    print("\n[계산된 시간당 최종 CO₂ 배출량 데이터 샘플]")
    print(df_final_result.head())

except FileNotFoundError as e:
    print(f"오류: 파일을 찾을 수 없습니다. '{e.filename}' 파일이 스크립트와 같은 폴더에 있는지 확인해주세요.")
    print("volume.csv, BUSVolume(LINK).csv, CongestIndex(LINK).csv 파일이 모두 필요합니다.")
except Exception as e:
    print(f"데이터 처리 중 오류 발생: {e}")