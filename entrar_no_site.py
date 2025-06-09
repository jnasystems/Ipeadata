from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    print("🌐 Acessando o site...")
    driver.get("https://dashboardipeadata.streamlit.app/")
    
    # Espera pela estrutura base do app
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "root"))
    )
    print("✅ App Streamlit carregado!")

    # Rola até o final para garantir renderização total
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("🔽 Página rolada até o final.")

    # Espera extra para garantir carregamento completo
    time.sleep(10)

except Exception as e:
    print("❌ Erro ao carregar o dashboard:", type(e).__name__, str(e))

finally:
    driver.quit()
