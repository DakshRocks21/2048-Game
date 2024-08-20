# 2048 Game with AI and Sequence Generator

This project is an implementation of the popular game **2048** with an integrated AI that suggests moves and a sequence generator that produces possible sequences of moves.

## Features

1. **Basic 2048 Game Mechanics**:
   - The game follows standard 2048 rules: combine tiles with the same number to create higher numbers, aiming to reach 2048 (or beyond).
   - The game ends when no more moves are possible.

2. **AI Integration**:
   - An AI (`WordleAI`) is included that suggests optimal moves based on several heuristics like monotonicity, clustering, and corner preference.

3. **Sequence Generator**:
   - Generates and saves possible sequences of moves up to a specified depth, allowing the user to explore different game outcomes.
