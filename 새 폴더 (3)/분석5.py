import pandas as pd

# ----------------------------------------------------------------------
# 1. 데이터 불러오기 및 전처리
# ----------------------------------------------------------------------
# ✅ volume.csv 파일이 이 파이썬 스크립트와 같은 폴더에 있는지 확인해주세요.
file_path = 'volume.csv'

try:
    # 8줄을 건너뛰고 헤더 없이 데이터를 불러옵니다.
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=8, header=None)

    # 필요한 컬럼만 선택: LINK ID (0번) 및 전체-평일의 24시간 교통량 (8번 ~ 31번)
    hourly_volume_cols = list(range(8, 32))
    df_analysis = df[[0] + hourly_volume_cols].copy()

    # 컬럼명 설정
    col_names = ['LINK ID'] + [f'volume_{i}' for i in range(24)]
    df_analysis.columns = col_names

    # 데이터 타입 변환 및 정리
    for col in df_analysis.columns:
        df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')
    df_analysis.dropna(inplace=True)
    df_analysis['LINK ID'] = df_analysis['LINK ID'].astype(int)

    print("✅ 데이터 불러오기 및 전처리 완료")

    # 2. 혼잡도 계산
    volume_cols = [f'volume_{i}' for i in range(24)]

    # 각 링크(행)의 하루 중 최대 교통량 계산
    df_analysis['max_volume'] = df_analysis[volume_cols].max(axis=1)

    # 0으로 나누는 것을 방지하기 위해 최대 교통량이 0인 링크는 제외
    df_analysis = df_analysis[df_analysis['max_volume'] > 0].copy()

    # 시간당 혼잡 지수 계산
    congestion_cols = []
    for i in range(24):
        congestion_col_name = f'congestion_{i}'
        df_analysis[congestion_col_name] = df_analysis[f'volume_{i}'] / df_analysis['max_volume']
        congestion_cols.append(congestion_col_name)

    # 일일 평균 혼잡도 계산
    df_analysis['avg_congestion_score'] = df_analysis[congestion_cols].mean(axis=1)
    print("✅ 일일 평균 혼잡도 계산 완료")

    # 3. 결과 정리 및 출력
    # 최종 결과 데이터프레임 생성
    df_result = df_analysis[['LINK ID', 'avg_congestion_score', 'max_volume']].copy()
    df_result['total_volume'] = df_analysis[volume_cols].sum(axis=1)  # 참고용 일일 총 교통량 추가

    # 혼잡도 점수가 높은 순으로 정렬
    df_result_sorted = df_result.sort_values(by='avg_congestion_score', ascending=False)

    # 결과 파일 저장
    output_filename = 'link_congestion_score.csv'
    df_result_sorted.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"✅ 전체 결과가 '{output_filename}' 파일로 저장되었습니다.")
    print("\n-=-=-= 일일 평균 혼잡도 상위 10개 링크 -=-=-=")
    print(df_result_sorted.head(10))
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    print("이 스크립트와 volume.csv 파일이 같은 폴더에 있는지 다시 확인해주세요.")
except Exception as e:
    print(f"데이터 처리 중 오류 발생: {e}")