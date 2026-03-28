# BionicPRO Reports System

## 🚀 Запуск проекта

### 1. Запуск всех сервисов

```bash
docker-compose up --build
```

---

### 2. Доступ к сервисам

* Frontend: http://localhost:3000
* Keycloak: http://localhost:8080
* Airflow: http://localhost:8081
* ClickHouse: localhost:9000

---

## Airflow

1. Открыть Airflow UI (http://localhost:8081)
2. Авторизоваться admin / admin
3. Включить DAG `etl_user_reports`
4. Запустить вручную или дождаться запуска по расписанию

---

## Проверка данных в ClickHouse

```bash
docker exec -it clickhouse clickhouse-client
```

```sql
SELECT * FROM user_reports;
```

---

## Получение отчёта

1. Открыть UI (http://localhost:3000)
2. Авторизоваться prothetic1 / prothetic123
3. Нажать "Download Report"
