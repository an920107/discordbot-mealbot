import pygsheets
from pygsheets.worksheet import Worksheet
from modules.utils import MealUtils

gsheets = pygsheets.authorize(service_file="gcp.json")
sheets = gsheets.open_by_url(
    "https://docs.google.com/spreadsheets/d/1gHvRGfwHbeimTNgHzfVErflvMnOoa_FE8rZoh_Pz35Q/")


print(f"{MealUtils().meal_store('07/07')}")