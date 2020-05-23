import requests
import sqlite3
from bs4 import BeautifulSoup

import sqlite3
from sqlite3 import Error	

import re

class db:	
	def __init__(self):
		try:
			self.conn = sqlite3.connect('im.db')
			self.c = self.conn.cursor()

			self.c.execute("""CREATE TABLE IF NOT EXISTS TT (
						Movie_ID INTEGER,
						Title TEXT,
						Year INTEGER,
						Rating REAL,
						Rated_By TEXT,
						Genre TEXT,
						Country TEXT,
						Realese_Date TEXT,
						Duration TEXT,
						Certification TEXT
						)""")
			self.conn.commit()
		except Error:
			print('Not Created')

	def ins(self, ttdict):
		self.c.execute("""INSERT INTO TT (Movie_ID,Title,Year,Rating,Rated_By,Genre,Country,Realese_Date,Duration,Certification) 
						  VALUES (?,?,?,?,?,?,?,?,?,?)""", ttdict)
		self.conn.commit()


	def fetchlast(self):
		self.c.execute(f"SELECT * FROM TT where RowID={self.max_id()}")
		result = self.c.fetchall()
		if len(result)==1:
			return(result[0][0])
		else:
			return
	def max_id(self):
		self.c.execute('SELECT max(Movie_ID) FROM TT')
		self.maxid = self.c.fetchone()[0]
		return(self.maxid)

	def fetall(self):
		self.c.execute(f"SELECT * FROM TT")
		result = self.c.fetchall()
		print(result)

	def delete(self):
		self.c.execute('DELETE FROM TT').rowcount
		self.conn.commit()
    
class imdb:

	def __init__(self):
		d = db()
		global url, page, soup, title

		try:

			if d.max_id()==None:
				last_id = 120663
			else:
				last_id=int(d.max_id())+1
		except ValueError:
			print("ValueError")
		try:
			for tt in range(last_id,120680):
				print(tt, end=' ')
				url = f'https://www.imdb.com/title/tt{str(tt).zfill(7)}/'
				page = requests.get(url)

				if str(page) == '<Response [404]>':
					d.ins((tt,'---<Response [404]>---',0,0,'NULL','NULL','NULL','NULL',"NULL",'NULL'))
					continue
				soup = BeautifulSoup(page.content, 'html.parser')
				
				title = soup.find_all('h1',class_="")
				
				tilist = (str(title).split("<span id=\"titleYear\">(<a href=\"/year/"))

				self.rating(tt)
				self.genre_reldate(tt)
				self.spl(tilist, tt)

		except requests.exceptions.ConnectionError:
			print("No Internet Connection.\nPlease connect to Internet")

	def rating(self,tt):
		try:
			global rate, usrs
			self.rate=str(soup.find_all("",class_="ratingValue")).split("\n")

			if len(self.rate) == 1:
				usrs = 'NULL'
				rate = 'NULL'
				return


				
			ulist= self.rate[1].split('<span itemprop="ratingValue">')[0].split(' based on ')
			rate = float(ulist[0][-3:])
			usrs = ulist[1][:-14]

		except requests.exceptions.ConnectionError:
			print("No Internet Connection.\nPlease connect to Internet")


	def genre_reldate(self,tt):
		try:
			global genres, reldate, country, duration, certificate

			self.condure = str(soup.find_all(class_="subtext")).split('\n')
		
			duration = '--- ---'
			for i in range(len(self.condure)):
				if 'time datetime' in self.condure[i]:
					
					duration = self.condure[i+1][23:]
				

			if len(str(soup.find_all(class_="subtext")).split('\n')) == 1:
				reldate='------'
				country = '------'
				

			else:
				country=str(soup.find_all(class_="subtext")).split('\n')[-2][70:].split('(')[-1][0:-1]
				reldate=str(soup.find_all(class_="subtext")).split('\n')[-2][70:].split('(')[0]
				
			
			rerel = re.compile(r'\d+')
			if len(rerel.findall(reldate)) == 0:
				reldate='------'
				country = '------'
			
			self.indx = 1
			
			certificate = "-----------"
		
			certificate = str(soup.find_all(class_="subtext")).split('\n')[1][19:]
			if len(certificate)>=10:
				certificate = "-- --- --- --"
			elif 'M">' in certificate:
				certificate = "-----------"

			if len(duration)> 9:													#if the movie is rated this condition is true
				duration=str(soup.find_all(class_="subtext")).split('\n')[3][23:]
				
				if "min" not in duration:
					duration= "-----------"
				self.indx=2
			
			if len(str(soup.find_all(class_="subtext")).split('\n')) <= 6:
				duration= "-----------"

			
			for i in range(len(str(soup.find_all(class_="subtext")).split('<span class="ghost">|</span>'))):
				
				if "genres" in str(soup.find_all(class_="subtext")).split('<span class="ghost">|</span>')[i]:
					self.gen = str(soup.find_all(class_="subtext")).split('<span class="ghost">|</span>')[i].split('\n')[1:-1]
					
			genres=""
			for g in self.gen:
				
				genres+=g.split('>')[1][:-3]+' '
			genres = genres[:-1].replace(' ',', ')
		except requests.exceptions.ConnectionError:
			print("No Internet Connection.\nPlease connect to Internet")

	def spl(self, tilist, tt):
		self.year = 0

		try:
			d = db()
			self.mov = tilist[0][14:]

			if len(tilist) == 1:
				self.mov = tilist[0][14:-6]
				
			if len(str(title)) == 2:
				title_long = soup.find_all('h1',class_="long")
				
				tilist = (str(title_long).split("<span id=\"titleYear\">(<a href=\"/year/"))
				self.mov = tilist[0][18:]
				if len(tilist) == 1:
					self.mov = tilist[0][18:-6]
			
			if len(tilist) == 2:

				self.year = tilist[1][:4]

			self.mov = self.mov.replace(u'\xa0', u'')

			d.ins((tt, self.mov,self.year,rate,usrs,genres,country,reldate,duration,certificate))
		
		except IndexError:
			d.ins((tt,'--Escaped--',0,0,'NULL','NULL','NULL','NULL',"NULL","NULL"))
		
d = db()

obj =imdb()
