import psycopg2

db_name = 'gzeksmetrics'
db_user = 'eks_metrics_user'
db_password = 'eks_123_metrics'
db_host = 'groundzero-infra-gzdev-gzdbinstance-vuowh8jmbfxa.c279y5qd65ct.ap-south-1.rds.amazonaws.com'

"""Gets a connection to the PostgreSQL database.

Returns a psycopg2 database connection to the database specified in 
the module constants.
"""
def get_db_connection():
    return psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host
    )

"""Creates the conversations table in the database if it does not already exist.

The conversations table stores metadata about conversations, including a unique ID, the ID of the user who initiated the conversation, the name of the conversation, and the S3 location where the conversation text is stored.

The table has columns for:

- conversation_id: The unique ID for the conversation (UUID type, primary key)
- user_id: The ID of the user who initiated the conversation (UUID type)  
- conversation_name: The name of the conversation (varchar(255), defaults to "New Chat")
- s3_file_location: The S3 location where the text of the conversation is stored (text type)
"""
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

"""Inserts a new conversation metadata record into the conversations table.

Arguments:
- conversation_id: The unique ID for the new conversation 
- user_id: The ID of the user who initiated the conversation
- s3_file_location: The S3 location where the conversation text is stored
- conversation_name: Optional name for the conversation, defaults to "New Chat"
"""
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

"""Gets metadata for a conversation from the database.

Arguments:
- conversation_id: The ID of the conversation to get metadata for  

Returns:
- metadata: A dictionary with metadata for the conversation, including:
  - conversation_id: The conversation ID
  - user_id: The ID of the user who initiated the conversation 
  - s3_file_location: The S3 location where the conversation text is stored
  - conversation_name: The name of the conversation
- None: If no conversation with the given ID exists
"""
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
