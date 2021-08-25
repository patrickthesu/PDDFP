import shutil
import requests
from bs4 import BeautifulSoup as bs

link = 'https://vodiy.ua'

#cache this 
def getBiletOrTheme  ( bilet = -1, theme = None, exam = False ) :
    print ('Getting bilet...')

    payload = { 'complect' : '6' }

    if theme == None :
        payload['bilet'] = bilet
    else : 
        payload['theme'] = theme

    response = requests.get( link + '/pdr/test/', params = payload )
    soup = bs( response.content , 'lxml' )
    return soup.find( class_ = 'ticketpage_ul' ).find_all('li')


def getQuestion ( number = 1, bilet = -1, theme = None, qusestionsList = False ):
    
    if qusestionsList == False :
        qusestionsList = getBiletOrTheme ( bilet = bilet, theme = theme )
    
    class questions: 
        img = False
    question = questions()
    question.answers = []
    question.text = qusestionsList[ number - 1 ].find('p').text.strip()  # =  qusestionsList[ number - 1 ]\
    question.img = False

    print ( question.text )
    
    imgBlock = qusestionsList[ number - 1 ].find( class_ = 'ticket_left' )
    if imgBlock != None :
        img = imgBlock.find ( 'img' )
        imgUrl = link + img.get('src')
        # print (imgUrl)
        r = requests.get(imgUrl, stream=True) 
        # print (r.status_code)
        if r.status_code == 200:   #200 status code = OK  
            question.img = True   
            with open("1.jpg", 'wb') as f: 
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    
    answers = qusestionsList[ number - 1 ].find_all( class_ = 'label_raio')

    for index in range( len(answers) ) : 

        question.answers.append( answers[index].find( class_ = 'span_text' ).text.strip() )
           
        if answers[index].find( class_ = 'radio' ).find( 'input' ).get( 'rel' ) == 'rt1' :
            question.correctAnswerI = index
   
    return question 

# for i in range( 1, 2 ):
#     print( str ( getQuestion( number = i, bilet = 1 ).correctAnswerI + 1 ) )


# print (len ( questionsLi ))
