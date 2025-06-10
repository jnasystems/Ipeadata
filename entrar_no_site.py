from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# Instala o ChromeDriver automaticamente
chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print("🌐 Acessando o site...")
    driver.get("https://dashboardipeadata.streamlit.app/")

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "root"))
    )
    print("✅ App carregado com sucesso.")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)

except Exception as e:
    print("❌ Erro ao carregar o dashboard:", type(e).__name__, str(e))

finally:
    driver.quit()
