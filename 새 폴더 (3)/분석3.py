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
    print("Malgun Gothic 폰트가 시스템에 설치되어 있지 않습니다. 다른 폰트를 지정해주세요.")

# ----------------------------------------------------------------------
# 1. 데이터 불러오기 및 전처리
# ----------------------------------------------------------------------
file_path = '도로평균속도.csv'

try:
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=6)

    column_rename_dict = {
        'Unnamed: 0': 'LINK ID',
        'Unnamed: 2': '도로등급',
        'Unnamed: 3': '도로명',
        'Unnamed: 4': '권역',
        'Unnamed: 5': '연장(km)',
        'Unnamed: 6': '차선수'
    }
    df.rename(columns=column_rename_dict, inplace=True)

    speed_columns = [f'{i}~{i + 1}시' for i in range(24)]
    info_columns = ['LINK ID', '도로명', '도로등급', '권역', '연장(km)', '차선수']

    df_analysis = df[info_columns + speed_columns].copy()

    for col in speed_columns:
        df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')

    df_analysis.dropna(subset=speed_columns, inplace=True)

except Exception as e:
    print(f"데이터 처리 중 오류 발생: {e}")
    exit()

# ----------------------------------------------------------------------
# 2. 도로별 혼잡도 지수 계산
# ----------------------------------------------------------------------
df_analysis['max_speed'] = df_analysis[speed_columns].max(axis=1)
df_analysis['avg_speed'] = df_analysis[speed_columns].mean(axis=1)
df_analysis = df_analysis[df_analysis['max_speed'] > 10]

congestion_cols = []
for i, col in enumerate(speed_columns):
    congestion_col_name = f'congestion_{i}'
    df_analysis[congestion_col_name] = (df_analysis['max_speed'] - df_analysis[col]) / df_analysis['max_speed']
    congestion_cols.append(congestion_col_name)

df_analysis['avg_congestion'] = df_analysis[congestion_cols].mean(axis=1)

print("✅ 데이터 불러오기 및 혼잡도 계산 완료")

# ----------------------------------------------------------------------
# 3. LINK ID별 평균 혼잡도 분석 (상위 10개 선별)
# ----------------------------------------------------------------------
link_congestion = df_analysis.groupby('LINK ID')['avg_congestion'].mean().sort_values(ascending=False)
top_10_congested_links = link_congestion.head(10)
top_10_ids = top_10_congested_links.index.tolist()

print("\n-=-=-= 상위 10개 상습 정체 LINK ID -=-=-=")
print(top_10_congested_links)
print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

# ----------------------------------------------------------------------
# 4. ⭐️ 요청하신 기능: 상위 10개 링크의 시간대별 혼잡도 시각화
# ----------------------------------------------------------------------
# 분석할 상위 10개 링크의 데이터만 필터링
df_top10 = df_analysis[df_analysis['LINK ID'].isin(top_10_ids)].copy()

# 시각화를 위해 LINK ID를 인덱스로 설정
df_top10.set_index('LINK ID', inplace=True)

# 시간대별 혼잡도 데이터만 추출 (congestion_0, congestion_1, ...)
df_top10_congestion_hourly = df_top10[congestion_cols]
# 컬럼명을 알아보기 쉽게 '0~1시', '1~2시' 등으로 변경
df_top10_congestion_hourly.columns = speed_columns

# 그래프 그리기
plt.figure(figsize=(18, 9))
for link_id in df_top10_congestion_hourly.index:
    plt.plot(df_top10_congestion_hourly.columns, df_top10_congestion_hourly.loc[link_id], marker='o', markersize=4,
             linestyle='-', label=f'LINK ID: {link_id}')

plt.title('상위 10개 혼잡 링크의 시간대별 혼잡도 추이', fontsize=18)
plt.xlabel('시간대', fontsize=12)
plt.ylabel('혼잡도 지수', fontsize=12)
plt.xticks(rotation=45)
plt.yticks([i / 10 for i in range(11)])  # Y축 눈금을 0.1 단위로 설정
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='LINK ID', bbox_to_anchor=(1.02, 1), loc='upper left')  # 범례를 그래프 바깥에 표시
plt.tight_layout()
plt.savefig('top10_links_hourly_congestion.png')
print("\n✅ 상위 10개 링크 시간대별 혼잡도 그래프 'top10_links_hourly_congestion.png' 저장 완료")