# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShellCraft is a command-line based crafting game inspired by Ted Chiang's "Seventy-Two Letters". It's a Python application that uses Click for CLI interactions, Pydantic for game state serialization, and features a tutorial system to guide players through mining, crafting, and research mechanics.

## Development Commands

The project uses [Mise](https://mise.jdx.dev) to manage the Python toolchain (via `uv`) and to expose development tasks. Run `mise install` once to provision Python and `uv`; `mise run <task>` thereafter.

### Mise tasks:
- **Install dependencies**: `mise run install` (wraps `uv sync`)
- **Run tests**: `mise run test`
- **Format code**: `mise run format` (ruff format)
- **Lint code**: `mise run lint` (ruff check)
- **Type check**: `mise run typecheck` (ty)
- **Coverage**: `mise run coverage`
- **Build documentation**: `mise run docs`
- **Serve documentation**: `mise run servedocs`
- **Build package**: `mise run build`
- **Clean artifacts**: `mise run clean`
- **Backup savegame**: `mise run backup`
- **Restore savegame**: `mise run restore`

To override the Python version, set `PYTHON_VERSION` before running mise (e.g., `PYTHON_VERSION=3.11 mise install`).

## Required checks after every code change

Before marking any task complete, run **all three** of these and resolve any reported issues:

1. `mise run format` — applies ruff formatting in place.
2. `mise run typecheck` — runs ty across `src/` and `tests/`; must report "All checks passed!".
3. `mise run test` — must show all tests passing.

If any check fails, fix the underlying issue rather than skipping or silencing the check. Don't ignore ty errors with `# type: ignore` unless the type is genuinely unexpressible — prefer fixing the annotation or the code.

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