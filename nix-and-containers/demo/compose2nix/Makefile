.PHONY: run
run: clean
	compose2nix --inputs=compose.yml --output=compose.nix --env_files=.env --runtime=docker -project=gitea

.PHONY: clean
clean:
	rm -f compose.nix
