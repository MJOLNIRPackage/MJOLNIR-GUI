distribution:
	fbs freeze
	fbs installer


wheel:
	python setup.py sdist

version = $(shell python cut.py $(shell ls -t dist/* | head -1))

upload:
	twine upload $(shell ls -t dist/* | head -1) -r testpypi
	twine upload $(shell ls -t dist/* | head -1) -r pypi


version: 
	echo 'Creating version $(version)'
	python Update.py $(version)

#	git add 'src/build/settings/base.json
#	git commit -m 'Update version'
#	git tag -a $(version) -m \'$(version)\'
#	make wheel
#	git push
#	git push --tags
