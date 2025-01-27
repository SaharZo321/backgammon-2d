# Backgammon 2D

Backgammon 2D is a Python-based implementation of the classic board game, built using the Pygame library. This project provides a digital way to enjoy Backgammon with features like piece movement validation, interactive UI, and an optional LAN multiplayer mode.

## Features

- **Local Play**: Play against a friend on the same device or against an AI if you are lonely.
- **Online Multiplayer**: Connect and play with friends over the same network.

<img src="./assets/videos/gamemodes.gif" height="300"/>

- **Valid Moves Highlighting**: Highlight possible moves for a selected piece.
- **Real-Time Updates**: Dynamic rendering of board and game state.
- **Custom Player Colors**: Change your piece color to your desire.

<img src="./assets/videos/colors.gif" height="300"/>


## Installation

Download the precompiled executable file from the [Releases](https://github.com/SaharZo321/sahar-backgammon/releases) page and run it directly on your system.

## How to Play

### Local Game Mode

1. Start the game by running the executable file.
2. Player 1 and Player 2 take turns to roll the dice and move their pieces.
3. The game highlights possible moves for selected pieces.
4. The first player to bear off all their pieces wins and gets points based on their win type.

<img src="./assets/videos/bot.gif" height="300"/>


### Online Multiplayer Mode

1. Ensure both players are connected to the same network.
3. On the client side, connect to the server by entering the host IP address and port.
4. Play as described in the local mode.

<img src="./assets/videos/multiplayer.gif" height="300"/>


## Technologies Used

- **Pygame**: Game development library
- **Asyncio**: For managing asynchronous tasks (server implementation)

Enjoy playing Backgammon 2D!
