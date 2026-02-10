# Makefile for Choke Test Safety Check (Swift/macOS)
#
# Simple build automation for the native macOS app

.PHONY: help build run clean archive install test

PROJECT = ChokeTestApp.xcodeproj
SCHEME = ChokeTestApp
CONFIG = Release
APP_NAME = Choke Test Safety Check

help:
	@echo "Choke Test Safety Check - Native Swift App"
	@echo ""
	@echo "Available targets:"
	@echo "  make build      - Build the app (Release configuration)"
	@echo "  make debug      - Build debug version"
	@echo "  make run        - Build and run the app"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make archive    - Create distributable archive"
	@echo "  make install    - Install to /Applications"
	@echo "  make test       - Run tests (if any)"
	@echo "  make size       - Show app size"
	@echo ""

build:
	@echo "Building $(APP_NAME)..."
	xcodebuild -project $(PROJECT) \
		-scheme $(SCHEME) \
		-configuration $(CONFIG) \
		build

debug:
	@echo "Building debug version..."
	xcodebuild -project $(PROJECT) \
		-scheme $(SCHEME) \
		-configuration Debug \
		build

run:
	@echo "Building and running..."
	xcodebuild -project $(PROJECT) \
		-scheme $(SCHEME) \
		-configuration Debug \
		build
	@open "build/Debug/$(APP_NAME).app"

clean:
	@echo "Cleaning build artifacts..."
	xcodebuild -project $(PROJECT) clean
	rm -rf build/
	@echo "✓ Clean complete"

archive:
	@echo "Creating archive for distribution..."
	xcodebuild -project $(PROJECT) \
		-scheme $(SCHEME) \
		-configuration $(CONFIG) \
		-archivePath build/$(SCHEME).xcarchive \
		archive
	@echo "✓ Archive created at build/$(SCHEME).xcarchive"

install: build
	@echo "Installing to /Applications..."
	@if [ -d "build/$(CONFIG)/$(APP_NAME).app" ]; then \
		cp -R "build/$(CONFIG)/$(APP_NAME).app" /Applications/; \
		echo "✓ Installed to /Applications/$(APP_NAME).app"; \
	else \
		echo "❌ App not found. Run 'make build' first"; \
		exit 1; \
	fi

test:
	@echo "Running tests..."
	xcodebuild test -project $(PROJECT) -scheme $(SCHEME)

size: build
	@echo "App size:"
	@du -sh "build/$(CONFIG)/$(APP_NAME).app"

open-xcode:
	@open $(PROJECT)
