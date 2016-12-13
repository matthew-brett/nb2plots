html: clean
	sphinx-build -W -b html -d html proj1 html

pxml: clean
	sphinx-build -W -b pseudoxml -d html proj1 html

permissive: clean
	sphinx-build -b html -d html proj1 html

debug: clean
	sphinx-build -P -W -b html -d html proj1 html

clean:
	rm -rf html

init: clean
	rm -rf proj1
	cp -r ../proj1 .
