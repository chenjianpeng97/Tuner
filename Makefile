## Convenience Makefile for running BDD UI scenarios

.PHONY: bdd-ui-headful

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
