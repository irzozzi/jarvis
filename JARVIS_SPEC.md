
---

# JARVIS_SPEC.md
## Техническая спецификация интеллектуальной системы стимулирования развития личности

---

## 1. ОБЩАЯ ИНФОРМАЦИЯ

**Название проекта:** Джарвис (Jarvis)  
**Назначение:** Персональный AI-ассистент для формирования привычек, планирования и развития личности  
**Архитектура:** Клиент-серверная (бэкенд на FastAPI + мобильное приложение на React Native)  
**Версия спецификации:** 2.0  
**Дата последнего обновления:** 2026-04-07  

---

## 2. СХЕМА БАЗЫ ДАННЫХ (POSTGRESQL)

### 2.1. Модель `User` (пользователи)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR UNIQUE,
    reset_password_token VARCHAR UNIQUE,
    reset_password_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2. Модель `RefreshToken` (refresh‑токены)
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.3. Модель `Personality` (OCEAN‑профиль)
```sql
CREATE TABLE personality (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    answers JSONB,
    openness FLOAT,
    conscientiousness FLOAT,
    extraversion FLOAT,
    agreeableness FLOAT,
    neuroticism FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.4. Модель `Habit` (привычки)
```sql
CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    type VARCHAR NOT NULL,          -- boolean, numeric, timer
    target FLOAT NOT NULL,
    unit VARCHAR,
    schedule JSONB,                 -- сложные расписания
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    deleted_at TIMESTAMP
);
```

### 2.5. Модель `HabitLog` (логи выполнения)
```sql
CREATE TABLE habit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id UUID NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    value FLOAT NOT NULL,
    notes TEXT,
    mood INTEGER,
    completed_at TIMESTAMP DEFAULT NOW(),
    context_id UUID REFERENCES context(id) ON DELETE SET NULL
);
```

### 2.6. Модель `Context` (контекстные данные)
```sql
CREATE TABLE context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    latitude FLOAT,
    longitude FLOAT,
    location_type VARCHAR,
    weather JSONB,
    activity VARCHAR,
    raw_data JSONB
);
```

### 2.7. Модель `Goal` (цели) и `GoalCategory` (категории)
```sql
CREATE TABLE goal_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR
);

CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES goal_categories(id) ON DELETE SET NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    custom_text TEXT,
    start_date TIMESTAMP DEFAULT NOW(),
    target_date TIMESTAMP,
    progress FLOAT DEFAULT 0,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);
```

### 2.8. Модель `GoalProgressLog` (история прогресса целей)
```sql
CREATE TABLE goal_progress_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    progress FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.9. Модель `Event` (события календаря)
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    habit_id UUID REFERENCES habits(id) ON DELETE SET NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    recurrence JSONB,
    status VARCHAR DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.10. Модели чата (`Conversation`, `Message`)
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR,
    pending_schedule JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE messagerole AS ENUM ('user', 'assistant', 'system');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role messagerole NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 3. API ЭНДПОИНТЫ (REST + WebSocket)

### 3.1. Аутентификация и пользователи

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| POST | `/auth/register` | Регистрация | `{email, password}` | `UserOut` |
| POST | `/auth/login` | Логин (form‑data) | `username, password` | `Token` |
| POST | `/auth/login-json` | Логин (JSON) | `{email, password}` | `Token` |
| POST | `/auth/refresh` | Обновление токена | `{refresh_token}` | `Token` |
| GET | `/auth/verify` | Подтверждение email | `?token=...` | `{message}` |
| POST | `/auth/forgot-password` | Запрос сброса пароля | `?email=...` | `{message}` |
| POST | `/auth/reset-password` | Сброс пароля | `?token=...&new_password=...` | `{message}` |
| POST | `/auth/change-password` | Смена пароля (авториз.) | `{old_password, new_password}` | `{message}` |
| GET | `/users/me` | Профиль текущего пользователя | – | `UserOut` |

