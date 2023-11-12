import json
import math

# 引入會員資料
global user_data
with open('user_data.json','r', encoding="utf-8") as f:
    user_data = json.load(f)

# 引入商品資料
global product_list
with open('product.json','r',encoding='utf-8') as f:
    product_list = json.load(f)

global login_status
login_status = False

global login_user
login_user = {}

global cart
cart = []

global register_data
register_data = {
    "username": "",
    "email": "",
    "password": "",
}

# 【系統功能-檢查帳號】
def is_user(username:str) -> bool:
    """
    根據給予的帳號，逐項檢查是否存在於資料集中。
    """
    for user in user_data:
        if user["username"] == username:
            return True
    return False


# 【系統功能-檢查電子郵件】
def check_email(email:str) -> bool:
    """
    根據給予的電子郵件，逐項檢查是否與資料集中的電子郵件重複。
    """
    for user in user_data:
        if user["email"] == email:
            return True
    return False

# 【系統功能-檢查電子郵件格式】
def is_valid_email(email:str) -> bool:
    """
    1. 輸入的電子郵件中只能有一個@，並且@不能出現在開頭或結尾。
    2. 以 @ 拆成兩個部分，前面的部分是「使用者名稱」，後面的部分是「域名」。
    3. @ 前後的「使用者名稱」、「域名」都要存在。
    4. 「域名」的部分要包含至少一個句點。
    """
    if email.count('@') != 1:
        return False
    
    name, domain = email.split('@')
    
    if not name or not domain:
        return False
    
    if domain.count('.') < 1:
        return False
    
    return True

# 【系統功能-檢查密碼安全性】
def is_valid_password(pwd:str) -> bool:
    """
    1. 密碼長度需大於8個字元。
    2. 密碼需包含大小寫字母與數字。
    """
    if len(pwd) < 8:
        return False
    has_upper, has_lower, has_digit = False, False, False
    
    # 檢查每個字符
    for char in pwd:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
            
    return has_upper and has_lower and has_digit

# 【系統功能-確認密碼】
def check_password(username:str, pwd:str) -> bool:
    """
    根據給予的帳號與密碼，檢查是否與資料集中的帳號與密碼相符。
    """
    for user in user_data:
        if username == user["username"] and pwd == user["password"]:
            return True
    
    return False

# 【系統功能-檢查商品是否存在】
def is_product(item:str) -> bool:
    for product in product_list:
        if product['name'] == item:
            return True
        
    return False

# 【系統功能-檢查商品庫存是否足夠】
def is_sufficient(item:str, number:int) -> bool:
    """
    根據給予的商品名稱，逐項檢查是否存在於資料集中。
    
    註: 此函式會檢查number是否為正整數，若不是則會拋出TypeError例外。
    例外訊息為「商品數量必須為正整數」。
    """
    
    if type(number) != int or number <= 0:
        raise TypeError("商品數量必須為正整數")
    
    for product in product_list:
        if product['name'] == item:
            if product['stock'] >= number:
                return True

    return False


# 【系統功能-加入購物車】
def add_to_cart(item:str, number:int):
    """
    1. 檢查商品是否存在。
    2. 檢查商品庫存是否足夠。
    3. 如果檢查都通過，則顯示「【{item}*{number} 已加入購物車!】」。
    """
    if not is_product(item):
        print("【我們沒有這個商品喔!】")
        return
    
    if not is_sufficient(item, number):
        print(f"【很抱歉，我們的庫存不足{number}份!> <】")
        return
    
    cart.append((item, number))
    print(f"【{item}*{number} 已加入購物車!】")
    
# 【系統功能-產生商品資訊】
def generate_product_info(page_number: int, page_size=10) -> str:
    """
    此函式是一個產生器，根據提供的頁數來產生商品資訊。
    1. 計算商品資料的起始索引與結束索引。
    2. 以yield的方式回傳商品資訊。
    3. 商品名稱與備註的欄位，使用全形空白填滿。
    4. 商品資訊的格式如下：
    |    商品名稱    |  售價  |   折扣  |  剩餘庫存  |        備註        |
    """
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size

    yield "|    商品名稱    |  售價  |   折扣  |  剩餘庫存  |        備註        |"
    yield "-" * 70
    for product in product_list[start_index:end_index]:
        name = product['name']
        price = f"{product['price']}元"
        discount = product['discount']
        stock = product['stock']
        remark = product['remark']

        # 處理打折名稱
        if discount == 1:
            discount_str = "　-"
        elif discount * 100 % 10 == 0:
            discount_str = f"{int(discount * 10)}折"
        else:
            discount_str = f"{int(discount * 100)}折"

        yield f"|{name:{chr(12288)}>8}|{price:>7}|{discount_str:>8}|{stock:>12}|{remark:{chr(12288)}>10}|"
    yield "-" * 70
    
# 【功能限制-登入後才能用的項目】
def check_login(func):
    """
    此函式為裝飾器，需接收一個函式作為參數。
    
    這個裝飾器會使被裝飾的函式，只有在登入後才能執行。
    
    如果有登入，則執行原函式；如果沒有登入，則顯示「【請先登入】」。
    """
    def wrapper(*args, **kwargs):
        if login_status:
            func(*args, **kwargs)
        else:
            print("【請先登入】")
    return wrapper