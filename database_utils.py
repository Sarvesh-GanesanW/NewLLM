import psycopg2

db_name = 'gzeksmetrics'
db_user = 'eks_metrics_user'
db_password = 'eks_123_metrics'
db_host = 'groundzero-infra-gzdev-gzdbinstance-vuowh8jmbfxa.c279y5qd65ct.ap-south-1.rds.amazonaws.com'

def get_db_connection():
    return psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host
    )

def create_conversations_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            conversation_name VARCHAR(255) DEFAULT 'New Chat',
            s3_file_location TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_conversation_metadata(conversation_id, user_id, s3_file_location, conversation_name='New Chat'):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
            INSERT INTO conversations (conversation_id, user_id, s3_file_location, conversation_name)
            VALUES (%s, %s, %s, %s)
        """, (conversation_id, user_id, s3_file_location, conversation_name))
    conn.commit()
    cur.close()
    conn.close()

def get_conversation_metadata(conversation_id):

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT conversation_id, user_id, s3_file_location, conversation_name
        FROM conversations 
        WHERE conversation_id = %s
    """, (conversation_id,))
    
    row = cur.fetchone()
    cur.close() 
    conn.close()
    
    if row:
        metadata = {
            "conversation_id": row[0],
            "user_id": row[1],
            "s3_file_location": row[2],
            "conversation_name": row[3] 
        }
    else:
        metadata = None
    
    return metadata