### 3.2. Привычки

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/habits` | Список привычек | `?skip=0&limit=100` | `[HabitOut]` |
| POST | `/habits` | Создание привычки | `HabitCreate` | `HabitOut` |
| GET | `/habits/{id}` | Детали привычки | – | `HabitOut` |
| PUT | `/habits/{id}` | Обновление привычки | `HabitCreate` | `HabitOut` |
| DELETE | `/habits/{id}` | Удаление (soft delete) | – | 204 |
| PATCH | `/habits/{id}/restore` | Восстановление | – | `HabitOut` |
| POST | `/habits/{id}/logs` | Добавить лог | `HabitLogCreate` | `HabitLogOut` |
| GET | `/habits/{id}/logs` | Логи привычки | `?skip=0&limit=100` | `[HabitLogOut]` |
| GET | `/habits/{id}/stats` | Статистика привычки | – | `{streak, completion_rate_7d, ...}` |
| GET | `/habits/stats` | Общая статистика | – | `{total_habits, active_habits, ...}` |
| GET | `/habits/chart` | Данные для графика | `?days=30&group_by=day` | `{overall, habits}` |
| GET | `/habits/heatmap` | Тепловая карта | `?year=2026` | `[{date, intensity}]` |
| GET | `/habits/context-stats` | Статистика по контексту | – | `{by_location, by_activity, by_time_of_day}` |
| GET | `/habits/{id}/predict` | Предсказание срыва | – | `{risk, score, message}` |

### 3.3. Цели и категории

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/goals` | Список целей | `?skip=0&limit=100` | `[GoalOut]` |
| POST | `/goals` | Создание цели | `GoalCreate` | `GoalOut` |
| GET | `/goals/{id}` | Детали цели | – | `GoalOut` |
| PUT | `/goals/{id}` | Обновление цели | `GoalUpdate` | `GoalOut` |
| DELETE | `/goals/{id}` | Удаление (soft delete) | – | 204 |
| PATCH | `/goals/{id}/restore` | Восстановление | – | `GoalOut` |
| GET | `/goals/{id}/history` | История прогресса | – | `[{date, progress}]` |
| GET | `/goals/chart/{id}` | Данные для графика | `?days=90` | `[ChartPoint]` |
| POST | `/goals/{id}/habits/{hid}` | Привязать привычку | – | 204 |
| DELETE | `/goals/{id}/habits/{hid}` | Отвязать привычку | – | 204 |

### 3.4. Календарь событий

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/events` | Список событий | `?skip=0&limit=100` | `[EventOut]` |
| POST | `/events` | Создание события | `EventCreate` | `EventOut` |
| GET | `/events/{id}` | Детали события | – | `EventOut` |
| PUT | `/events/{id}` | Обновление | `EventUpdate` | `EventOut` |
| DELETE | `/events/{id}` | Удаление | – | 204 |

### 3.5. Личность (OCEAN)

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/personality/questions` | Список вопросов | – | `[QuestionOut]` |
| POST | `/personality` | Сохранить ответы | `{answers: [{question_id, answer}]}` | `PersonalityOut` |
| GET | `/personality` | Получить OCEAN‑профиль | – | `PersonalityOut` |

### 3.6. Контекст

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| POST | `/context` | Сохранить контекст | `ContextCreate` | `ContextOut` |

### 3.7. Инсайты

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/insights` | Список инсайтов | `?skip=0&limit=50&unread_only=false` | `[InsightOut]` |
| POST | `/insights/generate` | Генерация инсайтов | – | `[InsightOut]` |
| PATCH | `/insights/{id}/read` | Отметить прочитанным | – | `InsightOut` |
| DELETE | `/insights/{id}` | Удалить инсайт | – | 204 |

### 3.8. Уведомления

| Метод | URL | Описание | Request body | Response |
|-------|-----|----------|--------------|----------|
| GET | `/notifications/upcoming` | Предстоящие события | `?minutes=30` | `[EventOut]` |

### 3.9. Чат (WebSocket)

**URL:** `ws://localhost:8000/ws?token={access_token}`

**Формат сообщений (текстовый):**
- Клиент отправляет строку (сообщение пользователя).
- Сервер отвечает строкой (ответ ассистента).

**Внутренний контекст:** в промпт передаются данные пользователя (привычки, инсайты, цели, OCEAN‑профиль, история диалога).

