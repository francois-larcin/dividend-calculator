"""
DB initialization script
Executes schema.sql to create tables and insert test data
"""
import psycopg2


def init_database():
    """Initialize database with schema.sql"""
    print("Initializating database...")
    
    conn = psycopg2.connect(
        host="localhost", 
        database="dividend_db",
        user="postgres" ,
        password="postgres"
    )
    
    cursor = conn.cursor()
    
    
    with open('database/schema.sql', 'r') as f:
        sql_content = f.read()
        cursor.execute(sql_content)
        conn.commit()
        
    print("Database initialized successfully!")
    
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
                    """)
    tables = cursor.fetchall()
    print(f"Tables created : {[t[0] for t in tables]}")
    
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f"Test users created: {user_count}")
        
    cursor.close()
    conn.close()
    
if __name__=="__main__":
    init_database()
    
    
        