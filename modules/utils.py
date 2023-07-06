import pygsheets
from pygsheets.worksheet import Worksheet
import sqlite3
import json

class MealUtils:
    def __init__(self) -> None:
        self._gsheets = pygsheets.authorize(service_file="gcp.json")
        self._spreadsheets = self._gsheets.open_by_url(
            "https://docs.google.com/spreadsheets/d/1gHvRGfwHbeimTNgHzfVErflvMnOoa_FE8rZoh_Pz35Q/")
        self._connection = sqlite3.connect("mealsql.db")
        self._cursor = self._connection.cursor()
        self._cursor.execute(
            """ CREATE TABLE IF NOT EXISTS `members` (`id` UNSIGNED BIG INT PRIMARY KEY, `name` VARCHAR(8) NOT NULL, `group` VARCHAR(20) NOT NULL) """)
        self._connection.commit()
        self._load_saves()

    def _load_saves(self) -> None:
        try:
            self._saves = json.load(open("saves.json", "r", encoding="utf-8"))
        except:
            self._saves = dict()
            self._dump_saves()

    def _dump_saves(self) -> None:
        json.dump(self._saves, open("saves.json", "w", encoding="utf-8"))

    def close(self) -> None:
        self._connection.close()

    def member_add(self, id: int, name: str, group: str) -> None:
        self._cursor.execute(
            f""" REPLACE INTO `members` (`id`, `name`, `group`) VALUES ({id}, "{name}", "{group}") """)
        self._connection.commit()

    def member_remove(self, id: int) -> None:
        self._cursor.execute(
            f""" DELETE FROM `members` WHERE `id` = {id} """)
        self._connection.commit()

    def member_query(self, id: int) -> tuple:
        self._cursor.execute(
            f""" SELECT * FROM `members` WHERE `id` = {id} """)
        return self._cursor.fetchone()

    def member_list(self) -> list:
        self._cursor.execute(
            f""" SELECT * FROM `members` ORDER BY `group` """)
        return self._cursor.fetchall()

    def meal_create(self, title: str) -> None:
        self._spreadsheets.add_worksheet(title, index=0)
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        members = self.member_list()

        sheet.update_values("A1", [["本日補助", 0, "餐點", "價格", "自付", "已交錢", "店家", "品項", "價格", "數量", "小計"]])
        sheet.update_value("G2", "無")
        sheet.update_values("D2", [[f"=XLOOKUP(C{i},H:H,I:I,\"\")", f"=IF(C{i}=\"\",\"\",IF(D{i}>B1,D{i}-B1,0))"] for i in range(2, 101)])
        sheet.update_values("J2", [[f"=IF(H{i}=\"\",\"\",COUNTIF(C2:C100,H{i}))", f"=IF(H{i}=\"\",\"\",I{i}*J{i})"] for i in range(2, 101)])
        sheet.update_valuea("L1", [["總金額"], ["=SUM(K2:K100)"], ["自付"], ["=SUM(E2:E100)"], ["報帳"], ["=L2-L4"]])
        sheet.update_values("A2", [[members[i][2]] for i in range(len(members))])
        sheet.update_values("B2", [[members[i][1]] for i in range(len(members))])

    def meal_list(self) -> list:
        return self._spreadsheets.worksheets()

    def meal_discount(self, title: str, value: int | None = None) -> int | None:
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        if value == None:
            return int(sheet.get_value("B1"))
        sheet.update_value("B1", value)

    def meal_add(self, title: str, item: str, price: int) -> None:
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        items = self.meal_query(title)
        if item in map(lambda x: x[0], items):
            raise Exception()
        items.append([item, price, 0])
        sheet.update_values("H2", items)

    def meal_query(self, title: str) -> list[list]:
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        items = sheet.get_values("H2", "I100")
        if items[0][0] == "":
            items = []
        return items
    
    def meal_delete(self, title: str, item: str):
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        items = self.meal_query(title)
        if item not in map(lambda x: x[0], items):
            raise Exception()
        for i in range(len(items)):
            if items[i][0] == item:
                break
        del items[i]
        sheet.clear("H2", "I100")
        sheet.update_values("H2", items)
    
    def meal_store(self, title: str, store: str | None = None) -> str | None:
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        if store == None:
            return sheet.get_value("G2")
        sheet.update_value("G2", store)

    def order_update(self, title: str, user_id: int, item: str) -> None:
        sheet: Worksheet = self._spreadsheets.worksheet_by_title(title)
        sheet_users = list(map(lambda x: x[0], sheet.get_values("B2", "B100")))
        self._cursor.execute(
            f""" SELECT `name` FROM `members` WHERE `id` = {user_id} """)
        index = sheet_users.index(self._cursor.fetchone()[0])
        sheet.update_value(f"C{index + 2}", item)

    def lastest_msg_id(self, id: int | None = None) -> int | None:
        self._load_saves()
        if id == None:
            return self._saves["msg_id"]
        self._saves["msg_id"] = id
        self._dump_saves()

    def lastest_meal_title(self, title: str | None = None) -> int | None:
        self._load_saves()
        if title == None:
            return self._saves["meal_title"]
        self._saves["meal_title"] = title
        self._dump_saves()

