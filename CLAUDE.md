# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShellCraft is a command-line based crafting game inspired by Ted Chiang's "Seventy-Two Letters". It's a Python application that uses Click for CLI interactions, Pydantic for game state serialization, and features a tutorial system to guide players through mining, crafting, and research mechanics.

## Development Commands

The project supports both Poetry and UV package managers. Use either consistently:

### With Poetry (legacy):
- **Install dependencies**: `poetry install`
- **Run tests**: `poetry run pytest`
- **Format code**: `poetry run black tests src`
- **Lint code**: `poetry run flake8 tests src --ignore E501,W503,E741`
- **Coverage**: `poetry run coverage run --source shellcraft -m pytest`
- **Build documentation**: `poetry run mkdocs build --clean`
- **Serve documentation**: `poetry run mkdocs serve`

### With UV (preferred):
- **Install dependencies**: `uv install`
- **Run tests**: `uv run pytest`
- **Format code**: `uv run black tests src`
- **Lint code**: `uv run flake8 tests src --ignore E501,W503,E741`

### Makefile shortcuts:
- `make test` - Run tests with poetry
- `make lint` - Run linting
- `make format` - Format code with black
- `make clean` - Remove build artifacts

## Architecture

### Core Components:
- **CLI Interface** (`cli.py`): Main Click-based command interface with game state management
- **Game Engine** (`shellcraft.py`): Core game logic and state management
- **Core Classes** (`core.py`): Resource management, item definitions, and proxy classes
- **Game State** (`game_state.py`): Pydantic classes for game state serialization
- **Tutorial System** (`tutorial.py`): Progressive game tutorial and onboarding
- **Event System** (`events.py`): Game event handling and triggers
- **Research/Crafting** (`research.py`, `missions.py`): Game progression mechanics

### Key Patterns:
- Game state is persisted using Pydantic in `~/Library/Application Support/ShellCraft/config.json`
- Commands are dynamically enabled/disabled based on game progression
- Actions (mine, craft, research) use a wrapper system for consistent state management
- Resource management uses proxy classes for type-safe  interaction
- Tutorial system controls command availability and guides player progression

### Game Mechanics:
- **Mining**: Extract clay, ore, and energy resources
- **Crafting**: Create tools and items using resources
- **Research**: Unlock new capabilities and recipes
- **Automata**: Advanced game mechanics for automation
- **Missions**: Structured objectives and contracts

### Entry Points:
- Main CLI entry point: `shellcraft.cli:main`
- Debug commands: `shellcraft debug <command>` (hidden in normal gameplay)
- Game commands are progressively unlocked through tutorial completion

### Testing:
- Tests in `tests/` directory using pytest
- Fixtures for game state testing in `tests/fixtures/`
- CI runs tests on Python 3.7-3.9 (GitHub Actions)