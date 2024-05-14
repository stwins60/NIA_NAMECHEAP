import random
import aiohttp
import asyncio

async def fetch_verse(session, verse):
    url = f'http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,en.asad'
    async with session.get(url) as response:
        data = await response.json()
        verse_a = data['data'][0]['text']
        verse_en = data['data'][1]['text']
        sura = data['data'][0]['surah']['englishName'] + '(' + str(data['data'][0]['surah']['number']) + '):' + str(data['data'][0]['numberInSurah'])
        return verse_a, verse_en, sura

async def get_verse():
    verse = random.randint(1, 6236)
    async with aiohttp.ClientSession() as session:
        return await fetch_verse(session, verse)

def main():
    loop = asyncio.get_event_loop()
    verse_a, verse_en, sura = loop.run_until_complete(get_verse())
    # print(verse_a, verse_en, sura)

if __name__ == "__main__":
    main()
