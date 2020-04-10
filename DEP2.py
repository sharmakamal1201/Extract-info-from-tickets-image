
#!pip install pytesseract


#!pip install regex


import pytesseract
import os
import random
import regex as re
import csv
import argparse
import sys
try:
	from PIL import Image
except ImportError:
	import Image


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def levD(str1, str2):
	m = len(str1)
	n = len(str2)
	dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
	for i in range(m + 1):
		for j in range(n + 1):
			if i == 0:
				dp[i][j] = j
			elif j == 0:
				dp[i][j] = i
			elif str1[i-1] == str2[j-1]:
				dp[i][j] = dp[i-1][j-1]
			else:
				dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])

	return dp[m][n]


def find_dist(s1, s2):
	#s1 <= DB
	#s2 <= extracted
	n = len(s2)
	m = len(s1)
	if(m<=3 or n<=3):
		return -1
	if m<n:
		return levD(s1,s2[:m])
	else:
		mini = n
		for i in range(m-n+1):
			str1 = s1[i:i+n]
			dist = levD(str1,s2)
			if(dist<mini):
				mini = dist
			#print(str1, len(str1), dist)
		return mini


def SearchInDB(str):
	str1 = ""
	for i in range(len(str)):
		if(str[i].isalnum()):
			str1 += str[i]
	str = str1.upper()
	res = ""
	if(len(str)<=3):
		return res
	mini = len(str)
	with open('bus_stations.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			dist = find_dist(row[0].upper(), str)
			#print(dist, row[0])
			if(dist != -1 and dist<mini and dist<len(row[0])):
				mini = dist
				res = row[0]

	return res


allowed_chars = ['.', ':', '/', '-']


def clean_text(txt):
	res = ""
	for i in range(len(txt)):
		''' for cleaning price (sometimes '.' is read as ',' 
		, also to handle 1,500 like cases)'''
		if(txt[i] == ',' and i+2<len(txt)):
			if(txt[i+1]>='0' and txt[i+1]<='9' and txt[i+2]>='0' and txt[i+2]<='9'):
				if(i+3<len(txt) and txt[i+3]>='0' and txt[i+3]<='9'):
					continue
				else:
					res += '.'
					continue

		if(txt[i]=='\n'):
			res += '\n'
			continue

		# to remove unwanted special chars  
		cnt = 0         
		if(txt[i].isalnum() == False):
			for j in allowed_chars:
				if(txt[i] == j):
					res += txt[i]
					cnt = 1
					break
			if cnt == 0:
				res += ' '

		else:
			res += txt[i]

	return res




def clean_price(i):
	for j in range(len(i)):
		if(i[j]=='.'):
			break
	prc = (i[:j])

	return prc



def most_frequent(List): 
	return max(set(List), key = List.count)



def _regex(result):

	From1 = re.search(r'(?P<From>([a-z]|[A-Z]|[0-9])+(.*))([t|T][o|O|0])', result)
	To1 = re.search(r'([t|T][o|O|0])(?P<To>(.*)([a-z]|[A-Z]|[0-9])+)', result)
	flgfr = 0
	flgTo = 0

	if not From1:
		From1 = re.search(r'(?P<From>([a-z]|[A-Z])+(.*))([1|t|T][o|O|0])', result)
		flgfr = 1
	if From1:
		From1 = From1.group('From')
		From2 = ""
		for i in range(len(From1)):
			if(From1[i].isalnum()):
				From2 += From1[i]

	if not To1:
		To1 = re.search(r'([1|t|T][o|O|0])(?P<To>(.*)([a-z]|[A-Z])+)', result)
		flgTo = 1
	if To1:
		To1 = To1.group('To')
		To2 = ""
		for i in range(len(To1)):
			if(To1[i].isalnum()):
				To2 += To1[i]
	
	if(From1):
		#print("From_initial: ", From2)
		From2 = SearchInDB(From2)
		levDF = levD(str(From2), From2)
		if(flgfr!=0 or levDF>2):
			print("From: " + str(From2) + " >>>> Not_SURE")
		else:
			print("From : ", From2)
	if(To1):
		#print("To_initial: ", len(To2))
		To2 = SearchInDB(To2)
		levDT = levD(str(To2), To2)
		if(flgTo!=0 or levDT>2):
			print("To: " + str(len(str(To2))) + " >>>> Not_SURE")
		else:
			print("To : ", To2)

		
	date =  re.search(r'[0-3][0-9]/[0|1][0-9]/[2]{0,1}[0]{0,1}[01|2][0-9]', result)
	chksum = 0
	if not date:
		chksum = 1
		date = re.search(r'[0-3][0-9]/[0|1][0-9]', result)
	if not date:
		chksum = 2
		date = re.search(r'[0|1][0-9]/[2]{0,1}[0]{0,1}[0|1|2][0-9]', result)
	if date:
		print("date : ", date.group(), end = ' ')
		if(chksum==0):
			print("format: data/month/year")
		if(chksum==1):
			print("format: data/month")
		if(chksum==2):
			print("format: month/year")

		
		
	time = re.search(r'[0-2]{0,1}[0-9](:[0-5]{0,1}[0-9])+', result)
	if time:
		print("time : ", time.group())

		
		
	per_h_price = 0
	net_rate = 0
	total_travellers = 0
	per_head_price = re.search(r'([0-9]+)(.*?)([x|X|\*| ])(.*?)([0-9]+\.[0-9]+)', result)   
	total_price = re.findall(r'([0-9]+\.[0-9]+)', result)
	net_price = []
	for i in range(len(total_price)):
		net_price.append(clean_price(total_price[i]))
	if len(net_price) > 0 :
		net_rate =  most_frequent(net_price)
		print("net_price : ", net_rate)
	
	if per_head_price and net_rate!=0 :
		per_h_price = clean_price(per_head_price.group(5))
		total_travellers = per_head_price.group(1)
		if( int(net_rate) == (int(total_travellers) * int(per_h_price)) ):
			print("total_travellers : ", total_travellers)
			print("per_head_price : ", per_h_price)
		else:
			print(" >>>> net_price output is not confident")



def create_arg_parser():
    parser = argparse.ArgumentParser(description='Description of your app.')
    parser.add_argument('image_path', help='Path to the input directory.')
    return parser


if __name__ == "__main__":

	arg_parser = create_arg_parser()
	parsed_args = arg_parser.parse_args(sys.argv[1:])
	img_path = parsed_args.image_path

	result = pytesseract.image_to_string(Image.open(img_path))
	result = clean_text(result)
	#print(result)
	#print()
	print()
	_regex(result)