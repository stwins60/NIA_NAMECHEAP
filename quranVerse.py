import random
import requests as req

def getVerse():
    verse = random.randint(1,6237)
    # Get random verse from quran api
    data = req.get('http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,en.asad'.format(verse=random.randint(1, 6236)))
    data = data.json()
    # Get the verse
    verse_a = data['data'][0]['text']
    verse_en = data['data'][1]['text']
    sura = data['data'][0]['surah']['englishName']+\
            '('+str(data['data'][0]['surah']['number'])+'):'+\
            str(data['data'][0]['numberInSurah'])
    sura_name = sura.split('(')[0]
    sura_chapter = sura.split(':')[0].split('(')[1].split(')')[0]
    sura_verse = sura.split(':')[1]
    
    return verse_a, verse_en, sura_name, sura_chapter, sura_verse


# print(getVerse()[4])