# weekly-sales-report 마켓플레이스

구글 시트 판매내역을 집계해 지난주 매출 리포트를 슬랙 채널에 올리는 스킬입니다.

## 설치

```
/plugin marketplace add danjeong8105/weekly-sales-report-marketplace
/plugin install weekly-sales-report@weekly-sales-report-marketplace
```

## 사용 전 준비
- 구글 드라이브와 슬랙 커넥터가 연결되어 있어야 합니다.
- 시트의 `판매내역` 탭에 열이 있어야 합니다: 주문일, 주문번호, 판매채널, 카테고리, 상품명, 옵션, 수량, 판매단가, 결제금액, 배송비
- 슬랙 채널은 실행할 때 물어봅니다.
