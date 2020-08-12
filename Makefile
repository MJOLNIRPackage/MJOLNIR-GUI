distribution:
	fbs freeze
	fbs installer

releasedistribution:
	fbs release $(version)

wheel:
	python preparePIP.py
	python setup.py sdist 
	python setup.py bdist_wheel


upload:
	twine upload $(shell ls -t dist/* | head -2) -r pypiMJOLNIRPackage
	fbs upload


version: 
	python Update.py $(version)

release:
	make wheel
	make distribution
	make upload


