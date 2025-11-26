# postgres_olap_optimizer_massive.py
import psycopg2
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class PostgresMassiveOLAPOptimizer:
    def __init__(self, connection_params):
        self.conn_params = connection_params

    def create_massive_test_data(self):
        """Создает ОГРОМНЫЙ объем тестовых данных для реалистичного тестирования"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        # Очищаем существующие таблицы
        print("🧹 Очистка старых данных...")
        cur.execute("DROP TABLE IF EXISTS transactions CASCADE")
        cur.execute("DROP TABLE IF EXISTS accounts CASCADE") 
        cur.execute("DROP TABLE IF EXISTS clients CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_client_stats CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_transactions CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_city_stats CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_analytics CASCADE")

        # Создаем таблицы с оптимизированной структурой
        print("📦 Создание таблиц...")
        cur.execute("""
            CREATE TABLE clients (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                phone VARCHAR(20),
                city VARCHAR(50),
                age INTEGER,
                income_level VARCHAR(20),
                registration_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE accounts (
                account_id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                account_number VARCHAR(20) UNIQUE,
                balance DECIMAL(15,2) DEFAULT 0,
                account_type VARCHAR(20),
                currency VARCHAR(3) DEFAULT 'RUB',
                status VARCHAR(10) DEFAULT 'active',
                credit_limit DECIMAL(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE transactions (
                transaction_id BIGSERIAL PRIMARY KEY,
                from_account_id INTEGER NOT NULL,
                to_account_id INTEGER NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                status VARCHAR(10) DEFAULT 'completed',
                category VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        print("🔄 Создание МАССИВНОГО объема тестовых данных...")

        # Создаем 50,000 клиентов
        self._create_massive_clients(50000)

        # Создаем 150,000 счетов  
        self._create_massive_accounts(150000)

        # Создаем 5,000,000 транзакций
        self._create_massive_transactions(5000000)

        print("✅ МАССИВНЫЙ объем тестовых данных создан!")

    def _create_massive_clients(self, count):
        """Создает большое количество клиентов"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        first_names = ["Ivan", "Petr", "Maria", "Anna", "Sergey", "Olga", "Alexey", "Elena", "Dmitry", "Natalya",
                      "Andrey", "Tatiana", "Vladimir", "Svetlana", "Mikhail", "Yulia", "Pavel", "Ekaterina", "Nikolay", "Irina"]
        last_names = ["Ivanov", "Petrov", "Sidorov", "Smirnov", "Kuznetsov", "Popov", "Vasilev", "Pavlov", "Semenov", "Golubev",
                     "Volkov", "Romanov", "Morozov", "Orlov", "Belyaev", "Komarov", "Titov", "Kiselev", "Gusev", "Vinogradov"]
        cities = ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny Novgorod", 
                 "Samara", "Omsk", "Chelyabinsk", "Rostov", "Ufa", "Volgograd", "Krasnoyarsk", "Voronezh"]
        income_levels = ["low", "medium", "high", "premium"]

        print(f"👥 Создание {count} клиентов...")
        
        batch_size = 1000
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []
            
            for i in range(batch_start, batch_end):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i}@bank.ru"
                city = random.choice(cities)
                age = random.randint(18, 80)
                income = random.choice(income_levels)
                reg_date = datetime.now() - timedelta(days=random.randint(1, 365*5))

                values.append((first_name, last_name, email, f"+7{random.randint(9000000000, 9999999999)}", 
                              city, age, income, reg_date))

            cur.executemany(
                "INSERT INTO clients (first_name, last_name, email, phone, city, age, income_level, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                values
            )
            conn.commit()
            
            if batch_start % 10000 == 0:
                print(f"   Создано {batch_start} клиентов...")

        conn.close()
        print(f"✅ Создано {count} клиентов")

    def _create_massive_accounts(self, count):
        """Создает большое количество счетов"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        # Получаем ID клиентов
        cur.execute("SELECT client_id FROM clients ORDER BY client_id")
        client_ids = [row[0] for row in cur.fetchall()]

        print(f"🏦 Создание {count} счетов...")
        
        batch_size = 2000
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []
            
            for i in range(batch_start, batch_end):
                client_id = random.choice(client_ids)
                account_number = f"40702{random.randint(100000000000, 999999999999)}"
                balance = random.randint(1000, 1000000)
                account_type = random.choice(['checking', 'savings', 'credit', 'investment', 'business'])
                credit_limit = random.randint(0, 500000) if account_type == 'credit' else 0

                values.append((client_id, account_number, balance, account_type, credit_limit))

            cur.executemany(
                "INSERT INTO accounts (client_id, account_number, balance, account_type, credit_limit) VALUES (%s, %s, %s, %s, %s)",
                values
            )
            conn.commit()
            
            if batch_start % 20000 == 0:
                print(f"   Создано {batch_start} счетов...")

        conn.close()
        print(f"✅ Создано {count} счетов")

    def _create_massive_transactions(self, count):
        """Создает ОГРОМНОЕ количество транзакций"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        # Получаем ID счетов
        cur.execute("SELECT account_id FROM accounts ORDER BY account_id")
        account_ids = [row[0] for row in cur.fetchall()]

        print(f"💸 Создание {count} транзакций...")
        
        transaction_types = ['transfer', 'payment', 'deposit', 'withdrawal', 'fee', 'salary', 'refund', 'investment']
        categories = ['food', 'transport', 'housing', 'entertainment', 'healthcare', 'education', 'shopping', 'travel']
        
        batch_size = 5000
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            values = []
            
            for i in range(batch_start, batch_end):
                from_account = random.choice(account_ids)
                to_account = random.choice(account_ids)
                
                # Убедимся, что from_account != to_account
                while from_account == to_account:
                    to_account = random.choice(account_ids)
                    
                amount = round(random.uniform(1, 50000), 2)
                transaction_type = random.choice(transaction_types)
                category = random.choice(categories)
                created_at = datetime.now() - timedelta(
                    days=random.randint(0, 365*3), 
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )

                values.append((from_account, to_account, amount, transaction_type, category, created_at))

            cur.executemany(
                "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, category, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                values
            )
            conn.commit()
            
            if batch_start % 500000 == 0:
                print(f"   Создано {batch_start} транзакций...")

        conn.close()
        print(f"✅ Создано {count} транзакций")

    def create_optimized_indexes(self):
        """Создает оптимизированные индексы для OLAP запросов"""
        print("📊 Создание оптимизированных индексов...")
        
        indexes = [
            # Индексы для транзакций (BRIN для временных рядов)
            "CREATE INDEX IF NOT EXISTS idx_transactions_created_at_brin ON transactions USING BRIN(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions(transaction_type, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_amount_partial ON transactions(amount) WHERE amount > 1000",
            "CREATE INDEX IF NOT EXISTS idx_transactions_from_account ON transactions(from_account_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_to_account ON transactions(to_account_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date_category ON transactions(DATE(created_at), category)",
            
            # Индексы для счетов
            "CREATE INDEX IF NOT EXISTS idx_accounts_client_id ON accounts(client_id)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_type_balance ON accounts(account_type, balance)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_balance_partial ON accounts(balance) WHERE balance > 10000",
            
            # Индексы для клиентов
            "CREATE INDEX IF NOT EXISTS idx_clients_city ON clients(city)",
            "CREATE INDEX IF NOT EXISTS idx_clients_reg_date ON clients(registration_date)",
            "CREATE INDEX IF NOT EXISTS idx_clients_name_composite ON clients(last_name, first_name)",
            "CREATE INDEX IF NOT EXISTS idx_clients_income_city ON clients(income_level, city)",
            "CREATE INDEX IF NOT EXISTS idx_clients_age_income ON clients(age, income_level)"
        ]

        for index_sql in indexes:
            try:
                conn = psycopg2.connect(**self.conn_params)
                cur = conn.cursor()
                cur.execute(index_sql)
                conn.commit()
                conn.close()
                print(f"✅ Создан индекс: {index_sql[:70]}...")
            except Exception as e:
                print(f"⚠️  Ошибка создания индекса: {e}")

    def create_materialized_views(self):
        """Создает материализованные представления для тяжелых агрегаций"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        print("🗃️ Создание материализованных представлений...")

        # Статистика клиентов
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_client_stats CASCADE")
        cur.execute("""
            CREATE MATERIALIZED VIEW mv_client_stats AS
            SELECT 
                c.client_id,
                c.first_name || ' ' || c.last_name as client_name,
                c.city,
                c.age,
                c.income_level,
                c.registration_date,
                COUNT(DISTINCT a.account_id) as account_count,
                SUM(a.balance) as total_balance,
                AVG(a.balance) as avg_balance,
                COUNT(t.transaction_id) as transaction_count,
                SUM(t.amount) as total_volume,
                AVG(t.amount) as avg_transaction_amount,
                MIN(t.created_at) as first_transaction_date,
                MAX(t.created_at) as last_transaction_date
            FROM clients c
            LEFT JOIN accounts a ON c.client_id = a.client_id
            LEFT JOIN transactions t ON a.account_id = t.from_account_id
            GROUP BY c.client_id, client_name, c.city, c.age, c.income_level, c.registration_date
        """)

        # Ежедневная статистика
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_transactions CASCADE")
        cur.execute("""
            CREATE MATERIALIZED VIEW mv_daily_transactions AS
            SELECT 
                DATE(created_at) as transaction_date,
                transaction_type,
                category,
                COUNT(*) as transaction_count,
                SUM(amount) as daily_volume,
                AVG(amount) as avg_amount,
                COUNT(DISTINCT from_account_id) as unique_accounts,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM transactions
            GROUP BY DATE(created_at), transaction_type, category
        """)

        # Статистика по городам
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_city_stats CASCADE")
        cur.execute("""
            CREATE MATERIALIZED VIEW mv_city_stats AS
            SELECT 
                c.city,
                COUNT(DISTINCT c.client_id) as client_count,
                COUNT(DISTINCT a.account_id) as account_count,
                SUM(a.balance) as total_balance,
                AVG(a.balance) as avg_balance,
                COUNT(t.transaction_id) as transaction_count,
                SUM(t.amount) as transaction_volume,
                AVG(c.age) as avg_client_age
            FROM clients c
            LEFT JOIN accounts a ON c.client_id = a.client_id
            LEFT JOIN transactions t ON a.account_id = t.from_account_id
            GROUP BY c.city
        """)

        # Месячная аналитика
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_analytics CASCADE")
        cur.execute("""
            CREATE MATERIALIZED VIEW mv_monthly_analytics AS
            SELECT 
                EXTRACT(YEAR FROM t.created_at) as year,
                EXTRACT(MONTH FROM t.created_at) as month,
                c.income_level,
                c.city,
                t.transaction_type,
                t.category,
                COUNT(*) as transaction_count,
                SUM(t.amount) as monthly_volume,
                AVG(t.amount) as avg_amount,
                COUNT(DISTINCT c.client_id) as unique_clients
            FROM transactions t
            JOIN accounts a ON t.from_account_id = a.account_id
            JOIN clients c ON a.client_id = c.client_id
            GROUP BY year, month, c.income_level, c.city, t.transaction_type, t.category
        """)

        conn.commit()
        conn.close()

        # Создаем индексы для материализованных представлений
        self.create_mv_indexes()
        print("✅ Материализованные представления созданы")

    def create_mv_indexes(self):
        """Создает индексы для материализованных представлений"""
        mv_indexes = [
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_client_stats_id ON mv_client_stats(client_id)",
            "CREATE INDEX IF NOT EXISTS idx_mv_client_stats_city ON mv_client_stats(city)",
            "CREATE INDEX IF NOT EXISTS idx_mv_client_stats_income ON mv_client_stats(income_level)",
            "CREATE INDEX IF NOT EXISTS idx_mv_daily_date_type ON mv_daily_transactions(transaction_date, transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_mv_city_stats_city ON mv_city_stats(city)",
            "CREATE INDEX IF NOT EXISTS idx_mv_monthly_year_month ON mv_monthly_analytics(year, month)",
            "CREATE INDEX IF NOT EXISTS idx_mv_monthly_income_city ON mv_monthly_analytics(income_level, city)"
        ]

        for index_sql in mv_indexes:
            try:
                conn = psycopg2.connect(**self.conn_params)
                cur = conn.cursor()
                cur.execute(index_sql)
                conn.commit()
                conn.close()
                print(f"✅ Создан индекс MV: {index_sql[:60]}...")
            except Exception as e:
                print(f"⚠️  Ошибка создания индекса MV: {e}")

    def analyze_query(self, query: str, iterations: int = 2) -> Dict:
        """Анализирует запрос с многократным выполнением для точности"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()

        try:
            # Прогрев кэша (только для первого запуска)
            try:
                cur.execute(query)
                cur.fetchall()
            except:
                pass

            total_time = 0
            successful_runs = 0
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    cur.execute(query)
                    cur.fetchall()
                    total_time += time.time() - start_time
                    successful_runs += 1
                except Exception as e:
                    if i == 0:  # Только для первого запуска показываем ошибку
                        return {'execution_time': 0, 'error': str(e)}

            avg_time = total_time / successful_runs if successful_runs > 0 else 0

            return {
                'execution_time': avg_time,
                'iterations': successful_runs
            }
        except Exception as e:
            return {'execution_time': 0, 'error': str(e)}
        finally:
            conn.close()

    def run_complete_optimization(self):
        """Запускает полную оптимизацию"""
        print("🔧 ЗАПУСК ПОЛНОЙ ОПТИМИЗАЦИИ OLAP НА МАССИВНЫХ ДАННЫХ")
        print("=" * 70)

        # 1. Создаем МАССИВНЫЙ объем данных
        self.create_massive_test_data()

        # 2. Создаем оптимизированные индексы
        self.create_optimized_indexes()

        # 3. Создаем материализованные представления
        self.create_materialized_views()

        print("\n✅ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА НА МАССИВНЫХ ДАННЫХ!")


def test_massive_queries():
    """Тестирование оптимизированных запросов на МАССИВНЫХ данных"""
    optimizer = PostgresMassiveOLAPOptimizer({
        "host": "localhost",
        "database": "bank",
        "user": "postgres",
        "password": "1007"
    })

    print("\n📊 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННЫХ ЗАПРОСОВ НА МАССИВНЫХ ДАННЫХ")
    print("=" * 80)

    # ОРИГИНАЛЬНЫЕ ЗАПРОСЫ (очень медленные на больших данных)
    original_queries = [
        {
            'name': 'СЛОЖНАЯ АГРЕГАЦИЯ: Статистика клиентов с JOIN',
            'query': """
                SELECT 
                    c.client_id,
                    c.first_name || ' ' || c.last_name as client_name,
                    c.city,
                    c.income_level,
                    COUNT(DISTINCT a.account_id) as account_count,
                    SUM(a.balance) as total_balance,
                    COUNT(t.transaction_id) as transaction_count,
                    SUM(t.amount) as total_volume,
                    AVG(t.amount) as avg_amount
                FROM clients c
                LEFT JOIN accounts a ON c.client_id = a.client_id
                LEFT JOIN transactions t ON a.account_id = t.from_account_id
                WHERE c.registration_date >= '2022-01-01'
                GROUP BY c.client_id, client_name, c.city, c.income_level
                ORDER BY total_volume DESC
                LIMIT 1000
            """
        },
        {
            'name': 'АНАЛИТИКА: Ежемесячная статистика по типам транзакций',
            'query': """
                SELECT 
                    EXTRACT(YEAR FROM t.created_at) as year,
                    EXTRACT(MONTH FROM t.created_at) as month,
                    t.transaction_type,
                    t.category,
                    COUNT(*) as transaction_count,
                    SUM(t.amount) as monthly_volume,
                    AVG(t.amount) as avg_amount,
                    COUNT(DISTINCT t.from_account_id) as unique_accounts
                FROM transactions t
                WHERE t.created_at >= '2023-01-01'
                GROUP BY year, month, t.transaction_type, t.category
                ORDER BY year, month, monthly_volume DESC
            """
        },
        {
            'name': 'GEO-АНАЛИТИКА: Клиенты по городам с детальной статистикой',
            'query': """
                SELECT 
                    c.city,
                    c.income_level,
                    COUNT(DISTINCT c.client_id) as client_count,
                    COUNT(DISTINCT a.account_id) as account_count,
                    SUM(a.balance) as total_balance,
                    AVG(a.balance) as avg_balance,
                    COUNT(t.transaction_id) as transaction_count,
                    SUM(t.amount) as transaction_volume,
                    AVG(c.age) as avg_client_age
                FROM clients c
                LEFT JOIN accounts a ON c.client_id = a.client_id
                LEFT JOIN transactions t ON a.account_id = t.from_account_id
                WHERE c.registration_date >= '2021-01-01'
                GROUP BY c.city, c.income_level
                ORDER BY total_balance DESC
            """
        },
        {
            'name': 'ВРЕМЕННЫЕ РЯДЫ: Ежедневная активность за год',
            'query': """
                SELECT 
                    DATE(t.created_at) as transaction_date,
                    t.transaction_type,
                    COUNT(*) as transaction_count,
                    SUM(t.amount) as daily_volume,
                    AVG(t.amount) as avg_amount,
                    COUNT(DISTINCT t.from_account_id) as unique_accounts
                FROM transactions t
                WHERE t.created_at >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY DATE(t.created_at), t.transaction_type
                ORDER BY transaction_date DESC, daily_volume DESC
            """
        },
        {
            'name': 'БИЗНЕС-АНАЛИТИКА: Сегментация клиентов по активности',
            'query': """
                SELECT 
                    CASE 
                        WHEN COUNT(t.transaction_id) = 0 THEN 'Нет транзакций'
                        WHEN COUNT(t.transaction_id) < 10 THEN 'Низкая активность'
                        WHEN COUNT(t.transaction_id) < 50 THEN 'Средняя активность'
                        ELSE 'Высокая активность'
                    END as activity_segment,
                    c.income_level,
                    COUNT(DISTINCT c.client_id) as client_count,
                    AVG(a.balance) as avg_balance,
                    SUM(t.amount) as total_volume,
                    AVG(t.amount) as avg_transaction_amount
                FROM clients c
                LEFT JOIN accounts a ON c.client_id = a.client_id
                LEFT JOIN transactions t ON a.account_id = t.from_account_id
                WHERE c.registration_date >= '2020-01-01'
                GROUP BY activity_segment, c.income_level
                ORDER BY activity_segment, client_count DESC
            """
        }
    ]

    # ОПТИМИЗИРОВАННЫЕ ЗАПРОСЫ (используют материализованные представления)
    optimized_queries = [
        {
            'name': 'СЛОЖНАЯ АГРЕГАЦИЯ (оптимизированная)',
            'query': """
                SELECT 
                    client_id,
                    client_name,
                    city,
                    income_level,
                    account_count,
                    total_balance,
                    transaction_count,
                    total_volume,
                    avg_transaction_amount
                FROM mv_client_stats
                WHERE registration_date >= '2022-01-01'
                ORDER BY total_volume DESC
                LIMIT 1000
            """
        },
        {
            'name': 'АНАЛИТИКА (оптимизированная)',
            'query': """
                SELECT 
                    year,
                    month,
                    income_level,
                    city,
                    transaction_type,
                    category,
                    transaction_count,
                    monthly_volume,
                    avg_amount,
                    unique_clients
                FROM mv_monthly_analytics
                WHERE year >= 2023
                ORDER BY year, month, monthly_volume DESC
            """
        },
        {
            'name': 'GEO-АНАЛИТИКА (оптимизированная)',
            'query': """
                SELECT 
                    city,
                    income_level,
                    client_count,
                    account_count,
                    total_balance,
                    avg_balance,
                    transaction_count,
                    transaction_volume,
                    avg_client_age
                FROM mv_city_stats
                WHERE city IN (SELECT DISTINCT city FROM clients WHERE registration_date >= '2021-01-01')
                ORDER BY total_balance DESC
            """
        },
        {
            'name': 'ВРЕМЕННЫЕ РЯДЫ (оптимизированная)',
            'query': """
                SELECT 
                    transaction_date,
                    transaction_type,
                    transaction_count,
                    daily_volume,
                    avg_amount,
                    unique_accounts
                FROM mv_daily_transactions
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '1 year'
                ORDER BY transaction_date DESC, daily_volume DESC
            """
        },
        {
            'name': 'БИЗНЕС-АНАЛИТИКА (оптимизированная)',
            'query': """
                SELECT 
                    CASE 
                        WHEN transaction_count = 0 THEN 'Нет транзакций'
                        WHEN transaction_count < 10 THEN 'Низкая активность'
                        WHEN transaction_count < 50 THEN 'Средняя активность'
                        ELSE 'Высокая активность'
                    END as activity_segment,
                    income_level,
                    COUNT(*) as client_count,
                    AVG(total_balance) as avg_balance,
                    SUM(total_volume) as total_volume,
                    AVG(avg_transaction_amount) as avg_transaction_amount
                FROM mv_client_stats
                WHERE registration_date >= '2020-01-01'
                GROUP BY activity_segment, income_level
                ORDER BY activity_segment, client_count DESC
            """
        }
    ]

    results = []

    for i in range(len(original_queries)):
        orig = original_queries[i]
        opt = optimized_queries[i]

        print(f"\n{i+1}. {orig['name']}")
        print("-" * 70)

        # Тестируем оригинальный запрос
        print("   Тестируем оригинальный запрос...")
        orig_result = optimizer.analyze_query(orig['query'], iterations=2)
        orig_time = orig_result['execution_time']

        # Тестируем оптимизированный запрос
        print("   Тестируем оптимизированный запрос...")
        opt_result = optimizer.analyze_query(opt['query'], iterations=2)
        opt_time = opt_result['execution_time']

        if 'error' in orig_result:
            print(f"   ❌ Ошибка в оригинальном запросе: {orig_result['error'][:100]}...")
            continue
            
        if 'error' in opt_result:
            print(f"   ❌ Ошибка в оптимизированном запросе: {opt_result['error'][:100]}...")
            continue

        print(f"   Оригинальный: {orig_time:.3f}s")
        print(f"   Оптимизированный: {opt_time:.3f}s")

        if orig_time > 0 and opt_time > 0:
            improvement = ((orig_time - opt_time) / orig_time) * 100
            speedup = orig_time / opt_time if opt_time > 0 else 0
            print(f"   🚀 Ускорение: {speedup:.1f}x ({improvement:+.1f}%)")
            results.append(speedup)

    # Сводка результатов
    if results:
        avg_speedup = sum(results) / len(results)
        max_speedup = max(results)
        min_speedup = min(results)
        
        print(f"\n🎯 ИТОГОВАЯ СВОДКА НА МАССИВНЫХ ДАННЫХ:")
        print(f"   Среднее ускорение: {avg_speedup:.1f}x")
        print(f"   Максимальное ускорение: {max_speedup:.1f}x") 
        print(f"   Минимальное ускорение: {min_speedup:.1f}x")
        print(f"   Успешных тестов: {len(results)} из {len(original_queries)}")
        
        if avg_speedup > 50:
            print(f"   💪 ФЕНОМЕНАЛЬНЫЙ РЕЗУЛЬТАТ! Оптимизация невероятно эффективна!")
        elif avg_speedup > 20:
            print(f"   🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Оптимизация работает превосходно!")
        elif avg_speedup > 10:
            print(f"   👍 ОЧЕНЬ ХОРОШО! Значительное улучшение производительности!")
        else:
            print(f"   ⚠️  УМЕРЕННЫЙ РЕЗУЛЬТАТ! Эффект есть, но можно улучшить!")

        # Показываем размеры данных
        conn = psycopg2.connect(host="localhost", database="bank", user="postgres", password="1007")
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM clients")
        clients_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM accounts")
        accounts_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM transactions")
        transactions_count = cur.fetchone()[0]
        
        conn.close()
        
        print(f"\n📊 РАЗМЕРЫ ТЕСТОВЫХ ДАННЫХ:")
        print(f"   Клиенты: {clients_count:,}")
        print(f"   Счета: {accounts_count:,}")
        print(f"   Транзакции: {transactions_count:,}")
        print(f"   Общий объем: {clients_count + accounts_count + transactions_count:,} записей")


if __name__ == "__main__":
    optimizer = PostgresMassiveOLAPOptimizer({
        "host": "localhost",
        "database": "bank",
        "user": "postgres",
        "password": "1007"
    })

    # Запускаем полную оптимизацию на МАССИВНЫХ данных
    optimizer.run_complete_optimization()

    # Тестируем оптимизированные запросы на МАССИВНЫХ данных
    test_massive_queries()