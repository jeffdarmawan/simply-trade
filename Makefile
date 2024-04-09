run:
	python -m venv venv
	. ./venv/bin/activate
	# pip install . 
	pip install waitress
	waitress-serve --host 127.0.0.1 --call app:create_app