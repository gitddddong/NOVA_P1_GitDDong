# %%
from dbfread import DBF
import pandas as pd
import sqlite3

print("node link test")
# DBF 두 개를 읽기
df1 = pd.DataFrame(iter(DBF("./data/seoul_lev6_2023/seoul_link_lev6_2023.dbf", encoding="cp949", load=True)))
df2 = pd.DataFrame(iter(DBF("./data/seoul_link_lev5.5_2023/seoul_link_lev5.5_2023.dbf", encoding="cp949", load=True)))
dfc = pd.read_csv("./data/level5.5_level6_matchingtable_2023.csv")

print(dfc.columns)       # 열 이름 확인
print(dfc.head(3))       # 파싱 정상 여부 확인
# SQLite 메모리 DB 연결
conn = sqlite3.connect(":memory:")

# 두 개 테이블로 저장
df1.to_sql("seoul_node_lev6_2023", conn, index=False, if_exists="replace")
df2.to_sql("seoul_link_lev5.5_2023", conn, index=False, if_exists="replace")
dfc.to_sql("lev5_5_2_6", conn, index=False, if_exists="replace")

# SQL 실행 (예: 고객과 주문 조인) ex) 1014051
query = """
SELECT l6.*
FROM lev5_5_2_6 c
JOIN seoul_node_lev6_2023 l6
  ON c.fnode_id = l6.node_id 
WHERE c.level5_id = '1014051'
"""
query2 = """
SELECT l6.*
FROM lev5_5_2_6 c
JOIN "seoul_link_lev5.5_2023" l55
  ON c.level5_id = l55.link_id
JOIN seoul_node_lev6_2023 l6
  ON l55.fnode_id = l6.node_id
WHERE c.level5_id = '1014051';
"""

print(pd.read_sql_query("PRAGMA table_info('lev5_5_2_6')", conn))
result = pd.read_sql_query(query, conn)

print(result)
