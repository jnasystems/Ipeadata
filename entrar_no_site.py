from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Usa o webdriver-manager para baixar o ChromeDriver compatível
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

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
