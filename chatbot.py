def chatbot(question):
	answer = ''
	text = ''
	results = list(search(question, tld="co.in", num=10, stop=3, pause=1))
	soup = BeautifulSoup((requests.get(results[0])).content, features="lxml")
	for a in soup.findAll('p'):
		text += '\n' + ''.join(a.findAll(text = True))
	text = text.replace('\n', '')
	text = text.split('.')
	answer = (text[0].split('?')[0]).translate({ord(c): None for c in string.whitespace}) #https://www.journaldev.com/23763/python-remove-spaces-from-string
	if len(answer) > 0:
		return answer
	else:
		return "I do not know. Ask me something else please."