import sys
import Puzzle

if __name__ == "__main__":
    try:
        params = sys.argv
        name = params[1]
        # url = params[2] if len(params) > 2 else None
        # baseURL = params[3] if len(params) > 3 else None
        # maxPeace = params[4] if len(params) > 4 else None

        game = Puzzle.PuzzleGame(name)
        status = game.getPeaces()
        print(status)
        sys.stdout.flush()
    except Exception as e:
        print('ERROR')
        print(e)
        sys.stdout.flush()
    

