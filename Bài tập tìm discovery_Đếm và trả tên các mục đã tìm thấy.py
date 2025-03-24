from appium import webdriver 
from appium.options.android import UiAutomator2Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Cấu hình Appium
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "RFCW919N6BL"
options.app_package = "ht.nct"
options.app_activity = "ht.nct.ui.activity.splash.SplashActivity"
options.automation_name = "UiAutomator2"
options.no_reset = True  # Giữ trạng thái ứng dụng giữa các lần chạy

driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 5)

def swipe(direction="left"):
    """Vuốt trong GridView theo hướng chỉ định."""
    grid_view = driver.find_element(By.ID, "ht.nct:id/recycler_view")
    grid_location = grid_view.location
    grid_size = grid_view.size
    
    start_x = grid_location["x"] + (grid_size["width"] * (0.8 if direction == "left" else 0.2))
    end_x = grid_location["x"] + (grid_size["width"] * (0.2 if direction == "left" else 0.8))
    y = grid_location["y"] + grid_size["height"] / 2
    
    driver.swipe(start_x, y, end_x, y, 800)
    print(f"✅ Swiped {direction} on GridView!")

def get_playlist_items():
    """Lấy danh sách playlist chính xác theo từng màn hình và cập nhật sau mỗi lần vuốt."""
    playlist_names = []
    seen_items = set()

    while True:
        elements = driver.find_elements(By.XPATH, "//*[@resource-id='ht.nct:id/name']")
        new_items = [el.text.strip() for el in elements if el.text.strip() and el.text.strip() not in seen_items]
        
        if not new_items:
            print("✅ No new items found, stopping swipe.")
            break
        
        playlist_names.extend(new_items)
        seen_items.update(new_items)
        
        swipe("left")
        time.sleep(1)
    
    return playlist_names

try:
    print("✅ Successfully connected to Appium!")

    # Click vào 'tvHome'
    tv_home = wait.until(EC.element_to_be_clickable((By.ID, "ht.nct:id/tvHome")))
    tv_home.click()
    print("✅ Clicked on 'tvHome' successfully!")

    # Chờ GridView xuất hiện
    wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/recycler_view")))
    print("✅ GridView found!")

    # Lấy danh sách playlist động
    playlist_names = get_playlist_items()
    print(f"🔍 Total playlists found: {len(playlist_names)}")
    for idx, item in enumerate(playlist_names):
        print(f"{idx}. {item}")

    # Duyệt playlist theo tên thay vì chỉ dựa vào thứ tự
    for playlist in playlist_names:
        print(f"🎯 Searching for playlist: {playlist}")

        try:
            elements = driver.find_elements(By.XPATH, "//*[@resource-id='ht.nct:id/name']")
            target_element = None
            
            for el in elements:
                if el.text.strip() == playlist:
                    target_element = el
                    break
            
            if not target_element:
                print(f"⚠️ Playlist '{playlist}' not found!")
                continue
            
            target_element.click()
            print(f"✅ Opened: {playlist}")

            # Xác minh tiêu đề playlist
            try:
                playlist_title = wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/tvTitle"))).text.strip()
                if playlist in playlist_title or playlist_title in playlist:
                    print(f"✅ Verified playlist title: {playlist_title}")
                else:
                    print(f"⚠️ Potential title update detected: Expected '{playlist}', but found '{playlist_title}'")
            except:
                print(f"⚠️ Could not verify title for {playlist}")

            # Nhấn back để quay lại danh sách
            try:
                back_button = wait.until(EC.element_to_be_clickable((By.ID, "ht.nct:id/btnBack")))
                back_button.click()
                print("✅ Returned to playlist list.")
                time.sleep(2)
            except:
                print("⚠️ Could not find back button, using driver.back().")
                driver.back()
                time.sleep(2)
        except:
            print(f"⚠️ Playlist '{playlist}' not found!")

        # Cập nhật lại danh sách nếu vuốt
        if playlist_names.index(playlist) % 4 == 0 and playlist_names.index(playlist) != 0:
            swipe("right")
            time.sleep(1)

except Exception as e:
    print(f"❌ Error: {str(e)}")

finally:
    driver.quit()
    print("✅ Appium session closed.")