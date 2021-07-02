import sys

from freedom import playgame
from freedom import FBState

def main():

    global dims

    # checking commandline arguments
    if len(sys.argv) < 2:
        print("No board dimensions entered, defaulting to 8")
        dims = [8, 8]
    elif int(sys.argv[1]) >= 11:
        print("Board dimensions greater than 10 are currently not supported")
        print("Defaulting to 8")
        dims = [8, 8]
    else:
        print("setting board to " + sys.argv[1] + "X" + sys.argv[1])
        dims = [int(sys.argv[1]), int(sys.argv[1])]

    if len(sys.argv) < 3:
        print("No difficulty specified, reverting to level 3")
        depth = 3
    else:
        print("difficulty set to level: " + sys.argv[2])
        depth = int(sys.argv[2])

    # starting game and getting the final state returned when game ends
    final_state = playgame(depth)

    # determining who has the mode lives
    # 1+ means AI won, 1- means player won, and 0 indicates a draw
    final_state.evaluate()

    if final_state.utility > 0:
        print("The AI won, you lost!")
    elif final_state.utility < 0:
        print("You won! Great Job!")
    else: # case draw
        print("It was a tie!")


main()
