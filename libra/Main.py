import json
import requests
import pandas as pd
import time

info = {
    "email": "info@volt-zonnepanelen.nl",
    "password": "jiwRuh-8sanza-joqkaj",
    "login-url": "https://shop.libra.energy/shop-api/login",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2NDQ2NjE1NDUsImV4cCI6MTY0NDY2MjQ0NSwicm9sZXMiOlsiUk9MRV9VU0VSIl0sInVzZXJuYW1lIjoiaW5mb0B2b2x0LXpvbm5lcGFuZWxlbi5ubCJ9.ERm7Q5-IYoD14EJGesKl88lZzPS4DebZTjwMVRz_aTAWk3FsOCxdcaAuNELojOBsZYx_Sa4V-369gKSPPTbxn7CG0HSln-zQl8Dgvbrp61L6uB3ahfw17Mj2OHD0pi1jyYRsg17dU3as0DcTW9mY0foB0vNAUzQiccV3RlEhwTwe4Cb4JU5NY0cBMZSEp2jVP_qNgZ6yfi9fhAI-S5EN8LmR-m0z87gKRKShM5jEseCq0dHbFwi_cU4NnT9lWokAOQPMWX0BFtN4UnejZL7VYK2Y6jxz5a2oDYysDrAHVzwY__hKmLaYy-wGZ1uVXpgydZpKeHq2y5dWxzRyKeaCaRNu6eStS4JIYp4rhiEkCiI6YLWdG9K68c-dKyafXF8y5Mlne1-7Rjwu_ZeXMwMWDMjB9P938S5LE279ZQly_iBKrbH-d3c3gy6X59TkcEs-5zpIiD2_m9r5sD_R9TFrQdyQnzV3x4LFba2ZvHscwy281GKUWQmj86CljsVotmlQgGHWImWDCpuDLsm9NLAyzIKlMsyvOj_Hda7PKQgInU7pLnXiBXoD7LxTCk1AKpBhYxFr5q7jVey9WFg0NPwntdhHyXuOWu0O5_7ARYUHuV1RdwAqny_sjEl1AvIVHnxc8QjdrKkw5cbk1ZD9qQezu2aMWuOu4AkJuFFqof2pAMo",
    "main_url": "https://shop.libra.energy",
    "taxon_url": "https://shop.libra.energy/shop-api/taxons",
    "product_ext": "producten",
    "shop_api": "https://shop.libra.energy/shop-api/taxon-products/by-slug/{product}?page=1&limit=10000",
    "stock_api": "https://shop.libra.energy/shop-api/stock"
}

class Test():
    def myTest(self):
        print('test')

class Engine():
    def generateCSV(self):
        while True:
            print("start generating2")
            auth = Auth()

            Auth.authToken = auth.login()
            data = {'main_category': ['solar', 'solar', 'solar', 'solar', 'solar', 'energieopslag', 'energieopslag', 'energieopslag', 'e-mobility', 'e-mobility', 'e-mobility', 'kabels', 'kabels', 'kabels', 'kabels'],
                    'category': ['zonnepanelen', 'omvormers', 'montagematerialen', 'accessoires', 'garanties', 'hybride-omvormers', 'accu-s-en-batterijen', 'accessoires', 'laadpalen', 'accessoires', 'configuraties', 'connectoren', 'kabelmanagement', 'kabels', 'overige'],
                    'price_rate': [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3]}

            categoriesDf = pd.DataFrame(data)

            collectProductUrls = CollectProductUrls()

            stockDf = collectProductUrls.collectStock()

            productDf = collectProductUrls.collectAllOfLinks(categoriesDf, stockDf)

            productDf.to_csv('out.csv', index=False)
            print("bitti")
            time.sleep(3600)


def getMainCategoriesList():
    categoriesDf = pd.DataFrame(columns=["main_category", "category"])

    url = info["taxon_url"]

    response = requests.get(url)

    responseList = json.loads(response.content)

    for elem in responseList:
        mainCategory = elem["slug"]

        for childElem in elem["children"]:
            category = str(childElem["slug"]).split("/")[1]
            categoriesDf.loc[len(categoriesDf)] = [mainCategory, category]

    return categoriesDf


class Auth:
    authToken = ""

    def login(self):
        payload = {"email": info["email"], "password": info["password"]}

        response = requests.post(info["login-url"], json=payload)

        responseJson = json.loads(str(response.content, 'utf-8'))

        authToken = "Bearer " + responseJson["token"]
        return authToken


