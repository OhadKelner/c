import pygame as p
from Chess import ChessEngine
from Chess import AI

BOARD_WIDTH = 800
BOARD_HEIGHT = 512

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
push_right = 700
push_down = 300
ai = AI.AI()

def loadImages():
    pieces = ['Wp', 'Wr', 'Wn', 'Wb', 'Wk', 'Wq', 'Bp', 'Br', 'Bn', 'Bb', 'Bk', 'Bq']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    IMAGES['shadow'] = p.transform.scale(p.image.load("images/shadow.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES['bg'] = p.transform.scale(p.image.load("images/bg.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    global push_right

    p.init()
    font = p.font.Font('freesansbold.ttf', 15)

    p.display.set_caption('לוח השחמט של אוהד')
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + 100), p.RESIZABLE)

    clock = p.time.Clock()
    screen.fill(p.Color("BLACK"))
    gs = ChessEngine.GameState()
    loadImages()
    running = True
    status = "game"
    sqSelected = (-1, -1)
    playerClicks = []

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                return
            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    p.quit()
                    return

            if status == "game":
                if gs.whiteToMove:
                    if e.type == p.MOUSEBUTTONDOWN:
                        location = p.mouse.get_pos()
                        col = (location[0] - push_right) // SQ_SIZE
                        row = (location[1]-push_down) // SQ_SIZE
                        out = False
                        if (row < 0 or row > 7) or (col < 0 or col > 7):
                            out = True
                            print("out")
                        if sqSelected == (row, col) or out:
                            sqSelected = (-1, -1)
                            playerClicks = []
                        else:
                            sqSelected = (row, col)

                            playerClicks.append(sqSelected)

                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            gs.makeMove(move)

                            sqSelected = (-1, -1)
                            playerClicks = []
                else:  # ai BLACK MOVE
                    ai_move = ai.calc_ai_move(gs)
                    if not ai_move:
                        status = "CHECKMATE on Black  |  White wins"

                    else:
                        move = ChessEngine.Move(ai_move[0], ai_move[1], gs.board)
                        gs.makeMove(move)

        drawGameState(screen, gs, sqSelected, font)
        drawInfo(screen, gs, font, status)

        p.display.flip()
        clock.tick(MAX_FPS)


def drawGameState(screen, gs, sqSelected, font):
    screen.blit(IMAGES["bg"], (0, 0))

    drawBoard(screen, sqSelected, gs, font)
    drawPieces(screen, gs.board)


def drawBoard(screen, sqSelected, gs, font):
    global push_right
    global push_down

    piece = gs.board[sqSelected[0]][sqSelected[1]]
    piece_color = piece[0]
    ways = []
    if sqSelected != (-1, -1):
        piece_beams = gs.get_beams(sqSelected, True, gs.board)

        for beam in range(len(piece_beams)):
            for aim in range(len(piece_beams[beam])):
                if piece_beams[beam][aim]["is_way"]:
                    ways.append(piece_beams[beam][aim]["aim"])

    red_sq = (-1, -1)
    if piece_color != '-':
        if gs.checked[piece_color]:
            red_sq = gs.kings_pos[piece_color]


    rect1 = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
    rect1.fill((255, 255, 255, 30))

    rect2 = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
    rect2.fill((0, 0, 0, 30))

    rect_colores = [rect1, rect2]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            rect_color = rect_colores[(r + c) % 2]
            if (r, c) == red_sq:

                rect_color = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                rect_color.fill((186, 13, 76, 100))

            if (r, c) == sqSelected:
                rect_color = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                rect_color.fill((255, 255, 255, 100))

            screen.blit(rect_color, (c * SQ_SIZE + push_right, r * SQ_SIZE+push_down))


            if (r, c) in ways and (sqSelected != (r, c)):
                screen.blit(IMAGES["shadow"], p.Rect(c * SQ_SIZE + push_right, r * SQ_SIZE+push_down, SQ_SIZE, SQ_SIZE))

            files_letters = font.render(chr(c + 65), True, "WHITE")

            screen.blit(files_letters, (64 * c + 700, 820))

            nums_letters = font.render(str(8 - r), True, "WHITE")

            screen.blit(nums_letters, (680, 64 * r + 340))


def drawPieces(screen, board):
    global push_right
    global push_down

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                if piece[1] == 'r':
                    piece = piece[:2]
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE + push_right, r * SQ_SIZE+push_down, SQ_SIZE, SQ_SIZE))


def drawInfo(screen, gs, font, status):
    exit = font.render('X', True, "WHITE")
    screen.blit(exit, (1600, 100))

    x = 1230
    y = 300
    # p.draw.rect(screen, "BLACK", p.Rect(x, y, 1000, 1000))
    if status == "game":
        turn_text = "White to move"

        if not gs.whiteToMove:
            turn_text = "Black to move"
    else:
        turn_text = status
    turn_text_r = font.render(turn_text, True, "WHITE")

    screen.blit(turn_text_r, (x + 15, y + 15))

    score_text_r = font.render(str(ai.get_board_rating(gs.board,gs)), True, "CYAN")
    screen.blit(score_text_r, (x, y + 256))

    text_log = ""
    for i in range(len(gs.moveLog)):
        text_log += f'{i + 1})   {gs.moveLog[i].getNotation(gs)}  \n'

    blit_text(screen, text_log, (x + 30, y + 50), font)


def blit_text(surface, text, pos, font, color=p.Color('white')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


if __name__ == "__main__":
    main()
