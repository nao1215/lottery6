.PHONY: check verify game committed gozen-check run web web-size desktop clean help

# gozen comes from go.mod (the tool directive), so the CLI and the player runtime are one version.
GOZEN = go tool gozen
# The whole browser version (dist/web after make web): GitHub Pages takes a site of 1 GB at most.
SITE_LIMIT = 950000000
DESKTOP_TARGETS = linux-amd64 linux-arm64 windows-amd64 windows-arm64 darwin-amd64 darwin-arm64

check: ## Write game/ from tools/ and check it with gozen
	$(MAKE) game
	$(MAKE) gozen-check

# What CI runs before Pages and a release publish anything (.github/workflows/verify.yml):
# check, and game/ must be the one committed.
verify: ## check, and fail when game/ differs from the commit
	$(MAKE) game
	$(MAKE) committed
	$(MAKE) gozen-check

game: ## Write game/game.yaml, game/data/world.yaml and game/lang/en.yaml from tools/build.py and tools/en.py
	python3 tools/build.py

committed: ## Fail when game/ is not the one committed (after make game)
	@git status --porcelain -- game
	@test -z "$$(git status --porcelain -- game)" || { echo "game/ differs from the commit: commit what make game wrote" >&2; exit 1; }

gozen-check: ## Run gozen check on game/
	$(GOZEN) check game

run: ## Play game/ in a window
	$(GOZEN) run game

web: ## Export the browser version into dist/web, failing past SITE_LIMIT bytes
	rm -rf dist/web
	rt=$$(tools/runtime.sh web) || exit 1; \
	$(GOZEN) export game --runtime "$$rt" --target web --out dist/web
	cp LICENSE dist/web/LICENSE
	cp NOTICE.md dist/web/NOTICE.txt
	cp game/assets/fonts/LICENSE.txt dist/web/LICENSE-mplus.txt
	$(MAKE) web-size

web-size: ## Fail when dist/web is past SITE_LIMIT bytes
	python3 tools/size.py dist/web $(SITE_LIMIT)

desktop: ## Export a zip of the game for each desktop OS into dist/
	mkdir -p dist
	for t in $(DESKTOP_TARGETS); do \
		rm -rf dist/lottery6_$$t dist/lottery6_$$t.zip; \
		rt=$$(tools/runtime.sh $$t) || exit 1; \
		$(GOZEN) export game --runtime "$$rt" --target $$t --out dist/lottery6_$$t || exit 1; \
		cp LICENSE dist/lottery6_$$t/LICENSE; \
		cp NOTICE.md dist/lottery6_$$t/NOTICE.txt; \
		cp game/assets/fonts/LICENSE.txt dist/lottery6_$$t/LICENSE-mplus.txt; \
		(cd dist && zip -qr lottery6_$$t.zip lottery6_$$t) || exit 1; \
		rm -rf dist/lottery6_$$t; \
	done

clean: ## Remove dist/ and the downloaded runtimes
	rm -rf dist .cache

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-12s %s\n", $$1, $$2}'
