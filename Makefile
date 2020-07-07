distribution:
	fbs freeze
	fbs installer


wheel:
	python setup.py sdist


upload:
	twine upload $(shell ls -t dist/* | head -1) -r testpypi
	twine upload $(shell ls -t dist/* | head -1) -r pypi


version: 
	python Update.py $(version)

#	git add 'src/build/settings/base.json
#	git commit -m 'Update version'
#	git tag -a $(version) -m \'$(version)\'
#	make wheel
#	git push
#	git push --tags
