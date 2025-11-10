### Quote

1️⃣ 기본 정보 → 종목, 거래소, 통화

| 필드         | 의미                       |
| ---------- | ------------------------ |
| `symbol`   | 종목 심볼 (예: AAPL)          |
| `name`     | 종목 이름 (예: Apple Inc.)    |
| `exchange` | 거래소 (예: NASDAQ)          |
| `mic_code` | ISO 10383 기준 시장 코드 (MIC) |
| `currency` | 통화 단위 (예: USD)           |


2️⃣ 시세 정보 → OHLC(시가, 고가, 저가, 종가), 거래량, 변화량

| 필드               | 의미                           |
| ---------------- | ---------------------------- |
| `datetime`       | 해당 바(candle)가 열린 시간 (타임존 적용) |
| `timestamp`      | `datetime`의 Unix timestamp   |
| `last_quote_at`  | 마지막 분봉 시점 timestamp          |
| `open`           | 현재 바 시작 시 가격                 |
| `high`           | 현재 바에서 최고 가격                 |
| `low`            | 현재 바에서 최저 가격                 |
| `close`          | 현재 바 종료 가격                   |
| `volume`         | 현재 바 거래량 (모든 종목에 있는 건 아님)    |
| `previous_close` | 이전 바 종료 가격                   |
| `change`         | `close - previous_close`     |
| `percent_change` | 가격 변동률 `%`                   |


3️⃣ 거래량 관련

| 필드               | 의미                            |
| ---------------- | ----------------------------- |
| `average_volume` | 지정 기간 평균 거래량 (모든 종목에 있는 건 아님) |


4️⃣ 가격 변동 (롤링) → 최근 변화, 기간별 변화

| 필드                  | 의미                                 |
| ------------------- | ---------------------------------- |
| `rolling_1d_change` | 1일간 가격 변동률 (주로 암호화폐)               |
| `rolling_7d_change` | 7일간 가격 변동률                         |
| `rolling_change`    | 요청한 기간(`rolling_period`) 기준 가격 변동률 |


5️⃣ 시장 상태

| 필드               | 의미                    |
| ---------------- | --------------------- |
| `is_market_open` | 시장 열림 여부 (True/False) |


6️⃣ 52주 기준 정보 → 장기 가격 범위와 변화량

| 필드                                   | 의미                |
| ------------------------------------ | ----------------- |
| `fifty_two_week.low`                 | 52주 최저 가격         |
| `fifty_two_week.high`                | 52주 최고 가격         |
| `fifty_two_week.low_change`          | 현재 가격 - 52주 최저    |
| `fifty_two_week.high_change`         | 현재 가격 - 52주 최고    |
| `fifty_two_week.low_change_percent`  | 52주 최저 대비 변동률 (%) |
| `fifty_two_week.high_change_percent` | 52주 최고 대비 변동률 (%) |
| `fifty_two_week.range`               | 52주 최고-최저 가격 범위   |


7️⃣ 시간외/확장 거래 (옵션/프리포스트) → 장 마감 후 가격 변화

| 필드                        | 의미                                |
| ------------------------- | --------------------------------- |
| `extended_change`         | 정규 거래 종료 후 가격 변화 (prepost=true 시) |
| `extended_percent_change` | 정규 거래 종료 후 가격 변동률 (%)             |
| `extended_price`          | 최신 시간외 가격                         |
| `extended_timestamp`      | 최신 시간외 가격 timestamp               |

