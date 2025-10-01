import pandas as pd
import numpy as np

try:
    # ----------------------------------------------------------------------
    # 1. 데이터 불러오기 및 전처리
    # ----------------------------------------------------------------------
    file_path = 'volume.csv'
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=8, header=None)

    # 필요한 모든 컬럼 선택: ID(0), 등급(2), 도로명(3), 길이(5), 차선(6), 시간별 교통량(8~31)
    info_cols_indices = [0, 2, 3, 5, 6]
    hourly_volume_cols_indices = list(range(8, 32))
    df_analysis = df[info_cols_indices + hourly_volume_cols_indices].copy()

    # 컬럼명 설정
    info_col_names = ['LINK ID', '도로등급', '도로명', '연장(km)', '차선수']
    hourly_volume_col_names = [f'volume_{i}' for i in range(24)]
    df_analysis.columns = info_col_names + hourly_volume_col_names

    # 데이터 타입 변환 및 정리
    for col in df_analysis.columns:
        if col not in ['도로등급', '도로명']:
            df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')
    df_analysis.dropna(inplace=True)
    df_analysis['LINK ID'] = df_analysis['LINK ID'].astype(int)

    print("✅ 1. 데이터 불러오기 및 전처리 완료")

    # ----------------------------------------------------------------------
    # 2. '최종 실질적 수용 능력' 계산
    # ----------------------------------------------------------------------
    volume_cols = [f'volume_{i}' for i in range(24)]

    # 1) 통계적 기준용량 (95th percentile) 계산
    # 각 행(LINK ID)에 대해 24시간 교통량의 95% 백분위수를 계산합니다.
    df_analysis['Stat_Capacity'] = df_analysis[volume_cols].quantile(q=0.95, axis=1)

    # 2) 가중치 계산
    # W_length: 도로 길이 가중치
    avg_length = df_analysis['연장(km)'].mean()
    df_analysis['W_length'] = df_analysis['연장(km)'] / avg_length

    # W_lanes: 도로명 그룹별 차선 가중치 (수정된 방식 적용)
    # 각 도로명 그룹 내의 평균 차선 수를 계산
    avg_lanes_by_road = df_analysis.groupby('도로명')['차선수'].transform('mean')
    df_analysis['W_lanes'] = df_analysis['차선수'] / avg_lanes_by_road

    # W_class: 도로 등급 가중치
    class_weights = {'고속도로': 1.5, '도시고속도로': 1.5, '일반국도': 1.2, '특별광역시도': 1.2, '국가지원지방도': 1.0, '지방도': 1.0, '시군도': 1.0,
                     '연결로': 1.0}
    df_analysis['W_class'] = df_analysis['도로등급'].map(class_weights).fillna(1.0)

    # 3) 최종 실질적 수용 능력 계산
    df_analysis['Final_Capacity'] = df_analysis['Stat_Capacity'] * df_analysis['W_length'] * df_analysis['W_lanes'] * \
                                    df_analysis['W_class']

    # 수용 능력이 0이 되는 경우를 방지 (분모가 0이 되면 안됨)
    df_analysis['Final_Capacity'] = df_analysis['Final_Capacity'].replace(0, np.nan)
    df_analysis.dropna(subset=['Final_Capacity'], inplace=True)

    print("✅ 2. '최종 실질적 수용 능력' 계산 완료")

    # ----------------------------------------------------------------------
    # 3. 시간당 최종 혼잡도 계산 및 파일 저장
    # ----------------------------------------------------------------------
    final_congestion_cols = []
    for i in range(24):
        final_col_name = f'Final_Congestion_Hour_{i}'
        df_analysis[final_col_name] = df_analysis[f'volume_{i}'] / df_analysis['Final_Capacity']
        final_congestion_cols.append(final_col_name)

    # 최종 결과 CSV 파일로 저장
    df_final_result = df_analysis[['LINK ID'] + final_congestion_cols]
    output_filename = 'final_hourly_congestion_score.csv'
    df_final_result.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print("✅ 3. 시간당 최종 혼잡도 계산 완료")
    print(f"✅ 전체 결과가 '{output_filename}' 파일로 저장되었습니다.")
    print("\n[계산된 시간당 최종 혼잡도 데이터 샘플]")
    print(df_final_result.head())

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    print("이 스크립트와 volume.csv 파일이 같은 폴더에 있는지 다시 확인해주세요.")
except Exception as e:
    print(f"데이터 처리 중 오류 발생: {e}")