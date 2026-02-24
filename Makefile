## Convenience Makefile for workspace operations

.PHONY: \
	bdd-ui-headful-smoke \
	bdd-http-generic-smoke \
	sync.all \
	guard-TAG \
	milestone-tag \
	milestone-tag-push \
	milestone-tag-show

TAG_REPOS := backend frontend .

# Sync all dependencies for the workspace root and all workspace members,
# including every dependency group (e.g., backend dev/test, root bdd).
sync.all:
	@echo "Syncing all workspace dependencies and groups..."
	@uv sync --all-packages --all-groups

# Run the UI behave scenario in headed (non-headless) mode.
# Usage:
#   make bdd-ui-headful                # runs default scenario against 127.0.0.1:5173
#   UI_BASE_URL=http://127.0.0.1:5173 \
#   SCENARIO_NAME="Reject creating a user with a duplicate username" \
#   make bdd-ui-headful-smock

bdd-ui-headful-smoke:
	@echo "Running UI BDD (headful)..."
	@UI_HEADLESS=false \
	UI_BASE_URL=${UI_BASE_URL:http://127.0.0.1:5173} \
	SCENARIO_NAME="${SCENARIO_NAME:Reject creating a user with a duplicate username}" \
	uv run behave --stage ui ./features/user.feature --name "$$SCENARIO_NAME"

# Run HTTP generic smoke scenario from demo module.
bdd-http-generic-smoke:
	@echo "Running HTTP generic component smoke..."
	@uv run behave --stage http ./features/demo/generic_components_smoke.feature


# Guard for required TAG parameter.
# Usage:
#   make milestone-tag TAG=v0.1.0-spreadsheet-pm-milestone
guard-TAG:
	@if [ -z "$(TAG)" ]; then \
		echo "TAG is required. Example: make milestone-tag TAG=v0.1.0-spreadsheet-pm-milestone"; \
		exit 1; \
	fi

# Create the same annotated tag in tuner/backend/frontend repos.
# Optional:
#   MESSAGE="custom tag message"
milestone-tag: guard-TAG
	@for repo in $(TAG_REPOS); do \
		if [ "$$repo" = "." ]; then label="tuner"; else label="$$repo"; fi; \
		if git -C "$$repo" rev-parse --verify --quiet "refs/tags/$(TAG)" >/dev/null; then \
			echo "[$$label] tag exists: $(TAG)"; \
		else \
			msg="$${MESSAGE:-Milestone $(TAG) ($$label)}"; \
			git -C "$$repo" -c tag.gpgSign=false tag -a "$(TAG)" -m "$$msg"; \
			echo "[$$label] tag created: $(TAG)"; \
		fi; \
	done

# Push existing tag to origin in tuner/backend/frontend repos.
milestone-tag-push: guard-TAG
	@for repo in $(TAG_REPOS); do \
		if [ "$$repo" = "." ]; then label="tuner"; else label="$$repo"; fi; \
		echo "[$$label] pushing tag: $(TAG)"; \
		git -C "$$repo" push origin "$(TAG)"; \
	done

# Display where the tag exists and what commit it points to.
milestone-tag-show: guard-TAG
	@for repo in $(TAG_REPOS); do \
		if [ "$$repo" = "." ]; then label="tuner"; else label="$$repo"; fi; \
		echo "=== $$label ==="; \
		git -C "$$repo" --no-pager show --no-patch --decorate "$(TAG)" | head -n 4; \
		echo; \
	done



