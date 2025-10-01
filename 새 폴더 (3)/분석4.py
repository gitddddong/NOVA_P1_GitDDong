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

# ----------------------------------------------------------------------
# 1. '일일 총 교통량' 데이터 처리 (TrafficVolume(LINK).csv)
# ----------------------------------------------------------------------
try:
    # 8줄을 건너뛰고 헤더 없이 데이터를 불러옵니다.
    df_volume = pd.read_csv('TrafficVolume(LINK) (2).csv', encoding='utf-8', skiprows=8, header=None)

    # 필요한 컬럼(LINK ID, 전체-평일-전일 교통량)만 선택
    df_volume = df_volume[[0, 7]].copy()
    df_volume.columns = ['LINK ID', 'Total_Volume']

    # 데이터 타입 변환 및 정리
    df_volume['LINK ID'] = pd.to_numeric(df_volume['LINK ID'], errors='coerce')
    df_volume['Total_Volume'] = pd.to_numeric(df_volume['Total_Volume'], errors='coerce')
    df_volume.dropna(inplace=True)
    df_volume = df_volume.astype({'LINK ID': int, 'Total_Volume': int})

    print("✅ '일일 총 교통량' 데이터 처리 완료")

except FileNotFoundError:
    print("오류: 'TrafficVolume(LINK).csv' 파일을 찾을 수 없습니다.")
    exit()
except Exception as e:
    print(f"교통량 데이터 처리 중 오류 발생: {e}")
    exit()

# ----------------------------------------------------------------------
# 2. '일일 CO₂ 배출량' 데이터 처리 (CongestIndex(LINK).xlsx - Sheet0.csv)
# ----------------------------------------------------------------------
try:
    # 8줄을 건너뛰고 헤더 없이 데이터를 불러옵니다.
    df_co2 = pd.read_csv('CongestIndex(LINK).csv', encoding='utf-8', skiprows=8, header=None)

    # 필요한 컬럼(LINK ID, 전체 CO2 배출량)만 선택
    df_co2 = df_co2[[0, 7]].copy()
    df_co2.columns = ['LINK ID', 'CO2_Emissions']

    # 데이터 타입 변환 및 정리
    df_co2['LINK ID'] = pd.to_numeric(df_co2['LINK ID'], errors='coerce')
    df_co2['CO2_Emissions'] = pd.to_numeric(df_co2['CO2_Emissions'], errors='coerce')
    df_co2.dropna(inplace=True)
    df_co2 = df_co2.astype({'LINK ID': int})

    print("✅ '일일 CO₂ 배출량' 데이터 처리 완료")

except FileNotFoundError:
    print("오류: 'CongestIndex(LINK).xlsx - Sheet0.csv' 파일을 찾을 수 없습니다.")
    exit()
except Exception as e:
    print(f"CO₂ 데이터 처리 중 오류 발생: {e}")
    exit()

# ----------------------------------------------------------------------
# 3. 데이터 결합 및 분석
# ----------------------------------------------------------------------
# 'LINK ID'를 기준으로 두 데이터를 결합
df_merged = pd.merge(df_volume, df_co2, on='LINK ID')

print("\n[교통량 및 CO₂ 배출량 결합 데이터 샘플]")
print(df_merged.head())

# 상관관계 분석
correlation = df_merged['Total_Volume'].corr(df_merged['CO2_Emissions'])
print(f"\n📈 일일 총 교통량과 CO₂ 배출량의 상관계수: {correlation:.4f}")
print("(1에 가까울수록 매우 강한 양의 상관관계를 의미합니다)")

# ----------------------------------------------------------------------
# 4. 시각화: 스캐터 플롯(Scatter Plot)
# ----------------------------------------------------------------------
plt.figure(figsize=(12, 8))
plt.scatter(df_merged['Total_Volume'], df_merged['CO2_Emissions'], alpha=0.5, color='green')
plt.title('일일 총 교통량과 CO₂ 배출량의 관계', fontsize=16)
plt.xlabel('일일 총 교통량 (대/일)', fontsize=12)
plt.ylabel('일일 CO₂ 배출량 (g/일)', fontsize=12)  # 단위는 g/일로 추정됩니다.
plt.grid(True)
plt.tight_layout()
plt.savefig('volume_vs_co2.png')

print("\n✅ 분석 결과 그래프가 'volume_vs_co2.png' 파일로 저장되었습니다.")