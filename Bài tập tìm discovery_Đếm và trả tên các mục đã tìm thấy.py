from appium import webdriver 
from appium.options.android import UiAutomator2Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Appium configuration
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "R58W41PDE1M"
options.app_package = "ht.nct"
options.app_activity = "ht.nct.ui.activity.splash.SplashActivity"
options.automation_name = "UiAutomator2"
options.no_reset = True  # Keep app state between sessions

driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 5)

# Store playlist list
playlist_positions = {}
found_playlists = set()
not_found_playlists = set()

def swipe(direction="left"):
    """Swipe in the specified direction inside the GridView."""
    grid_view = driver.find_element(By.ID, "ht.nct:id/recycler_view")
    grid_location = grid_view.location
    grid_size = grid_view.size
    
    start_x = grid_location["x"] + (grid_size["width"] * (0.8 if direction == "left" else 0.2))
    end_x = grid_location["x"] + (grid_size["width"] * (0.2 if direction == "left" else 0.8))
    y = grid_location["y"] + grid_size["height"] / 2
    
    driver.swipe(start_x, y, end_x, y, 800)
    print(f"✅ Swiped {direction} on GridView!")

def get_visible_playlists():
    """Return a dictionary of visible playlists on the screen."""
    return {el.text.strip(): el for el in driver.find_elements(By.XPATH, "//*[@resource-id='ht.nct:id/name']") if el.text.strip()}

def collect_playlist_positions():
    """Collect all playlist names and their swipe positions across the GridView."""
    global playlist_positions
    seen_items = {}
    swipe_count = 0
    max_swipe = 6  # Limit number of swipes

    while swipe_count < max_swipe:
        visible_playlists = get_visible_playlists()
        print(f"🔍 Playlists at swipe index {swipe_count}: {list(visible_playlists.keys())}")

        for name, element in visible_playlists.items():
            if name not in seen_items:
                seen_items[name] = swipe_count  # Save the swipe index
            else:
                # If the playlist appears at a better swipe index, update it
                prev_index = seen_items[name]
                if swipe_count < prev_index:
                    seen_items[name] = swipe_count

        if not visible_playlists:  # No new items found, stop swiping
            break
        
        swipe("left")
        time.sleep(1)
        swipe_count += 1

    playlist_positions = seen_items
    print(f"🔍 Final collected playlists: {playlist_positions}")

def go_to_playlist(playlist_name):
    """Navigate to a specific playlist using its stored swipe position."""
    if playlist_name in playlist_positions:
        target_swipe_count = playlist_positions[playlist_name]
        print(f"🔄 Moving to {playlist_name} at swipe index {target_swipe_count}")

        # Check if playlist is already visible
        visible_playlists = get_visible_playlists()
        if playlist_name in visible_playlists:
            print(f"✅ Found {playlist_name}, clicking...")
            visible_playlists[playlist_name].click()
            found_playlists.add(playlist_name)
            return True

        # If it's at the beginning, swipe right instead
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

        # Swipe left the required number of times
        for _ in range(target_swipe_count):
            swipe("left")
            time.sleep(1)

        # Check again after swiping
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

    # Click on 'tvHome'
    tv_home = wait.until(EC.element_to_be_clickable((By.ID, "ht.nct:id/tvHome")))
    tv_home.click()
    print("✅ Clicked on 'tvHome' successfully!")

    # Wait for GridView to appear
    wait.until(EC.presence_of_element_located((By.ID, "ht.nct:id/recycler_view")))
    print("✅ GridView found!")

    # Collect playlist positions
    collect_playlist_positions()
    
    print(f"🔍 Total playlists found: {len(playlist_positions)}")
    for idx, (name, pos) in enumerate(playlist_positions.items()):
        print(f"{idx}. {name} - Swipe index: {pos}")

    # Check visible playlists
    visible_playlists = get_visible_playlists()

    # Open playlists currently visible on screen
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

    # Swipe to find the rest of the playlists
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
