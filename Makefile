install:
	# python -m venv venv
	venv\Scripts\activate
	python.exe -m pip install --upgrade pip
	pip install --upgrade -r requirements.txt

install_one_line:
	python -m venv venv && venv\Scripts\activate && python.exe -m pip install --upgrade pip && pip install --upgrade -r requirements.txt
