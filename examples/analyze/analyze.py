#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Annotate a game with an UCI engine."""

from __future__ import print_function

import chess
import chess.pgn
import chess.uci
import time
import argparse
import itertools
import logging
import sys


def annotate_pgn(engine, position, threads, movetime):
    engine.ucinewgame()
    engine.setoption({
        "Threads": threads
    })
    engine.position(position)

    handler = chess.uci.InfoHandler()
    engine.info_handlers.append(handler)

    enginemove, pondermove = engine.go(movetime=movetime)
    with handler as info:
        evaluation = info["score"][1]

    print("%s: %s | %s" % (position.fen(), position.san(enginemove), evaluation))
    return 1.0

if __name__ == "__main__":
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-e", "--engine", required=True,
        help="The UCI engine under test.")
    parser.add_argument("pgn", nargs="+", type=argparse.FileType("r"),
        help="PGN file(s).")
    parser.add_argument("-t", "--threads", default=1, type=int,
        help="Threads for use by the UCI engine.")
    parser.add_argument("-m", "--movetime", default=1000, type=int,
        help="Time to move in milliseconds.")
    parser.add_argument("-d", "--debug", action="store_true",
        help="Show debug logs.")
    args = parser.parse_args()

    # Configure logger.
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    # Find variant.
    position = chess.Board()

    # Open engine.
    engine = chess.uci.popen_engine(args.engine)
    engine.uci()

    # Load PGN.
    for database in args.pgn:
        game = chess.pgn.read_game(database)
        while game != None:
            for move in game.main_line():
                position.push(move)
                annotate_pgn(engine, position, args.threads, args.movetime)
            game = chess.pgn.read_game(database)

    # Run each test line.
    score = 0.0
    count = 0

    engine.quit()
