import logging
from core.database import supabase

def check_orders_table():
    try:
        response = supabase.table("orders").select("*").limit(1).execute()
        print("Table 'orders' EXISTS.")
        print(response.data)
    except Exception as e:
        print("Error checking table 'orders':", e)
        
    try:
        # also check what columns 'conversations' has
        response = supabase.table("conversations").select("*").limit(1).execute()
        if response.data:
            print("Conversations columns:", response.data[0].keys())
        else:
            print("Conversations table is empty but exists.")
    except Exception as e:
        print("Error checking table 'conversations':", e)

if __name__ == "__main__":
    check_orders_table()