class CollectProductUrls:
    idCounter = 1

    def collectStock(self):
        stockDf = pd.DataFrame(columns=["SKU", "STOCK"])

        isContinue = True
        while isContinue:
            try:
                response = requests.get(info["stock_api"])

                if response.status_code != 200:
                    continue

                responseAsStr = str(response.content, 'utf-8')
                responseAsStr = responseAsStr.replace("\n", "")
                responseAsStr = responseAsStr.replace("\r", "")
                responseAsStr = responseAsStr.replace("\t", "")
                responseAsStr = responseAsStr.replace("  ", " ")

                productList = json.loads(responseAsStr)
                for elem in productList:
                    try:
                        sku = elem["sku"]
                    except:
                        sku = ""

                    try:
                        stock = elem["availableFrom"]["quantity"]
                    except:
                        stock = ""
                    stockDf.loc[len(stockDf)] = [sku, stock]

                isContinue = False
            except:
                iy = 0

        return stockDf

    def collectAllOfLinks(self, df, stockDf):
        unique_arr = df["main_category"].unique()
        columns = ["ID", "Categories", "Code", "Name", "SKU", "Description", "Short description", "attributes", "Images", "Published", "Brand", "Published", "Datasheet", "Stock", "In stock?", "Sales price", "Regular price",
                   "Merk", "Lengte", "Breedte", "Module-rendement", "Vermogen", "MPP-spanning", "Kabellengte", "MPP vermogen (Maximum Power Point)", "Hoogte", "Nullastspanning", "Max. systeemspanning", "Kortsluitstroom", "Aantal bypassdiodes", "Aantal cellen", "Gewicht", "MPP-stroom", "Met aansluitkabel", "Met frame", "Kleur frame", "Celmateriaal", "AC-nom. uitgangsvermogen", "WiFi", "Aantal MPP trackers", "Ingebouwde batterij", "Ethernet", "Netbewaking", "Type", "Serie"
                   ]
        productDf = pd.DataFrame(columns=columns)

        for mainCategory in unique_arr:
            header = {"authorization": Auth.authToken}
            url = str(info["shop_api"]).format(product=mainCategory)
            response = requests.post(url, data={}, headers=header)

            responseAsStr = str(response.content, 'utf-8')
            responseAsStr = responseAsStr.replace("\n", "")
            responseAsStr = responseAsStr.replace("\r", "")
            responseAsStr = responseAsStr.replace("\t", "")
            responseAsStr = responseAsStr.replace("  ", " ")

            print(mainCategory)
            print(url)
            print(response)
            productList = json.loads(responseAsStr)["items"]

            for product in productList:
                tmpList = CollectProductUrls.setArrayFromRecord(self, df, product, stockDf)
                productDf.loc[len(productDf)] = tmpList

        return productDf

    def getQuantityBySku(self, sku):
        try:
            response = requests.get("https://shop.libra.energy/shop-api/stock?sku[]=" + sku)

            responseAsStr = str(response.content, 'utf-8')
            responseAsStr = responseAsStr.replace("\n", "")
            responseAsStr = responseAsStr.replace("\r", "")
            responseAsStr = responseAsStr.replace("\t", "")
            responseAsStr = responseAsStr.replace("  ", " ")

            productList = json.loads(responseAsStr)

            lastDateIndex = ''
            for dateIndex in productList[0]["available"]:
                lastDateIndex = dateIndex

            return productList[0]["available"][lastDateIndex]

        except:
            return None

    def setArrayFromRecord(self, df, product, stockDf):
        myList = []

        myList.append(str(self.idCounter).zfill(5))
        self.idCounter += 1
        # category
        try:
            myList.append(CollectProductUrls.formatterCategory(self, product["taxons"]["main"].split("/")[0]) + ", " + CollectProductUrls.formatterCategory(self, product["taxons"]["main"].split("/")[1]))
        except:
            myList.append(None)

        # code
        try:
            myList.append(product["code"])
        except:
            myList.append(None)

        # name
        try:
            myList.append(product["name"])
        except:
            myList.append(None)

        # slug
        try:
            myList.append(product["slug"])
        except:
            myList.append(None)

        # description
        try:
            myList.append(product["description"])
        except:
            myList.append(None)

        # shortDescription
        try:
            # product["datasheet"][0]
            if "datasheet" in product and product["datasheet"][0]:
                myList.append(product["shortDescription"] + "<br></br><a href=\"" + product["datasheet"][0] + "\">Datasheet</a>  <br></br> ")
            else:
                myList.append(product["shortDescription"])
        except:
            myList.append(None)

        # attributes
        try:
            myList.append(product["attributes"])
        except:
            myList.append(None)

        # images
        try:
            myList.append(", ".join(item["relativePath"] for item in product["images"]))
        except:
            myList.append(None)

        # enabled
        try:
            myList.append(product["enabled"])
        except:
            myList.append(None)

        # brand
        try:
            myList.append(product["brand"])
        except:
            myList.append(None)

        # Published
        try:
            myList.append(1 if str(product["onSale"]) == "true" else 0)
        except:
            myList.append(None)

        # datasheet
        try:
            myList.append(product["datasheet"][0])
        except:
            myList.append(None)

        # stock
        try:
            myList.append(CollectProductUrls.getQuantityBySku(self, product["code"]))
        except:
            myList.append(None)

        # stock
        try:
            if myList[-1] and str(myList[-1]) and str(myList[-1]) != "" and str(myList[-1]) != "0":
                myList.append(1)
            else:
                myList.append(0)
        except:
            myList.append(0)
        # sales price
        try:
            value = ""
            for key in product["variants"]:
                value = product["variants"][key]["originalPrice"]["current"]

            record = df.loc[df['category'] == product["taxons"]["main"].split("/")[1]]

            priceRate = record.loc[record.index.values.tolist()[0]]["price_rate"]
            newPrice = (value / 100) * priceRate
            myList.append(round(newPrice, 2))
        except:
            myList.append(None)

        # regular price
        try:
            value = ""
            for key in product["variants"]:
                value = product["variants"][key]["price"]["current"]

            record = df.loc[df['category'] == product["taxons"]["main"].split("/")[1]]

            priceRate = record.loc[record.index.values.tolist()[0]]["price_rate"]
            newPrice = (value / 100) * priceRate
            myList.append(round(newPrice, 2))
        except:
            myList.append(None)

        # "Merk", "Lengte", "Breedte", "Module-rendement", "Vermogen", "MPP-spanning", "Kabellengte", "MPP vermogen (Maximum Power Point)", "Hoogte", "Nullastspanning", "Max. systeemspanning", "Kortsluitstroom", "Aantal bypassdiodes", "Aantal cellen", "Gewicht", "MPP-stroom", "Met aansluitkabel", "Met frame", "Kleur frame", "Celmateriaal"
        # Merk
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Merk" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Lengte
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Lengte" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Breedte
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Breedte" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Module-rendement
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Module-rendement" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Vermogen
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Vermogen" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # MPP-spanning
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "MPP-spanning" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Kabellengte
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Kabellengte" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # MPP vermogen (Maximum Power Point)
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "MPP vermogen (Maximum Power Point)" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Hoogte
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Hoogte" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Nullastspanning
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Nullastspanning" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Max. systeemspanning
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Max. systeemspanning" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Kortsluitstroom
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Kortsluitstroom" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Aantal bypassdiodes
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Aantal bypassdiodes" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Aantal cellen
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Aantal cellen" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Gewicht
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Gewicht" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # MPP-stroom
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "MPP-stroom" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Met aansluitkabel
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Met aansluitkabel" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Met frame
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Met frame" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Kleur frame
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Kleur frame" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Celmateriaal
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Celmateriaal" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # AC-nom. uitgangsvermogen
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "AC-nom. uitgangsvermogen" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # WiFi
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "WiFi" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Aantal MPP trackers
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Aantal MPP trackers" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Ingebouwde batterij
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Ingebouwde batterij" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Ethernet
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Ethernet" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Netbewaking
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Netbewaking" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Type
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Type" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        # Serie
        try:
            added = False
            for elems in product["attributes"]:
                if elems["name"] == "Serie" and not added:
                    myList.append(elems["value"])
                    added = True

            if not added:
                myList.append("")
        except:
            myList.append(None)

        return myList

    def formatterCategory(self, key):
        categoryJson = {}
        categoryJson['zonnepanelen'] = 'Zonnepanelen'
        categoryJson['omvormers'] = 'Omvormers'
        categoryJson['montagematerialen'] = 'Montagematerialen'
        categoryJson['accessoires'] = 'Accessoires'
        categoryJson['garanties'] = 'Garanties'
        categoryJson['hybride-omvormers'] = 'Hybride omvormers'
        categoryJson['accu-s-en-batterijen'] = "Accu's en batterijen"
        categoryJson['laadpalen'] = 'Laadpalen'
        categoryJson['configuraties'] = 'Configuraties'
        categoryJson['connectoren'] = 'Connectoren'
        categoryJson['kabelmanagement'] = 'Kabelmanagement'
        categoryJson['kabels'] = 'Kabels'
        categoryJson['overige'] = 'Overige'
        categoryJson['solar'] = 'Solar'
        categoryJson['energieopslag'] = 'Energieopslag'
        categoryJson['e-mobility'] = 'E-mobility'
        categoryJson['kabels'] = 'Kabels'

        try:
            return categoryJson[key]
        except:
            return key

