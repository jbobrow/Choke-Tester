# Makefile for Choke Test Safety Check - macOS Build
#
# Common tasks for building and testing the macOS app
#

.PHONY: help setup build build-dev clean dmg install test run

# Default target
help:
	@echo "Choke Test Safety Check - macOS Build"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup      - Set up development environment"
	@echo "  make run        - Run app from source (no build)"
	@echo "  make build      - Build production macOS app"
	@echo "  make build-dev  - Build development app (alias mode)"
	@echo "  make dmg        - Create DMG installer"
	@echo "  make dmg-styled - Create styled DMG installer"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make test       - Run tests"
	@echo "  make install    - Install to /Applications"
	@echo "  make all        - Clean, build, and create DMG"
	@echo ""

# Set up development environment
setup:
	@echo "Setting up development environment..."
	python3 -m venv venv
	@echo "Activating virtual environment..."
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements-macos.txt
	@echo ""
	@echo "✓ Setup complete!"
	@echo "  Activate with: source venv/bin/activate"

# Run from source
run:
	@./launch_macos.sh

# Build production app
build:
	@./build_macos.sh

# Build development app (alias mode)
build-dev:
	@./build_macos.sh --dev

# Build and test
build-test:
	@./build_macos.sh --test

# Create DMG
dmg:
	@./create_dmg.sh

# Create styled DMG
dmg-styled:
	@./create_dmg.sh --styled

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v

# Install to Applications folder
install:
	@if [ -d "dist/Choke Test Safety Check.app" ]; then \
		echo "Installing to /Applications..."; \
		cp -R "dist/Choke Test Safety Check.app" /Applications/; \
		echo "✓ Installed"; \
	else \
		echo "❌ App not found. Run 'make build' first"; \
		exit 1; \
	fi

# Full build pipeline
all: clean build dmg
	@echo ""
	@echo "✓ Complete build finished"
	@echo "  App:  dist/Choke Test Safety Check.app"
	@echo "  DMG:  dist/ChokeTestSafetyCheck-macOS.dmg"

# Development workflow
dev: build-dev
	@open "dist/Choke Test Safety Check.app"

# Quick development cycle
quick:
	@python3 run.py
