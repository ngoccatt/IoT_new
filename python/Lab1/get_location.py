import os

lat, lot = os.popen('curl ipinfo.io/loc').read().split(',')

# ------------------Lay location dua vao IP (thuong dan toi nha cung cap dich vu ISP)---------------------------
import geocoder

g = geocoder.ip('me')
print(g.raw)
print(g.raw['loc'])
print("Latitude = %f, Longitude = %f" % (g.latlng[0], g.latlng[1]))
# ----------------------------------------------------------------------------------------------------------------

# my true location
# 10.699914, 106.730919


# -------------------su dung Windows va API cua windows (ap dung cho windows 10 tro len) de lay location---------------------------------
# https://stackoverflow.com/questions/24906833/how-to-access-current-location-of-any-user-using-python#:~:text=0-,I%20have%20been%20trying%20for%20months%20to%20get%20this%20and%20finally%20I%20came%20across%20a%20solution%20for%20windows%20users!%20For%20me%20it%20got%20as%20close%20as%20the%20street%20name.%20You%20need%20to%20install%20winrt(https%3A//pypi.org/project/winrt/)%20Here%20it%20is%3A,-import%20winrt.windows
import winrt.windows.devices.geolocation as wdg, asyncio


async def getCoords():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]


def getLoc():
    return asyncio.run(getCoords())


# ----------------------------------------------------------------------------------------------------------

# ------------------------------Su dung google chrome de lay location -------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time

s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.get('https://www.google.com')
# dong code duoi day dung de tao them 1 p co id = "location" chen vao trang web
# thuc te thi cac ham o day deu la ham async, nen ta khong the tra ve 1 gia tri nao ca
# kieu, khi goi ham async, thay vi cho async lam xong thi code di toi dong tiep theo luon
# con ham async chay trong background, khi nao no xong thi no goi ham callback
string = '''
   function getLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var myjson = {"latitude":position.coords.latitude, "longitude":position.coords.longitude};
                console.log(position);
                console.log(position.coords.latitude);
                console.log(position.coords.longitude); 
                var stringJson = JSON.stringify(myjson);
                console.log(stringJson);
                const para = document.createElement("p");
                para.innerHTML = stringJson;
                para.id = "location";
                document.body.appendChild(para);
            });
        } else {
            console.log("Geolocation is not supported by this browser.");
        }
    }
    getLocation();'''.replace('\n', '').replace('\t', '')


# repeat this code
try:
    driver.execute_script(string)
    time.sleep(2)
    res = driver.find_element(By.ID, "location")
    loc = res.text
    locDict = json.loads(loc)
    print("latitude: %f, longitude: %f" % (locDict["latitude"], locDict["longitude"]))
except:
    print("unable to get latitude and longitude")

# -------------------------------------------------------------------------------------------------


# code driver co the tra ve gia tri neu ham duoc goi return cai gi do.
string = '''
        function returnsomething() {
            return "abc"
        }
        return returnsomething()'''
driver.execute_script("return {foo: 'bar'}")
driver.execute_script(string)

# ---------------------lay location su dung geopy va Nominatim-----------------------
from geopy.geocoders import Nominatim
import geocoder

longitude = 106.7
latitude = 10.6

app = Nominatim(user_agent="me")
address = 'Ho Chi Minh City University of Technology'

location = app.geocode(address)
# type(location) -> geopy.location.Location

dictLocation = location.raw  # this is a dict
print(dictLocation)
for i in dictLocation:
    print("%s: %s" % (i, str(dictLocation[i])))

# dict -> json:
jsonLocation = json.dumps(location.raw)  # and this is a Json
print(jsonLocation)
# day la 1 chuoi json, va chuoi json nay ko the truy cap duoc!. De truy cap,
# buoc phai dung json.loads() de bien json thanh dict.


# xem link sau de xem kieu du lieu cua class geopy.location.Location
# https: // geopy.readthedocs.io / en / stable /  #:~:text=Data-,class,geopy.location.Location(address%2C%20point%2C%20raw),-Contains%20a%20parsed
longitude = location.longitude
latitude = location.latitude

# ------------------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def getLocation():
    options = Options()
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    timeout = 20
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    driver.get("https://mycurrentlocation.net/")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)
    longitude = driver.find_element(By.XPATH, '//*[@id="longitude"]').text
    latitude = driver.find_element(By.XPATH, '//*[@id="latitude"]').text
    driver.quit()
    return (latitude, longitude)


print(getLocation())

# another way
import requests
res = requests.get('https://ipinfo.io/')
data = res.json()

location = data['loc'].split(',')
print(location)

13.7765, 109.2237
