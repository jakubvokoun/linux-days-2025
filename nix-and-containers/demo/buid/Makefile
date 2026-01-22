.PHONY: build
build: clean
	nix-build default.nix
	docker load < result

.PHONY: check
check:
	docker images | rg nix-web-server

.PHONY: clean
clean:
	docker image rm nix-web-server:latest --force
	rm -rf result

.PHONY: run
run:
	docker run --rm -it -p 8080:8080 nix-web-server:latest
