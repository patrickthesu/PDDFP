import config
import logging
import parsing
#from telebot import types
from aiogram import Bot, Dispatcher, executor, types

# log level
logging.basicConfig( level=logging.INFO )

# bot init
bot = Bot( token=config.TOKEN )
dp = Dispatcher( bot )

# 


# echo
@dp.message_handler( commands = 'start' )
async def start ( message: types.Message ):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	
	item1 = types.KeyboardButton('Задания 📋')
	item2 = types.KeyboardButton('Пройти экзамен 📝')
	item3 = types.KeyboardButton('Статистика 📊')
	item4 = types.KeyboardButton('Главное меню 🏠')
	markup.add(item1, item2, item3, item4)


	await bot.send_sticker( message.chat.id, 'CAACAgQAAxkBAAECs7VhDkRBFeq3kdWMmW_y6PjDjpm8cAACOhgAAqbxcR6cYA5lHoA_dCAE')
	await bot.send_message( message.chat.id, '''Привет, {0.first_name} ! Этот телеграм бот сделан для получения ПДД тестов с сайта vodiy.ua. Здесь вы можете легко получать статистику прохождения, сохранять и заново проходить некоторые тесты. Чтож, ни гвоздя вам, не жезла! Удачи !!!'''.format( message.from_user ), reply_markup = markup )

	# registing or log in 

@dp.message_handler( content_types = ['text'] )
async def operations ( message ):
	if message.chat.type == 'private':
		if message.text == 'Задания 📋':

			markup = types.InlineKeyboardMarkup( row_width = 2 ) 
		
			for i in range(1, 11):
				markup.add( types.InlineKeyboardButton( str(i), callback_data = '{0}'.format(i) ))

			# item1 = types.InlineKeyboardButton( '>> ', callback_data = '>>' )
			item1 = types.InlineKeyboardButton(">>", callback_data='>>')
			item2 = types.InlineKeyboardButton( '...', callback_data = '...' )

			markup.add(item1, item2)

			await bot.send_message( message.chat.id, 'Выберите билет, или напишите номер в чат', reply_markup = markup )

		elif message.text == 'Пройти экзамен 📝':
			await passBilet ( exam = True, chatID = message.chat.id )
		elif message.text == 'Статистика 📊':
			print ('lol')
		else:
			await bot.send_message( message.chat.id, 'https://youtu.be/06IwTULTJmo' )

async def sendQuestion( question, chatID ): 

	global nowQuestion

	nowQuestion = question

	markup = types.InlineKeyboardMarkup( row_width = 2 ) 
	tooLongAns = False
	for i in range ( len ( question.answers ) ) :
		# print ( tooLongAns )
		if ( len ( question.answers[i] ) > 40 and not tooLongAns ) :
			tooLongAns = True
			# print ( len ( question.answers[i] ))
			question.text += "\n\nВарианты ответа:\n\n"
			for j in range ( len ( question.answers ) ) :
				question.text += ( str ( j + 1 ) + ". " + question.answers[j] + '\n')
		markup.add( types.InlineKeyboardButton( str ( i + 1 ) + '. ' + question.answers[i], callback_data=( 'answer' + str( i ) ) ) )

	if question.img:
		img = open( '1.jpg' , mode='rb' )
		await bot.send_photo( chatID, img, caption = question.text, reply_markup= markup )
	else :
		await bot.send_message( chatID, question.text, reply_markup= markup)

# questNumber = 0
global questNumber
global makedError
global questionsList
global errs

makedError = False
questionsList = None
questNumber = 0
errs = 0

async def passBilet ( biletNum = -1, theme = None, exam = False, chatID = None ):
	global questNumber
	global errs
	global questionsList

	if questNumber == 20:
		if errs > 2 :
			await bot.send_message( chatID, 'К сожелению в не сдали этот тест( . \nКоличество ошибок: {0}. \nВсего вопросов: 20. Правильность ответов: {1}%'.format( errs, ( 100 - ( errs / 20 * 100 ) ) ) )
		elif errs == 0: 
			await bot.send_message( chatID, '🎉🎉🎊🎊Ейс!!! Это взрыв, поздравляем !!!🎉🎉🎊🎊')
		else :
			await bot.send_message( chatID, 'Поздравляю, вы сдали тест ! \nКоличество ошибок: {0}. \nВсего вопросов: 20. Правильность ответов: {1}%'.format( errs, ( 100 - ( errs / 20 * 100 ) ) ) )
		questionsList = None
		questNumber = 0
		errs = 0
		return 0

	global mode
	mode = 'pass'

	if questionsList == None:
		questionsList = parsing.getBiletOrTheme( bilet = biletNum, theme = theme, exam = exam )
		
	question = parsing.getQuestion( number = questNumber, qusestionsList = questionsList )
	question.text = str( questNumber + 1 ) + '/20 \n' + question.text

	await sendQuestion ( question, chatID = chatID )
	# print (questNumber)
	questNumber += 1

@dp.callback_query_handler()
async def process_callback(call):
	try:
		if call.message:
			
			if call.data == '>>':
				await bot.send_message(call.message.chat.id, 'aaa')
			elif call.data == '...':
				await bot.send_message(call.message.chat.id, 'aaa')
			elif 'answer' in call.data :
				global errs
				global mode

				if str( nowQuestion.correctAnswerI ) in call.data :
					await bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="✅ Правильно! ✅") 

					if mode == 'pass':
						global makedError 
						if not makedError:
							await bot.delete_message( message_id=call.message.message_id, chat_id=call.message.chat.id ) 

					makedError = False
					# print ( makedError )

					await passBilet( chatID =  call.message.chat.id, biletNum = 1  )

				else :
					await bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="❌ Ошибка! ❌")

					if mode == 'pass':

						makedError = True
						errs += 1
						
			elif str ( call.data in range ( 1, 100 )) :
				await passBilet( chatID =  call.message.chat.id, biletNum = call.data,  )

	except Exception as e:
		print(repr(e))

# run long-polling
executor.start_polling( dp )

