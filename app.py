from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# -------------------- DRIVER SETUP --------------------
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------- UTILITY --------------------
def parse_price(price_str):
    try:
        clean = price_str.replace("₹","").replace(",","").replace(" ","").replace("Rs.","").strip()
        return float(clean)
    except:
        return float('inf')

# -------------------- AMAZON SCRAPER --------------------
def scrape_amazon(product_name):
    driver = get_driver()
    results = []
    try:
        url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
        driver.get(url)
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        )
        products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")[:5]
        for p in products:
            try: name = p.find_element(By.TAG_NAME, "h2").text
            except: continue
            try: price = p.find_element(By.CLASS_NAME, "a-price-whole").text
            except: price = "0"
            try: link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
            except: link = ""
            try: img = p.find_element(By.TAG_NAME, "img").get_attribute("src")
            except: img = ""
            results.append({"Website": "Amazon", "Product": name, "Price": price, "Link": link, "Image": img})
    except Exception as e:
        print("Amazon Error:", e)
    finally:
        driver.quit()
    return results

# -------------------- FLIPKART SCRAPER --------------------
def scrape_flipkart(product_name):
    driver = get_driver()
    results = []
    try:
        url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}"
        driver.get(url)
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
            )
            close_btn.click()
        except: pass
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._75nlfW, div._1AtVbE"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, "div._75nlfW")
        if not products:
            products = driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")
        for p in products[:5]:
            try:
                try: name = p.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text
                except: name = p.find_element(By.CSS_SELECTOR, "div._4rR01T").text
                try: price = p.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text
                except: price = p.find_element(By.CSS_SELECTOR, "div._30jeq3").text
                link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
                try: img = p.find_element(By.TAG_NAME, "img").get_attribute("src")
                except: img = ""
                price = price.replace("₹","").replace(",","").replace("Rs.","").strip()
                results.append({"Website": "Flipkart", "Product": name, "Price": price, "Link": link, "Image": img})
            except: continue
    except Exception as e:
        print("Flipkart Error:", e)
    finally:
        driver.quit()
    return results

# -------------------- MYNTRA SCRAPER --------------------
def scrape_myntra(product_name):
    driver = get_driver()
    results = []
    try:
        url = f"https://www.myntra.com/{product_name.replace(' ', '-')}"
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.product-base"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, "li.product-base")[:5]
        for p in products:
            try:
                brand = p.find_element(By.CSS_SELECTOR, "h3.product-brand").text
                item = p.find_element(By.CSS_SELECTOR, "h4.product-product").text
                name = f"{brand} {item}"
            except:
                continue
            price = "0"
            try:
                price = p.find_element(By.CSS_SELECTOR, "span.product-discountedPrice").text
            except:
                try:
                    price = p.find_element(By.CSS_SELECTOR, "span.product-price").text
                except:
                    price = "0"
            try: link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
            except: link = ""
            try: img = p.find_element(By.TAG_NAME, "img").get_attribute("src")
            except: img = ""
            price = price.replace("₹","").replace(",","").replace("Rs.","").strip()
            results.append({"Website": "Myntra", "Product": name, "Price": price, "Link": link, "Image": img})
    except Exception as e:
        print("Myntra Error:", e)
    finally:
        driver.quit()
    return results

# -------------------- SNAPDEAL SCRAPER --------------------
def scrape_snapdeal(product_name):
    driver = get_driver()
    results = []
    try:
        url = f"https://www.snapdeal.com/search?keyword={product_name.replace(' ','%20')}"
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-tuple-listing"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")[:5]
        for p in products:
            try: name = p.find_element(By.CSS_SELECTOR, "p.product-title").text
            except: name = "N/A"
            try: price = p.find_element(By.CSS_SELECTOR, "span.lfloat.product-price").text.replace("₹","").replace(",","")
            except: price = "0"
            try: link = p.find_element(By.TAG_NAME,"a").get_attribute("href")
            except: link = ""
            try: img = p.find_element(By.TAG_NAME,"img").get_attribute("src")
            except: img = ""
            price = price.replace("₹","").replace(",","").replace("Rs.","").strip()
            results.append({"Website":"Snapdeal","Product":name,"Price":price,"Link":link,"Image":img})
    except Exception as e:
        print("Snapdeal Error:", e)
    finally:
        driver.quit()
    return results

# -------------------- AJIO SCRAPER --------------------
def scrape_ajio(product_name):
    driver = get_driver()
    results = []
    try:
        url = f"https://www.ajio.com/search/?text={product_name.replace(' ','%20')}"
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.aitem, div.item"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, "div.aitem, div.item")[:5]
        for p in products:
            try: brand = p.find_element(By.CSS_SELECTOR,"div.brand").text
            except: brand = ""
            try: name_text = p.find_element(By.CSS_SELECTOR,"div.name").text
            except: name_text = ""
            full_name = (brand + " " + name_text).strip() or "N/A"
            try: price = p.find_element(By.CSS_SELECTOR,"span.price, div.price").text
            except: price = "0"
            try: link = p.find_element(By.TAG_NAME,"a").get_attribute("href")
            except: link = ""
            try: img = p.find_element(By.TAG_NAME,"img").get_attribute("src")
            except: img = ""
            price = price.replace("₹","").replace(",","").replace("Rs.","").strip()
            results.append({"Website":"Ajio","Product":full_name,"Price":price,"Link":link,"Image":img})
    except Exception as e:
        print("Ajio Error:", e)
    finally:
        driver.quit()
    return results

# -------------------- FLASK ROUTE --------------------
@app.route('/', methods=['GET','POST'])
def index():
    results = []
    best_deals_by_site = {}
    overall_best_deal = None

    if request.method == 'POST':
        product = request.form.get('product')
        amazon_res = scrape_amazon(product)
        flipkart_res = scrape_flipkart(product)
        myntra_res = scrape_myntra(product)
        snapdeal_res = scrape_snapdeal(product)
        ajio_res = scrape_ajio(product)
        results = amazon_res + flipkart_res + myntra_res + snapdeal_res + ajio_res

        websites = ['Amazon','Flipkart','Myntra','Snapdeal','Ajio']
        final_results = []
        for site in websites:
            site_items = [i for i in results if i['Website']==site]
            site_items.sort(key=lambda x: parse_price(x["Price"]))
            final_results.extend(site_items[:5])
        results = final_results

        for item in results:
            site = item["Website"]
            price_val = parse_price(item["Price"])
            if site not in best_deals_by_site or price_val < parse_price(best_deals_by_site[site]["Price"]):
                best_deals_by_site[site] = item

        if results:
            overall_best_deal = min(results, key=lambda x: parse_price(x["Price"]))

    return render_template('index.html', results=results, best_deals_by_site=best_deals_by_site, overall_best_deal=overall_best_deal)

if __name__=="__main__":
    app.run(debug=True)
