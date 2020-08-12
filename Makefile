distribution:
	fbs freeze
	fbs installer


wheel:
	python preparePIP.py
	python setup.py sdist 
	python setup.py bdist_wheel


upload:
	twine upload $(shell ls -t dist/* | head -2) -r pypiMJOLNIRPackage


version: 
	python Update.py $(version)