---

## 4. РЕАЛИЗОВАННЫЕ ФИЧИ (v2.0)

### 4.1. Аутентификация и безопасность
- ✅ JWT access + refresh токены
- ✅ Регистрация и логин (form‑data и JSON)
- ✅ Подтверждение email (с реальной отправкой через SMTP)
- ✅ Сброс пароля (через email)
- ✅ Смена пароля для авторизованных пользователей
- ✅ Защита эндпоинтов через `deps.get_current_user`
- ✅ Мягкое удаление (`deleted_at`) для привычек и целей
- ✅ Восстановление мягко удалённых объектов

### 4.2. Привычки
- ✅ CRUD с валидацией
- ✅ Три типа: boolean, numeric, timer
- ✅ Расписания: ежедневно, по дням недели, `every_n_days`, `monthly`, `custom_dates`
- ✅ Логи выполнения с заметками, настроением и контекстом
- ✅ Статистика: серии, проценты выполнения (с учётом расписания)
- ✅ Предсказание срывов (rule‑based)
- ✅ Графики и тепловая карта

### 4.3. Цели и проекты
- ✅ Создание целей (свободный текст + AI‑анализ категории)
- ✅ Привязка привычек к целям
- ✅ Прогресс цели (ручное обновление)
- ✅ История прогресса (логирование изменений)
- ✅ Мягкое удаление и восстановление

### 4.4. AI‑ассистент (чат)
- ✅ WebSocket‑чат с аутентификацией
- ✅ Интеграция с YandexGPT (модель yandexgpt-5-lite / yandexgpt-5-pro)
- ✅ Контекст диалога (история сообщений)
- ✅ Персонализация через OCEAN‑профиль
- ✅ Создание событий календаря через чат
- ✅ Создание привычек с расписанием через чат (с подтверждением)

### 4.5. Календарь
- ✅ Модель `Event`, CRUD эндпоинты
- ✅ Умные уведомления о предстоящих событиях

### 4.6. Личность (OCEAN)
- ✅ 15 вопросов (по 3 на каждый фактор)
- ✅ Расчёт баллов (0–100) и сохранение в БД
- ✅ Эндпоинт для получения вопросов
- ✅ Использование профиля в промпте AI

### 4.7. Контекст и аналитика
- ✅ Сбор контекста (геолокация, активность)
- ✅ Тепловая карта выполнения привычек
- ✅ Агрегация графиков по неделям/месяцам
- ✅ Статистика по контексту (location_type, activity, time_of_day)

### 4.8. Инфраструктура
- ✅ Alembic миграции (управление схемой БД)
- ✅ Docker‑compose (PostgreSQL + Redis) – опционально
- ✅ Поддержка SQLite и PostgreSQL
- ✅ Логирование, отладка

---

## 5. ПЛАН УЛУЧШЕНИЯ БЭКЕНДА (РОADMAP)

### 5.1. Завершить текущие улучшения
- [x] Агрегация графиков по неделям/месяцам
- [x] Тепловая карта выполнения привычек
- [x] История прогресса целей
- [x] Статистика по контексту

### 5.2. Кэширование в Redis
- [ ] Установка и настройка Redis
- [ ] Кэширование результатов `/habits/chart`, `/habits/stats`
- [ ] Инвалидация кэша при добавлении/изменении логов

### 5.3. Фоновые задачи (Celery + Redis)
- [ ] Настройка Celery
- [ ] Периодическая генерация инсайтов (раз в сутки)
- [ ] Отправка push‑уведомлений о предстоящих событиях

### 5.4. Интеграция с внешними календарями
- [ ] OAuth2 для Google Calendar
- [ ] Экспорт событий из Джарвиса в Google Calendar
- [ ] Двусторонняя синхронизация

### 5.5. Мобильное приложение (React Native + Expo)
- [ ] Экраны: авторизация, онбординг (OCEAN), главный (привычки), статистика, чат, календарь
- [ ] Интеграция с бэкендом (API + WebSocket)
- [ ] Геолокация и push‑уведомления
- [ ] Сборка APK / IPA для демонстрации

