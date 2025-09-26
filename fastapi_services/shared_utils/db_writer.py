import psycopg2

def test_db_writer():
    conn = psycopg2.connect(
        host="localhost",
        dbname="wwu_degree_works",
        user="admin",
        password="test",
        port="5432"
    )

    cursor = conn.cursor()

    name = "John Doe"
    website = "https://www.john-doe.com"
    research_interest = "Research Interest 1, Research Interest 2"
    src_url = "https://www.john-doe.com"

    cursor.execute("CREATE TABLE IF NOT EXISTS research (id SERIAL PRIMARY KEY, name VARCHAR(255), website VARCHAR(255), research_interest VARCHAR(255), src_url VARCHAR(255))")
    cursor.execute("INSERT INTO research (name, website, research_interest, src_url) VALUES (%s, %s, %s, %s)", (name, website, research_interest, src_url))
    conn.commit()
    cursor.close()
    conn.close()

def write_to_db(data):
    conn = psycopg2.connect(
        host="localhost",
        dbname="wwu_degree_works",
        user="admin",
        password="test",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS research (id SERIAL PRIMARY KEY, name VARCHAR(255), website VARCHAR(255), research_interest VARCHAR(500), src_url VARCHAR(255))")
    for item in data:
        cursor.execute("INSERT INTO research (name, website, research_interest, src_url) VALUES (%s, %s, %s, %s)", (item["name"], item["website"], item["research_interest"], item["src_url"]))
    conn.commit()
    cursor.close()
    conn.close()

def read_from_db():
    conn = psycopg2.connect(
        host="localhost",
        dbname="wwu_degree_works",
        user="admin",
        password="test",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM public.research")
    table = cursor.fetchall()
    print(table)
    return table

if __name__ == "__main__":
    read_from_db()