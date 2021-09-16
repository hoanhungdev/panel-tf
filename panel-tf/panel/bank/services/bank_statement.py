from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from bank.services.pattern_bank_statement import DoDownload

Iterations = 5

bank_accounts = [
    {'bank': 'Банковская выписка из Альфа-Банка', 'account': 'ИП Пахомов Александр Александрович - 4080 2810 7290 5000 0789'},
    {'bank': 'Банковская выписка из Альфа-Банка', 'account': 'ООО "Техно Фасад" - 4070 2810 8290 5000 1872'},
    {'bank': 'Банковская выписка из Альфа-Банка', 'account': 'ООО "Техно Фасад" - 4070 2810 4290 5000 3319'},
    {'bank': 'Банковская выписка из Альфа-Банка', 'account': 'ИП Пахомов Александр Александрович - 4080 2810 6290 5000 1613'},
]

def get_bank_statement():
    for ba in bank_accounts:
        for i in range(0, Iterations):
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Remote("http://selenium:4444/wd/hub", desired_capabilities=chrome_options.to_capabilities())
            driver.implicitly_wait(40)  # неявное ожидание появления элемента в видимости
            driver.set_page_load_timeout("{}".format(40))

            status = DoDownload(driver, ba['bank'], ba['account'])
            if status == 0:
                break
            else:
                print("Ошибка: ", status)
                
            # driver.quit()

