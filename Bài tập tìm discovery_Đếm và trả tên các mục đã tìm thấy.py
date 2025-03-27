from appium import webdriver 
from appium.options.android import UiAutomator2Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Cấu hình Appium
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "R58W41PDE1M"
options.app_package = "ht.nct"
options.app_activity = "ht.nct.ui.activity.splash.SplashActivity"
options.automation_name = "UiAutomator2"
options.no_reset = True  # Giữ trạng thái ứng dụng giữa các lần chạy

driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 5)

# Lưu danh sách playlist
playlist_positions = {}
found_playlists = set()
not_found_playlists = set()

def swipe(direction="left"):
    """Vuốt theo hướng chỉ định trong GridView."""
    grid_view = driver.find_element(By.ID, "ht.nct:id/recycler_view")
    grid_location = grid_view.location
    grid_size = grid_view.size
    
    start_x = grid_location["x"] + (grid_size["width"] * (0.8 if direction == "left" else 0.2))
    end_x = grid_location["x"] + (grid_size["width"] * (0.2 if direction == "left" else 0.8))
    y = grid_location["y"] + grid_size["height"] / 2
    
    driver.swipe(start_x, y, end_x, y, 800)
    print(f"✅ Swiped {direction} on GridView!")

def get_visible_playlists():
    """Trả về danh sách playlist đang hiển thị trên màn hình."""
    return {el.text.strip(): el for el in driver.find_elements(By.XPATH, "//*[@resource-id='ht.nct:id/name']") if el.text.strip()}

def collect_playlist_positions():
    """Thu thập danh sách playlist bằng cách vuốt qua toàn bộ GridView."""
    global playlist_positions
    seen_items = {}
    swipe_count = 0
    max_swipe = 6  # Giới hạn số lần vuốt

    while swipe_count < max_swipe:
        visible_playlists = get_visible_playlists()
        print(f"🔍 Playlists at swipe index {swipe_count}: {list(visible_playlists.keys())}")

        for name, element in visible_playlists.items():
            if name not in seen_items:
                seen_items[name] = swipe_count  # Ghi lại swipe index chính xác
            else:
                # Nếu một playlist xuất hiện ở swipe index khác, cập nhật lại vị trí đúng
                prev_index = seen_items[name]
                if swipe_count < prev_index:
                    seen_items[name] = swipe_count

        if not visible_playlists:  # Nếu không tìm thấy item mới, dừng lại
            break
        
        swipe("left")
        time.sleep(1)
        swipe_count += 1

    # Lưu lại danh sách chính xác
    playlist_positions = seen_items
    print(f"🔍 Final collected playlists: {playlist_positions}")

def go_to_playlist(playlist_name):
    """Tìm và mở playlist dựa trên vị trí đã lưu."""
    if playlist_name in playlist_positions:
        target_swipe_count = playlist_positions[playlist_name]
        print(f"🔄 Moving to {playlist_name} at swipe index {target_swipe_count}")

        # Kiểm tra danh sách hiện tại trước khi vuốt
        visible_playlists = get_visible_playlists()
        if playlist_name in visible_playlists:
            print(f"✅ Found {playlist_name}, clicking...")
            visible_playlists[playlist_name].click()
            found_playlists.add(playlist_name)
            return True

        # Nếu playlist cần tìm ở đầu danh sách, vuốt phải thay vì vuốt trái
        current_swipe = 0
        if target_swipe_count == 0:
            while current_swipe < 3:
                swipe("right")
                time.sleep(1)
                visible_playlists = get_visible_playlists()
                if playlist_name in visible_playlists:
                    print(f"✅ Found {playlist_name}, clicking...")
                    visible_playlists[playlist_name].click()
                    found_playlists.add(playlist_name)
                    return True
                current_swipe += 1

        # Vuốt sang trái nếu cần
        for _ in range(target_swipe_count):
            swipe("left")
            time.sleep(1)

        # Kiểm tra lại sau khi vuốt
        visible_playlists = get_visible_playlists()
        if playlist_name in visible_playlists:
            print(f"✅ Found {playlist_name}, clicking...")
            visible_playlists[playlist_name].click()
            found_playlists.add(playlist_name)
            return True

        print(f"⚠️ {playlist_name} not found after swiping.")
        not_found_playlists.add(playlist_name)
        return False

    print(f"⚠️ Playlist {playlist_name} not in saved positions.")
    not_found_playlists.add(playlist_name)
    return False

try:
    print("✅ Successfully connected to Appium!")

    # Click vào 'tvHome'
    tv_home = wait.until(EC.element_to_be_clickable((By.ID, "ht.nct:id/tvHome")))
    tv_home.click()
    print("✅ Clicked on 'tvHome' successfully!")

    # Chờ GridView xuất hiện
    wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/recycler_view")))
    print("✅ GridView found!")

    # Thu thập vị trí playlist
    collect_playlist_positions()
    
    print(f"🔍 Total playlists found: {len(playlist_positions)}")
    for idx, (name, pos) in enumerate(playlist_positions.items()):
        print(f"{idx}. {name} - Swipe index: {pos}")

    # Kiểm tra danh sách đang hiển thị
    visible_playlists = get_visible_playlists()

    # Mở các playlist có sẵn trên màn hình
    for playlist in visible_playlists.keys():
        print(f"🎯 Checking playlist: {playlist}")
        visible_playlists[playlist].click()
        time.sleep(2)

        try:
            playlist_title = wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/tvTitle"))).text.strip()
            print(f"✅ Verified playlist title: {playlist_title}")
            found_playlists.add(playlist)
        except:
            print(f"⚠️ Could not verify title for {playlist}")

        driver.back()
        time.sleep(2)

    # Vuốt để tìm các playlist còn lại
    for playlist in playlist_positions.keys():
        if playlist not in found_playlists:
            print(f"🎯 Searching for playlist: {playlist}")

            if go_to_playlist(playlist):
                try:
                    playlist_title = wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/tvTitle"))).text.strip()
                    print(f"✅ Verified playlist title: {playlist_title}")
                except:
                    print(f"⚠️ Could not verify title for {playlist}")

                driver.back()
                time.sleep(2)

except Exception as e:
    print(f"❌ Error: {str(e)}")

finally:
    print("\n🔹 **Summary of Results:**")
    print(f"✅ Found playlists ({len(found_playlists)}): {sorted(found_playlists)}")
    print(f"⚠️ Not found playlists ({len(not_found_playlists)}): {sorted(not_found_playlists)}")
    
    driver.quit()
    print("✅ Appium session closed.")
