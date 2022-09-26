import pandas as pd
from bs4 import BeautifulSoup
import requests

page = requests.get("https://www.len.com.ng/csblogdetail/421/Classification-and-types-of-planets-with-their-characteristics")
soup = BeautifulSoup(page.content, "html.parser")


