from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


url_list = ["https://www.amazon.com/GIGABYTE-GeForce-WINDFORCE-Graphics-GV-N5070WF3OC-12GD/dp/B0DTQMLX4F/ref=sr_1_1?crid=2MUUBE8GLTBBN&dib=eyJ2IjoiMSJ9.FG3VxBsny1zXGlw-UW5EUpWh_u02HudejmbrWOOeumnI-wmdxdDtosLJ4jlgRgz4A76V2yPXesKtr_GczTkIQ3Z3KHragv-fjMZwt2GKx6JDWoqx6p9OzhhgJzciBgfeZc2tft4jZG0kkMGJ-Dw5Oj_NAxbjRzkRHTwrw10MzljC5fXUt3otG8bCNWx1kU24T5eZg4bjWE9DnM8AwQLCwweqxJorGqSh5UmboXmYZK0.mKhsM9QYM_hnrsnEPpVXhtS6TxAJi45pHHAzLCyvClY&dib_tag=se&keywords=rtx%2B5070&qid=1775217841&sprefix=rtx%2Caps%2C254&sr=8-1&th=1",
            "https://www.amazon.com/PNY-Overclocked-Graphics-2-4-Slot-Epic-XTM/dp/B0DYPGBX6J/ref=sims_dp_d_dex_ai_rank_model_1_d_v1_d_sccl_1_1/135-9892342-9905632?pd_rd_w=iD1nN&content-id=amzn1.sym.bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_p=bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_r=QJTQTZP9M9Y39MNMN9ZX&pd_rd_wg=BFrhG&pd_rd_r=4daea938-0807-4877-ac90-9cc22e00244b&pd_rd_i=B0DYPGBX6J&th=1",
            "https://www.amazon.com/ASUS-SFF-Ready-Graphics-2-5-Slot-Axial-tech/dp/B0DS6WPTLL/ref=sims_dp_d_dex_ai_rank_model_1_d_v1_d_sccl_1_4/135-9892342-9905632?pd_rd_w=iD1nN&content-id=amzn1.sym.bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_p=bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_r=QJTQTZP9M9Y39MNMN9ZX&pd_rd_wg=BFrhG&pd_rd_r=4daea938-0807-4877-ac90-9cc22e00244b&pd_rd_i=B0DS6WPTLL&th=1",
            "https://www.amazon.com/GIGABYTE-GeForce-WINDFORCE-Graphics-GV-N5060WF2OC-8GD/dp/B0F8LDHQ7Y/ref=sims_dp_d_dex_ai_rank_model_1_d_v1_d_sccl_1_6/135-9892342-9905632?pd_rd_w=iD1nN&content-id=amzn1.sym.bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_p=bb4a0aac-c2b4-4b4b-a0c8-9aa89b28dce3&pf_rd_r=QJTQTZP9M9Y39MNMN9ZX&pd_rd_wg=BFrhG&pd_rd_r=4daea938-0807-4877-ac90-9cc22e00244b&pd_rd_i=B0F8LDHQ7Y&th=1"]


def get_amazon_price(url):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options = options)

    driver.get(url)
    total = 0
    try:
        value_integer = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "a-price-whole"))).text.replace(",", "")
        value_integer = float(value_integer)
        value_float = float(driver.find_element(By.CLASS_NAME, "a-price-fraction").text) / 100
        total = value_integer + value_float

        title = driver.find_element(By.ID, "productTitle").text.strip()


    except:
        return None, None

    finally:
        driver.quit()

    return title, total

load_dotenv()

db_host = os.getenv("db_host_url")
db_name = os.getenv("db_name_key")
db_user = os.getenv("db_user_key")
db_pass = os.getenv("db_pass_key")

db_conn = psycopg2.connect(host = db_host, database = db_name, user = db_user, password = db_pass)

c = db_conn.cursor()
engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}")

c.execute("""CREATE TABLE IF NOT EXISTS profiles (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL)""")

c.execute("""CREATE TABLE IF NOT EXISTS prices (
            id SERIAL PRIMARY KEY,
            profile_id INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE)""")

def insert_db(name, url, price):
    with db_conn:
        c.execute("INSERT INTO profiles (url, name) VALUES (%s, %s) ON CONFLICT (url) DO NOTHING", (url, name))
        c.execute("SELECT id FROM profiles WHERE url = %s", (url,))
        profile_id = c.fetchone()[0]
        c.execute("""INSERT INTO prices (profile_id, price) VALUES (%s, %s)""", (profile_id, price))

def plot():
    with db_conn:
        plt.figure(figsize=(10, 6))

        df = pd.read_sql_query("""SELECT pr.profile_id, p.name, pr.price, pr.timestamp
                                      FROM prices pr
                                      JOIN profiles p on pr.profile_id = p.id""", engine)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['short_name'] = df['name'].str.split(',').str[0]
        for name, group in df.groupby('short_name'):
            plt.plot(group['timestamp'], group['price'], marker='.', label=name)

        plt.title('Prices over time')
        plt.xlabel('Time')
        plt.ylabel('Price')

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.xticks(rotation=30)

        plt.show()


def insert_product(url):
    name, price = get_amazon_price(url)
    if name and price:
        return name, url, price
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
    thread_results = list(executor.map(insert_product, url_list))

    for results in thread_results:
        if results:
            insert_db(results[0], results[1], results[2])


plot()

c.close()

input("Press any key to exit.")
