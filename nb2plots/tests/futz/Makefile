html: clean
	sphinx-build -W -b html -d html proj1 html

pxml: clean
	sphinx-build -W -b pseudoxml -d html proj1 html

phtml: clean
	# Permissive HTML
	sphinx-build -b html -d html proj1 html

ppxml: clean
	# Permissive PXML
	sphinx-build -b pseudoxml -d html proj1 html

debug: clean
	sphinx-build -P -W -b html -d html proj1 html

clean:
	rm -rf html

init: clean
	rm -rf proj1
	cp -r ../proj1 .
