from appium import webdriver 
from appium.options.android import UiAutomator2Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "RFCW919N6BL"
options.app_package = "ht.nct"
options.app_activity = "ht.nct.ui.activity.splash.SplashActivity"
options.automation_name = "UiAutomator2"
options.no_reset = True  # Không reset app khi chạy lại

driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 5)

try:
    print("✅ Kết nối Appium thành công!")

    # Click vào 'tvHome'
    tv_home = wait.until(EC.element_to_be_clickable((By.ID, "ht.nct:id/tvHome")))
    tv_home.click()
    print("✅ Đã bấm vào 'tvHome' thành công!")

    # Chờ GridView hiển thị
    grid_view = wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/recycler_view")))
    print("✅ Tìm thấy GridView!")

    # Tìm kiếm mục "Chủ Đề"
    try:
        chu_de = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='android.widget.TextView' and @text='Chủ Đề']")))
        print("✅ Tìm thấy mục:", chu_de.text)
    except:
        print("⚠️ Không tìm thấy mục 'Chủ Đề'")

    # Tìm kiếm mục "BXH"
    try:
        bxh = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='android.widget.TextView' and @text='BXH']")))
        print("✅ Tìm thấy mục:", bxh.text)
    except:
        print("⚠️ Không tìm thấy mục 'BXH'")

    def swipe_left():
        driver.swipe(900, 652, 180, 652, 800)
        print("✅ Vuốt sang trái!")

    def get_grid_items():
        elements = driver.find_elements(By.XPATH, "//*[@resource-id='ht.nct:id/name']")
        return {el.text for el in elements if el.text}

    found_items = set()

    # Thêm "Chủ Đề" & "BXH" nếu đã tìm thấy
    if 'chu_de' in locals():
        found_items.add(chu_de.text)
    if 'bxh' in locals():
        found_items.add(bxh.text)

    max_swipes = 6

    for _ in range(max_swipes):
        new_items = get_grid_items()
        if new_items.issubset(found_items):
            print("✅ Không có mục mới, dừng vuốt.")
            break
        found_items.update(new_items)
        swipe_left()

    print(f"🔍 Tổng số mục tìm thấy: {len(found_items)}")
    for item in found_items:
        print(f"- {item}")

except Exception as e:
    print(f"❌ Lỗi: {str(e)}")

finally:
    driver.quit()
    print("✅ Đã đóng phiên Appium.")
