import pyppeteer
from bs4 import BeautifulSoup
import asyncio
import html
import time
import pandas as pd


def export_data(data: list):
    df = pd.DataFrame(data)
    print(df)
    df.to_excel("posts.xlsx", index=False)


def scrape_data(content: str):
    soup = BeautifulSoup(content, "html.parser")
    selectors = {
        "Quest Number": "#view-bid-posting > div.row.visible-print.print > div.col-md-10 > div > h4 > span > b",
        "Closing Date": "#current_project > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)",
        "Est. Value Notes": "#current_project > div > div:nth-child(2) > div > table > tbody > tr:nth-child(3) > td:nth-child(2)",
        "Description": "#current_project > div > div:nth-child(3) > div > table > tbody > tr:nth-child(3) > td:nth-child(2)",
    }

    data = {}

    for selector in selectors.keys():
        data[selector] = soup.select_one(selectors[selector]).get_text()

    data["Quest Number"] = data["Quest Number"].split(": ")[1]

    return data


async def main():
    BASE_URL = "https://qcpi.questcdn.com/cdn/posting/?group=1950787&provider=1950787"

    # # INITIALIZE HEADLESS BROWSER
    browser = await pyppeteer.launch(headless=True)
    url = await browser.newPage()
    await url.goto(
        BASE_URL,
        timeout=40000,
    )  # PROVIDE TIMEOUT FOR SLOW INTERNET CONNECTION
    await url.waitForSelector(
        "#table_id > tbody > tr:nth-child(1) > td:nth-child(4) > div > a"
    )
    btns = await url.querySelectorAll(
        "#table_id > tbody > tr > td:nth-child(4) > div > a"
    )  # GET ALL POSTS ON PAGE

    posts = len(btns)  # COUNT POSTS ON PAGE

    if not btns:
        print("There are no posts.")

    time.sleep(
        1
    )  # WAIT FOR JAVASCRIPT TO GET LOADED FOR EXECUTING FUNCTION FOR OPENING NEXT PAGE OF DETAILS
    await btns[0].click()
    await url.waitForSelector(
        "#current_project > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)"
    )

    data = []
    page_content = await url.content()
    data.append(scrape_data(page_content))

    for i in range(1, min(5, posts)):
        btn = await url.querySelector("#id_prevnext_next")
        time.sleep(0.5)
        await btn.click()
        await url.waitForSelector(
            "#current_project > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)"
        )
        time.sleep(0.5)
        data.append(scrape_data(await url.content()))

    export_data(data)

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
