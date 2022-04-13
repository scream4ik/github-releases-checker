build:
	docker build -t scream4ik/github-releases-checker .

push:
	docker push scream4ik/github-releases-checker
