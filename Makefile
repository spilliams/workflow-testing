.PHONY: build
build:
	docker build \
		-t workflow-testing:latest \
		-f docker/Dockerfile \
		--progress=plain \
		.
