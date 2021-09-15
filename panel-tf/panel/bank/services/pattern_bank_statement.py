
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



from datetime import timedelta, datetime

from startpage.models import Auth

SeleniumTimeout = 40

def DoDownload(driver, VypiskaIz, SchetName):
    NowDate = datetime.now()
    # ============== Логинюсь
    driver.get("https://online.moysklad.ru/")

    WebDriverWait(driver, SeleniumTimeout).until(
        EC.visibility_of_element_located((By.NAME, "j_username"))
    ).send_keys(Auth.get('moysklad')[0])
    driver.find_element_by_name("j_password").send_keys(Auth.get('moysklad')[1])

    WebDriverWait(driver, SeleniumTimeout).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Войти')]"))
    ).click()

    driver.get("https://online.moysklad.ru/app/#finance")

    Click = 'Импорт'
    Pechat = WebDriverWait(driver, SeleniumTimeout+100).until(
        EC.visibility_of_element_located((By.XPATH, "//span[@class='text' and text()='{}']".format(Click)))
    )
    Pechat.click()
    print(Click)

    Click = VypiskaIz
    MenuItem = WebDriverWait(driver, SeleniumTimeout).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@class='gwt-MenuItem' and text()='{}']".format(Click)))
    )
    MenuItem.click()
    print(Click)
    
    try:
        Scheta = WebDriverWait(driver, SeleniumTimeout).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='search-selector account-selector']/div/div"))
        )
        Scheta.click()
    except:
        # driver.save_screenshot(f"/home/admin/code/panel-tf/panel/bank/screenshots/{name_for_screenshots} (-1).png")
        pass
    Schet = WebDriverWait(driver, SeleniumTimeout).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@title='{}']".format(SchetName)))
    )
    Schet.click()
    print(SchetName)
    
    YesterdayDate = NowDate - timedelta(days=1)

    DateFields = driver.find_elements_by_xpath("//input[@class='gwt-TextBox gwt-DateBox']")
    DateFields[-2].clear()
    YesterdayDate = "{}.{}.{}".format(YesterdayDate.strftime("%d"), YesterdayDate.strftime("%m"), YesterdayDate.year)
    DateFields[-2].send_keys(YesterdayDate)
    print("C", YesterdayDate)

    DateFields[-1].clear()
    TodayDate = "{}.{}.{}".format(NowDate.strftime("%d"), NowDate.strftime("%m"), NowDate.year)
    DateFields[-1].send_keys(TodayDate)
    print("По", TodayDate)
    
    # driver.save_screenshot(f"/home/admin/code/panel-tf/panel/bank/screenshots/{name_for_screenshots} (0).png")
    
    Click = 'Импортировать выписку'
    MenuItem = WebDriverWait(driver, SeleniumTimeout).until(
        EC.visibility_of_element_located((By.XPATH, "//span[@class='text' and text()='{}']".format(Click)))
    )
    MenuItem.click()
    print(Click)
    
    # driver.save_screenshot(f"/home/admin/code/panel-tf/panel/bank/screenshots/{name_for_screenshots} (1).png")
    try:
        Click = 'Выбрать платежи'
        MenuItem = WebDriverWait(driver, SeleniumTimeout + 150).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='text' and text()='{}']".format(Click)))
        )
        MenuItem.click()
        print(Click)
    except:
        # driver.save_screenshot(f"/home/admin/code/panel-tf/panel/bank/screenshots/{name_for_screenshots} (2).png")
        return 0

    try:
        Click = 'Загрузить'
        MenuItem = WebDriverWait(driver, SeleniumTimeout + 50).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='text' and text()='{}']".format(Click)))
        )
        MenuItem.click()
        print(Click)
    except:
        try:
            MenuItem = WebDriverWait(driver, SeleniumTimeout).until(
            EC.visibility_of_element_located((By.XPATH, "//div[text()='Импорт']"))
            )
            return 0
        except Exception as exc:
            return exc

    # driver.quit()
    return 0



