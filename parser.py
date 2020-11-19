from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from pygeckodriver import geckodriver_path
from time import sleep

MAIN_URL = 'https://www.wildberries.ru/'

def get_top_menus(driver, unnecessary_cat_ids=[]):
    """
    Функция получается ссылки на основные
    категории товаров Wildberries. В итоговый список
    не включены те категории, id которых переданы в
    списке.
    Возвращает список url-ов.
    
    """
    driver.get(MAIN_URL)
    sleep(1)

    main_menu_button = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div[2]/button')
    main_menu_button.send_keys(Keys.RETURN)

    # Поиск всех элементов topmenus
    top_menus_block = driver.find_element_by_class_name("topmenus")
    top_menus_items = top_menus_block.find_elements_by_class_name("topmenus-item")
    print(f"Len top menus: {len(top_menus_items)}")

    # Получим ссылки на top_menus и сразу исключим не нужные категории
    menus_links = []
    for item in top_menus_items:
        # Получим значение data-menu-id
        cur_id = int(item.get_attribute('data-menu-id'))
        if cur_id not in unnecessary_cat_ids:
            a_elem = item.find_element_by_tag_name('a')
            cur_url = a_elem.get_attribute('href')
            menus_links.append(cur_url)

    return menus_links

# Список для всех url-ов категорий
all_categories_urls = []

def parse_categories_on_page(driver):
    """
    Парсит все ссылки со страницы в боковом 
    меню.
    """
    categories_licks_on_page = []
    # проверка на sport
    last_url_part = driver.current_url.split('/')[-1]
    if last_url_part == 'sport':
        ul_elem = driver.find_element_by_class_name("j-menu-catalog-second")

        # сразу ищет теги a по классу, удалям сразу первую
        a_elems = ul_elem.find_elements_by_class_name("menu-item-link")[1:]
    else:
        try:
            ul_elem = driver.find_element_by_class_name("sidemenu")
            a_elems = ul_elem.find_elements_by_tag_name('a')[1:]
        except NoSuchElementException:
            try:
                ul_elem = driver.find_element_by_class_name("maincatalog-list-2")
                a_elems = ul_elem.find_elements_by_tag_name("a")
            except NoSuchElementException:
                print(f"Parser failed on {driver.current_url}")
        
        
    #  добавление href в categories_licks_on_page
    for a_elem in a_elems:
        cur_url = a_elem.get_attribute('href')
        categories_licks_on_page.append(cur_url)

    return categories_licks_on_page

def collect_urls_from_list(driver, urls):
    """

    """
    new_categories = []

    for url in urls:
        driver.get(url)
        new_categories += parse_categories_on_page(driver)

    return new_categories


driver = webdriver.Firefox(executable_path=geckodriver_path)
# исключенные категории:
# # Авиабилеты id="61037", Premium id="63451", Ювелирные изделия id="1023",
# Тренды id="1003", Бренды id="4853", Акции id="2192", Цифровые товары id="62813"
unnecessary_cat_ids = [61037, 63451, 1023, 1003, 4853, 2192, 62813]
top_menus_urls = get_top_menus(driver, unnecessary_cat_ids)

second_menus_urls = collect_urls_from_list(driver, top_menus_urls)

print(f"len second_menus_urls: {len(second_menus_urls)}")
for url in second_menus_urls:  
    print('-->', url)

# exit
print(f"End programm")
driver.close()