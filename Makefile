EXT_NAME:=audio-control
EXT_DIR:=$(shell pwd)

.PHONY: help lint format link unlink deps dev
.DEFAULT_TARGET: help

link: ## Symlink the project source directory with Ulauncher extensions dir.
	@ln -s ${EXT_DIR} ~/.local/share/ulauncher/extensions/${EXT_NAME}

unlink: ## Unlink extension from Ulauncher
	@rm -rf ~/.local/share/ulauncher/extensions/${EXT_NAME}

deps: ## Install Python Dependencies
	@pip3 install -r requirements.txt

dev: ## Runs ulauncher on development mode
	ulauncher --no-extensions --dev -v |& grep -i audio-control
