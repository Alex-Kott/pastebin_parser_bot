import config as cfg 
import telebot
from telebot import types
import re
from peewee import *
import time
import random as rnd
from multiprocessing import Process
from bs4 import BeautifulSoup
import math
import requests as req
import datetime as dt

bot = telebot.TeleBot(cfg.token)

db = SqliteDatabase('bot.db')

class BaseModel(Model):

	class Meta:
		database = db

class Paste(BaseModel):
	link = TextField(unique = True)
	text = TextField()
	important = IntegerField()

class Parser:
	def __call__(self):
		while True:
			print(str(dt.datetime.now()))
			r = req.get("https://pastebin.com/archive")
			soup = BeautifulSoup(r.text, "lxml")
			maintable = soup.find_all(class_="maintable")[0]
			trs = maintable.find_all("tr")
			for tr in trs:
				tds = tr.find_all("td")

				for td in tds:
					href = td.a['href']
					r = req.get("https://pastebin.com/raw{}".format(href))
					text = r.text

					accept = 0 # добавляем ли запись в базу

					if re.findall(r'admin', text):
						accept += 1
					if re.findall(r'pass', text):
						accept += 1
					if re.findall(r'root', text):
						accept += 1
					if re.findall(r'jauntech', text):
						accept += 1

					if accept:
						try:
							Paste.create(link = href, text = text, important = accept)
						except Exception as e:
							print(str(e))

					break
				t = 0.1 * rnd.randint(10, 50)
				time.sleep(t)



			





@bot.message_handler(commands = ['init'])
def init(message):
	Paste.create_table(fail_silently = True)

@bot.message_handler(content_types = ["text"])
def response(message):
	bot.send_message(message.chat.id, message.text)



parser = Parser()
p1 = Process(target = parser)
p1.start()




Paste.create_table(fail_silently = True)
if __name__ == '__main__':
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		print(str(e))

