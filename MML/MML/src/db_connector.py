"""
Database Connector Module.
Connects directly to the live MySQL database 'insurance_fraud_db'
and extracts raw claim records into a pandas DataFrame.
All downstream cleaning, feature engineering, and model training
pull data EXCLUSIVELY from this MySQL database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
import pandas as pd
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, TABLE_NAME

def get_db_connection(as_dict=False):
    """Establish and return a connection to the live MySQL database."""
    cursorclass = pymysql.cursors.DictCursor if as_dict else pymysql.cursors.Cursor
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=cursorclass
    )
    return conn

def fetch_claims_from_db(limit=None):
    """
    Query and extract vehicle claim records directly from MySQL.
    
    Args:
        limit (int, optional): Maximum number of rows to retrieve. None for all rows.
        
    Returns:
        pd.DataFrame: DataFrame containing raw records from the database.
    """
    print(f"[*] Connecting to live MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}...")
    conn = get_db_connection(as_dict=False)
    try:
        sql = f"SELECT * FROM `{TABLE_NAME}`"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        
        print(f"[*] Executing query: {sql}")
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            
        print(f"[+] Successfully pulled {len(df)} records from MySQL table `{TABLE_NAME}`.")
        return df
    finally:
        conn.close()

def fetch_single_claim_by_id(policy_number: int):
    """
    Query a single claim by its primary key PolicyNumber from MySQL.
    Used for end-to-end prediction tracing (CO1).
    """
    conn = get_db_connection(as_dict=True)
    try:
        sql = f"SELECT * FROM `{TABLE_NAME}` WHERE `PolicyNumber` = %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, (policy_number,))
            record = cursor.fetchone()
        return record
    finally:
        conn.close()

if __name__ == "__main__":
    df_check = fetch_claims_from_db(limit=5)
    print("\nDatabase pull preview:")
    print(df_check[['PolicyNumber', 'Make', 'VehicleCategory', 'FraudFound_P', 'Deductible']])
    
    single = fetch_single_claim_by_id(1)
    print("\nSingle claim fetched by PolicyNumber=1:")
    print(f"Policy: {single['PolicyNumber']}, Make: {single['Make']}, Fraud: {single['FraudFound_P']}")
