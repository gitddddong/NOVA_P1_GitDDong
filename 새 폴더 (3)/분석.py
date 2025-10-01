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
    # ⭐️⭐️⭐️ 오류 수정: 새 파일 구조에 맞게 건너뛸 줄 수를 7에서 6으로 변경했습니다. ⭐️⭐️⭐️
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=6)

    # 잘못 지정된 컬럼명을 올바른 이름으로 직접 변경합니다.
    column_rename_dict = {
        'Unnamed: 2': '도로등급',
        'Unnamed: 3': '도로명',
        'Unnamed: 4': '권역',
        'Unnamed: 5': '연장(km)',
        'Unnamed: 6': '차선수'
    }
    df.rename(columns=column_rename_dict, inplace=True)

    speed_columns = [f'{i}~{i + 1}시' for i in range(24)]
    info_columns = ['도로명', '도로등급', '권역', '연장(km)', '차선수']

    df_analysis = df[info_columns + speed_columns].copy()

    for col in speed_columns:
        df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')

    df_analysis.dropna(subset=speed_columns, inplace=True)

    print("✅ 데이터 불러오기 및 전처리 완료")
    print(df_analysis.head())

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"데이터 처리 중 오류 발생: {e}")
    exit()

# ----------------------------------------------------------------------
# 2. 도로별 혼잡도 지수 계산 (이후 코드는 변경 없음)
# ----------------------------------------------------------------------
df_analysis['max_speed'] = df_analysis[speed_columns].max(axis=1)
df_analysis['avg_speed'] = df_analysis[speed_columns].mean(axis=1)

df_analysis = df_analysis[df_analysis['max_speed'] > 10]

for i, col in enumerate(speed_columns):
    df_analysis[f'congestion_{i}'] = (df_analysis['max_speed'] - df_analysis[col]) / df_analysis['max_speed']

congestion_cols = [f'congestion_{i}' for i in range(24)]
df_analysis['avg_congestion'] = df_analysis[congestion_cols].mean(axis=1)

print("\n✅ 혼잡도 지수 계산 완료")
print(df_analysis[['도로명', 'max_speed', 'avg_speed', 'avg_congestion']].head())

# ----------------------------------------------------------------------
# 3. 시간대별 평균 혼잡도 분석 및 시각화
# ----------------------------------------------------------------------
hourly_congestion = [df_analysis[f'congestion_{i}'].mean() for i in range(24)]

plt.figure(figsize=(15, 7))
plt.plot(speed_columns, hourly_congestion, marker='o', linestyle='-')
plt.title('시간대별 평균 혼잡도 지수', fontsize=16)
plt.xlabel('시간대', fontsize=12)
plt.ylabel('평균 혼잡도 지수', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('hourly_congestion.png')
print("\n✅ 시간대별 혼잡도 분석 그래프 'hourly_congestion.png' 저장 완료")

# ----------------------------------------------------------------------
# 4. 도로별 평균 혼잡도 분석 및 시각화 (상위 10개)
# ----------------------------------------------------------------------
road_congestion = df_analysis.groupby('도로명')['avg_congestion'].mean().sort_values(ascending=False)
top_10_congested_roads = road_congestion.head(10)

print("\n-=-=-= 상위 10개 상습 정체 도로 -=-=-=")
print(top_10_congested_roads)
print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

plt.figure(figsize=(12, 8))
top_10_congested_roads.sort_values(ascending=True).plot(kind='barh', color='tomato')
plt.title('평균 혼잡도가 가장 높은 상위 10개 도로', fontsize=16)
plt.xlabel('평균 혼잡도 지수', fontsize=12)
plt.ylabel('도로명', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6, axis='x')
plt.tight_layout()
plt.savefig('top10_congested_roads.png')
print("\n✅ 도로별 혼잡도 분석 그래프 'top10_congested_roads.png' 저장 완료")