### 5.6. Документация и подготовка к защите
- [ ] README для бэкенда и мобильного приложения
- [ ] Схема архитектуры
- [ ] Демо‑видео (5–7 минут)
- [ ] Презентация

---

## 6. СТРУКТУРА ПРОЕКТА

```
jarvis/
├── backend/
│   ├── app/
│   │   ├── api/               # эндпоинты (auth, users, habits, goals, events, personality, context, insights, chat, notifications)
│   │   ├── core/              # database.py, security.py
│   │   ├── models/            # SQLAlchemy модели (user, habit, goal, event, personality, context, chat, refresh_token, goal_progress_log)
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── services/          # stats, analytics, prediction, personality_service, email_service, refresh_token_service, charts, habit_schedule_extractor, date_extractor, event_service, llm_service
│   │   ├── utils/             # вспомогательные функции (date_parser и др.)
│   │   └── main.py
│   ├── alembic/               # миграции
│   ├── venv/                  # виртуальное окружение
│   ├── .env
│   └── requirements.txt
├── mobile/                    # React Native (Expo) – планируется
│   ├── src/
│   │   ├── screens/           # экраны
│   │   ├── components/        # компоненты
│   │   ├── navigation/        # навигация
│   │   └── services/          # API клиенты
│   └── App.js
├── docs/                      # документация (схемы, спецификации)
└── README.md
```

---

## 7. ТЕХНОЛОГИЧЕСКИЙ СТЕК

### Бэкенд
- **Python** 3.14
- **FastAPI** – веб‑фреймворк
- **SQLAlchemy** – ORM
- **Alembic** – миграции
- **PostgreSQL** – основная БД (также поддерживается SQLite)
- **Redis** – кэширование и брокер (планируется)
- **Celery** – фоновые задачи (планируется)
- **YandexGPT API** – языковая модель
- **JWT** – аутентификация
- **SMTP** – отправка писем (Mail.ru)

### Фронтенд (планируется)
- **React Native** + **Expo**
- **Axios** – HTTP‑клиент
- **WebSocket API** – для чата
- **AsyncStorage** – локальное хранение
- **Expo‑Location** – геолокация
- **Expo‑Notifications** – push‑уведомления

### Инфраструктура
- **Git** + **GitHub**
- **Docker** (опционально)
- **ngrok** – для тестирования публичного доступа

---

## 8. ПОЛЕЗНЫЕ КОМАНДЫ

### Бэкенд
```bash
# Активировать окружение
cd backend
.\venv\Scripts\activate

# Запустить сервер
uvicorn app.main:app --reload

# Создать миграцию
alembic revision --autogenerate -m "message"
alembic upgrade head

# Подключиться к БД
psql -U postgres -d jarvis_dev
```

### WebSocket тестирование
```bash
wscat -c "ws://localhost:8000/ws?token=JWT_TOKEN"
```

### Git
```bash
git add .
git commit -m "message"
git push
```

---

## 9. ПРИМЕЧАНИЯ

- Все эндпоинты (кроме `/auth/*`, `/docs`, `/openapi.json`) требуют JWT‑токен.
- WebSocket требует токен в query‑параметре `?token=...`.
- Для реальной отправки писем в `.env` должны быть заданы `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`.
- OCEAN‑профиль используется в промпте AI для персонализации.
- Мягкое удаление реализовано через поле `deleted_at` (для привычек и целей).
- Тепловая карта возвращает интенсивность от 0 до 100 (процент выполнения от максимального количества привычек в день).

---

## 10. ИСТОРИЯ ИЗМЕНЕНИЙ

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2026-04-07 | 2.0 | Добавлены улучшения графиков, тепловая карта, история прогресса целей, статистика по контексту. |
| 2026-04-07 | 1.9 | Реализована интеграция с YandexGPT, OCEAN, сложные расписания, мягкое удаление. |
| 2026-04-06 | 1.5 | Добавлены refresh‑токены, email‑верификация, сброс пароля. |
| 2026-04-05 | 1.0 | Базовая версия: привычки, логи, статистика, инсайты, контекст, цели, календарь. |

---
