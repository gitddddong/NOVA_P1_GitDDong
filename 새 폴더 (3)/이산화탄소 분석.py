import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ----------------------------------------------------------------------
# 윈도우 환경에서 Matplotlib 한글 폰트 설정
# ----------------------------------------------------------------------
try:
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("Malgun Gothic 폰트가 시스템에 설치되어 있지 않습니다.")

try:
    # ----------------------------------------------------------------------
    # 1. 최종 CO₂ 배출량 데이터 불러오기
    # ----------------------------------------------------------------------
    file_path = 'final_hourly_co2_emissions.csv'
    df = pd.read_csv(file_path)
    print("✅ 1. 최종 CO₂ 배출량 데이터 불러오기 완료")

    # ----------------------------------------------------------------------
    # 2. 전체적인 시간대별 CO₂ 배출 패턴 분석 및 시각화
    # ----------------------------------------------------------------------
    hourly_cols = [f'Final_CO2_Hour_{i}' for i in range(24)]
    avg_hourly_co2 = df[hourly_cols].mean()

    plt.figure(figsize=(15, 7))
    avg_hourly_co2.index = [f'{i}~{i + 1}시' for i in range(24)]
    avg_hourly_co2.plot(kind='line', marker='o', color='green')
    plt.title('전체 도로의 시간대별 평균 CO₂ 배출량', fontsize=16)
    plt.xlabel('시간대', fontsize=12)
    plt.ylabel('평균 CO₂ 배출량', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    print("✅ 2. 전체 시간대별 CO₂ 배출 패턴 그래프 표시 완료")

    # ----------------------------------------------------------------------
    # 3. TOP 10 CO₂ 배출 구간 선별 및 시각화
    # ----------------------------------------------------------------------
    df['avg_daily_co2'] = df[hourly_cols].mean(axis=1)
    top_10_links = df.sort_values(by='avg_daily_co2', ascending=False).head(10)

    print("\n-=-=-= 하루 평균 CO₂ 배출량 TOP 10 -=-=-=")
    print(top_10_links[['LINK ID', 'avg_daily_co2']])
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

    plt.figure(figsize=(12, 8))
    top_10_links_sorted = top_10_links.sort_values(by='avg_daily_co2', ascending=True)
    plt.barh(top_10_links_sorted['LINK ID'].astype(str), top_10_links_sorted['avg_daily_co2'], color='olive')
    plt.title('하루 평균 CO₂ 배출량 TOP 10 도로 링크', fontsize=16)
    plt.xlabel('평균 CO₂ 배출량', fontsize=12)
    plt.ylabel('LINK ID', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6, axis='x')
    plt.tight_layout()
    plt.show()

    print("✅ 3. TOP 10 CO₂ 배출 구간 그래프 표시 완료")

    # ----------------------------------------------------------------------
    # 4. 상습 배출 구간 패턴 심층 분석 및 시각화
    # ----------------------------------------------------------------------
    df_top10_hourly = top_10_links.set_index('LINK ID')[hourly_cols]
    df_top10_hourly.columns = [f'{i}~{i + 1}시' for i in range(24)]

    plt.figure(figsize=(18, 9))
    for link_id in df_top10_hourly.index:
        plt.plot(df_top10_hourly.columns, df_top10_hourly.loc[link_id], marker='o', markersize=4, linestyle='-',
                 label=f'LINK ID: {link_id}')

    plt.title('TOP 10 CO₂ 배출 링크의 시간대별 배출량 추이', fontsize=18)
    plt.xlabel('시간대', fontsize=12)
    plt.ylabel('CO₂ 배출량', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='LINK ID', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    print("✅ 4. TOP 10 CO₂ 배출 구간 패턴 심층 분석 그래프 표시 완료")

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    print("이 스크립트와 final_hourly_co2_emissions.csv 파일이 같은 폴더에 있는지 다시 확인해주세요.")
except Exception as e:
    print(f"처리 중 오류 발생: {e}")