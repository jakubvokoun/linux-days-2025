.PHONY: start-app
start-app:
	docker compose up -d web-app

.PHONY: stop-app
stop-app:
	docker compose down

.PHONY: local
local:
	docker compose up -d web-app
	python -m pytest tests/ -v --headed
	docker compose down

.PHONY: docker
docker:
	docker compose up -d web-app
	docker compose run --rm playwright-tests
	docker compose down

.PHONY: ci
ci:
	gitlab-ci-local

.PHONY: show-report
show-report:
	xdg-open test-results/report.html

.PHONY: build-images
build-images:
	docker build -f Dockerfile.app -t local/ping-cms-app .
	docker save local/ping-cms-app | gzip > ping-cms-app.tar.gz
	docker build -f Dockerfile.playwright -t local/ping-cms-playwright .
	docker save local/ping-cms-playwright | gzip > ping-cms-playwright.tar.gz


.PHONY: clean
clean:
	rm -fv *.png
	rm -rfv ./tests/__pycache__
