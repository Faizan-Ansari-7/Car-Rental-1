import psycopg2

def get_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            database="car_rental",
            user="postgres",
            password="",
            port="5432"
        )
    except Exception as e:
        print("Connection Error:", e)
        return None