from pygame import mixer




def in_bounds(row, col):
    if (0 <= row <= 7) and (0 <= col <= 7):
        return True
    return False


def search_king_pos(board, color):
    tag = f'{color}k'
    for r in range(8):
        for c in range(8):
            if board[r][c] == tag:
                return (r, c)
    return (None, None)


def imaginary_board(old_sq, new_sq, real_board):
    i_board = []
    for r in range(8):
        i_board.append([])
        for c in range(8):
            i_board[r].append(real_board[r][c])

    piece = real_board[old_sq[0]][old_sq[1]]
    i_board[old_sq[0]][old_sq[1]] = '--'
    i_board[new_sq[0]][new_sq[1]] = piece
    return i_board


class GameState:
    def __init__(self):
        self.board2 = [
            ["Brq", "Bn", "Bb", "Bq", "--", "Bb", "Bn", "Brk"],  # 0
            ["--", "--", "--", "Bp", "Bp", "Bp", "--", "--"],  # 1
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 2
            ["--", "--", "--", "--", "--", "Bq", "--", "--"],  # 3
            ["--", "--", "--", "--", "--", "--", "--", "Bb"],  # 4
            ["--", "--", "--", "Bp", "--", "--", "Wp", "--"],  # 5
            ["Wp", "--", "--", "--", "--", "--", "--", "--"],  # 6
            ["Wrq", "Wn", "Wb", "Wq", "Wk", "Wb", "Wn", "Wrk"],  # 7
            #  0     1    2     3      4     5    6      7
        ]
        self.board = [
            ["Brq", "Bn", "Bb", "Bq", "Bk", "Bb", "Bn", "Brk"],
            ["Bp", "Bp", "Bp", "Bp", "Bp", "Bp", "Bp", "Bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["Wp", "Wp", "Wp", "Wp", "Wp", "Wp", "Wp", "Wp"],
            ["Wrq", "Wn", "Wb", "Wq", "Wk", "Wb", "Wn", "Wrk"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.move_sound = mixer.Sound("sounds/wood.wav")
        self.eat_sound = mixer.Sound("sounds/eat.wav")

        self.score = 0

        self.castle_inf = {"W": {"k": True, "rk": True, "rq": True}, "B": {"k": True, "rk": True, "rq": True}}
        self.checked = {'W': False, 'B': False}
        self.kings_pos = {'W': (7, 4), 'B': (0, 4)}

    ###################################################################################
    def makeMove(self, move):
        if self.legalMove(move):
            def check_castled():
                if move.pieceMoved[0] == move.pieceCaptured[0]:
                    if self.checked[move.pieceMoved[0]]:
                        print("CANT CASTLE WHEN CHECKED")
                        return
                    cking = 6
                    crook = 5
                    if move.pieceCaptured[1:] == 'rq':
                        cking = 2
                        crook = 3
                    self.board[move.startRow][move.startCol] = "--"  # clear king sq
                    self.board[move.endRow][cking] = move.pieceMoved  # king to place
                    self.board[move.endRow][crook] = move.pieceCaptured  # rook to the side
                    self.board[move.endRow][move.endCol] = "--"  # clear rook sq

                    piece_type = move.pieceMoved[1:]
                    piece_color = move.pieceMoved[0]
                    if piece_type[0] in {'k', 'r'}:
                        self.castle_inf[piece_color][piece_type] = False
                    self.move_sound.play()
                    return True

            def check_promotion():
                if piece_type == 'p':
                    if move.endRow in {7, 0}:
                        self.board[move.endRow][move.endCol] = f'{piece_color}q'

            def check_if_check():
                if self.is_check(enemy_king_color, self.board):
                    self.checked[enemy_king_color] = True
                else:
                    self.checked[enemy_king_color] = False
                    self.checked[piece_color] = False

            if check_castled():
                return

            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved

            piece_type = move.pieceMoved[1:]
            piece_color = move.pieceMoved[0]

            check_promotion()

            enemy_king_color = 'W'
            if piece_color == 'W':
                enemy_king_color = 'B'

            check_if_check()

            if piece_type[0] in {'k', 'r'}:
                self.castle_inf[piece_color][piece_type] = False
                if piece_type[0] == 'k':
                    self.kings_pos[piece_color] = (move.endRow, move.endCol)

            self.moveLog.append(move)
            self.whiteToMove = not self.whiteToMove

            if move.pieceCaptured[0].isalpha():
                self.eat_sound.play()
                if move.pieceCaptured[1] == 'r':
                    self.castle_inf[enemy_king_color][move.pieceCaptured[1:]] = False
            else:
                self.move_sound.play()

        else:
            print("ILLIGAL MOVE")

    def legalMove(self, move):
        def is_legal_turn():
            if (piece_color == "W" and not self.whiteToMove) or (piece_color == "B" and self.whiteToMove):
                return False
            return True

        def is_in_ways():
            for beam in range(len(piece_beams)):
                for sq in range(len(piece_beams[beam])):
                    square = piece_beams[beam][sq]
                    if square["is_way"] and square["aim"] == dest:
                        return True

        piece_color = move.pieceMoved[0]

        if not is_legal_turn():
            return False

        dest = (move.endRow, move.endCol)
        origin = (move.startRow, move.startCol)

        piece_beams = self.get_beams(origin, True, self.board)

        if is_in_ways():
            return True

        return False

    def get_beams(self, sqSelected, real, board):
        def get_piece_beams():
            piece_beams = []
            if piece_type == 'p':
                piece_beams = self.pawn_aims(sqSelected, piece_color, real, board)
            elif piece_type == 'n':
                piece_beams = self.knight_aims(sqSelected, piece_color, real, board)
            elif piece_type == 'r':
                piece_beams = self.rook_aims(sqSelected, piece_color, real, board)
            elif piece_type == 'b':
                piece_beams = self.bishop_aims(sqSelected, piece_color, real, board)
            elif piece_type == 'k':
                piece_beams = self.king_aims(sqSelected, piece_color, real, board)
            elif piece_type == 'q':
                piece_beams = self.rook_aims(sqSelected, piece_color, real, board) + self.bishop_aims(sqSelected,
                                                                                                      piece_color,
                                                                                                      real, board)
            return piece_beams

        def no_selected_square():
            if sqSelected == (-1, -1):
                return True

        if no_selected_square():
            return []

        selected_p = board[sqSelected[0]][sqSelected[1]]
        piece_color = selected_p[0]
        piece_type = selected_p[1]

        piece_beams = get_piece_beams()

        return piece_beams

    #####################################################
    def pawn_aims(self, sqSelected, piece_color, real, board):
        r = sqSelected[0]
        c = sqSelected[1]
        step = 1
        aims = []

        def first_pawn_jump():
            if r == 6 and piece_color == "W" or r == 1 and piece_color == "B":
                return True
            return False

        def foward_steps():
            is_way = True
            beam = []
            for i in range(1, step + 1):
                new_r = r + sign * i
                if board[new_r][c][0] != "-":
                    is_way = False
                new_sq = (new_r, c)
                new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": False}
                if real:
                    i_board = imaginary_board(sqSelected, new_sq, self.board)
                    if not self.is_check(piece_color, i_board):
                        beam.append(new_aim)
                else:
                    beam.append(new_aim)
            if beam:
                aims.append(beam)

        def diag_threats():
            beam = []
            if 0 <= c <= 6:
                is_way = True
                if board[r + sign][c + 1][0] in {piece_color, "-"}:
                    is_way = False

                new_sq = (r + sign, c + 1)
                new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": True}
                if real:
                    i_board = imaginary_board(sqSelected, new_sq, self.board)
                    if not self.is_check(piece_color, i_board):
                        beam.append(new_aim)
                else:
                    beam.append(new_aim)

            if beam:
                aims.append(beam)

            beam = []
            if 1 <= c <= 7:
                is_way = True
                if board[r + sign][c - 1][0] in {piece_color, "-"}:
                    is_way = False
                new_sq = (r + sign, c - 1)
                new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": True}
                if real:
                    i_board = imaginary_board(sqSelected, new_sq, self.board)
                    if not self.is_check(piece_color, i_board):
                        beam.append(new_aim)
                else:
                    beam.append(new_aim)

            if beam:
                aims.append(beam)

        if first_pawn_jump():
            step = 2

        sign = 1
        if piece_color == "W":
            sign = -1

        foward_steps()

        diag_threats()

        return aims

    def knight_aims(self, sqSelected, piece_color, real, board):
        def knight_aim():
            is_way = True
            row = r + knight_dic[key][0]
            col = c + knight_dic[key][1]
            if in_bounds(row, col):
                beam = []
                if board[row][col][0] == piece_color:
                    is_way = False

                new_sq = (row, col)
                new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": True}
                if real:
                    i_board = imaginary_board(sqSelected, new_sq, self.board)
                    if not self.is_check(piece_color, i_board):
                        beam.append(new_aim)
                else:
                    beam.append(new_aim)

                if beam:
                    aims.append(beam)

        knight_dic = {"a": (-2, 1), "b": (-1, 2), "c": (1, 2), "d": (2, 1),
                      "e": (2, -1), "f": (1, -2), "g": (-1, -2), "h": (-2, -1)}
        r = sqSelected[0]
        c = sqSelected[1]
        aims = []

        for key in knight_dic:
            knight_aim()

        return aims

    def rook_aims(self, sqSelected, piece_color, real, board):
        r = sqSelected[0]
        c = sqSelected[1]

        def get_row_col(direction, sq):
            dir_dict = {"right": (0, 1), "down": (1, 0),
                        "left": (0, -1), "up": (-1, 0)}
            new_r = r + sq * dir_dict[direction][0]
            new_c = c + sq * dir_dict[direction][1]

            return (new_r, new_c)

        def rook_beam():
            beam = []
            is_way = True
            is_aim = True
            for sq in range(1, 8):
                row_col = get_row_col(direction, sq)
                row = row_col[0]
                col = row_col[1]
                if in_bounds(row, col):
                    square = board[row][col]
                    if square[0] == piece_color:
                        is_way = False
                    new_sq = (row, col)
                    new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": is_aim}
                    if real:
                        i_board = imaginary_board(sqSelected, new_sq, self.board)
                        if not self.is_check(piece_color, i_board):
                            beam.append(new_aim)
                    else:
                        beam.append(new_aim)

                    if not is_way:
                        is_aim = False
                    if square[1] != 'k':
                        if square[0] != '-':
                            break

            if beam:
                aims.append(beam)

        dir_set = ["right", "down", "left", "up"]
        aims = []

        for direction in dir_set:
            rook_beam()

        return aims

    def bishop_aims(self, sqSelected, piece_color, real, board):
        r = sqSelected[0]
        c = sqSelected[1]

        def get_row_col(direction, sq):
            dir_dict = {"down-right": ("+", "+"), "down-left": ("+", "-"),
                        "up-right": ("-", "+"), "up-left": ("-", "-")}
            new_r = r + sq
            new_c = c + sq
            if dir_dict[direction][0] == "-":
                new_r = r - sq
            if dir_dict[direction][1] == "-":
                new_c = c - sq

            return (new_r, new_c)

        def bishop_beam():
            beam = []
            is_way = True
            is_aim = True
            for sq in range(1, 8):
                row_col = get_row_col(direction, sq)
                row = row_col[0]
                col = row_col[1]
                if in_bounds(row, col):
                    square = board[row][col]
                    if square[0] == piece_color:
                        is_way = False
                    new_sq = (row, col)
                    new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": is_aim}
                    if real:
                        i_board = imaginary_board(sqSelected, new_sq, self.board)
                        if not self.is_check(piece_color, i_board):
                            beam.append(new_aim)
                    else:
                        beam.append(new_aim)

                    if not is_way:
                        is_aim = False
                    if square[1] != 'k':
                        if square[0] != '-':
                            break
            if beam:
                aims.append(beam)

        dir_set = ["down-right", "down-left", "up-right", "up-left"]

        aims = []

        for direction in dir_set:
            bishop_beam()

        return aims

    def king_aims(self, sqSelected, piece_color, real, board):
        r = sqSelected[0]
        c = sqSelected[1]

        def castle_aims():
            def king_side():
                if castle_inf['rk']:
                    if kings_row[c + 1] == kings_row[c + 2] == '--':
                        # if castle squares(king till rook) in enemy beam: return []
                        i_sqs = [(r, c + 1), (r, c + 2)]
                        for i_sq in i_sqs:
                            i_board = imaginary_board(sqSelected, i_sq, self.board)
                            if self.is_check(piece_color, i_board):
                                return
                        castle_aims.append({"aim": (r, 7), "is_way": True})
                return

            def queen_side():
                if castle_inf['rq']:
                    if kings_row[c - 1] == kings_row[c - 2] == kings_row[c - 3] == '--':
                        # if castle squares(king till rook) in enemy beam: return []
                        i_sqs = [(r, c - 1), (r, c - 2)]
                        for i_sq in i_sqs:
                            i_board = imaginary_board(sqSelected, i_sq, self.board)
                            if self.is_check(piece_color, i_board):
                                return
                        castle_aims.append({"aim": (r, 0), "is_way": True})

                return

            castle_inf = self.castle_inf[piece_color]
            if not castle_inf['k']:
                return []
            castle_aims = []
            kings_row = self.board[r]

            king_side()
            queen_side()

            return [castle_aims]

        def around_king_aims():
            around_aims = []
            for row in range(-1, 2):
                for col in range(-1, 2):
                    if (row, col) == (r, c):
                        continue
                    beam = []

                    is_way = True
                    row_way = r + row
                    col_way = c + col
                    if in_bounds(row_way, col_way):
                        sq = board[row_way][col_way]

                        new_sq = (row_way, col_way)
                        if real:
                            i_board = imaginary_board(sqSelected, new_sq, self.board)
                            if not self.is_check(piece_color, i_board):
                                is_way = True
                            else:
                                is_way = False
                        if sq[0] == piece_color:
                            is_way = False
                        new_aim = {"aim": new_sq, "is_way": is_way, "is_aim": True}

                        beam.append(new_aim)
                        if beam:
                            around_aims.append(beam)
            return around_aims

        aims = around_king_aims()
        castle_aims = castle_aims()

        return aims + castle_aims

    ########################################################################################
    def is_check(self, king_color, board):  # returns true if king checked in given board
        def get_enemy_pieces():

            enemy_pieces = []
            for r in range(8):
                for c in range(8):
                    if board[r][c][0] == enemy_color:
                        if board[r][c][1] != 'k':
                            enemy_pieces.append((r, c))
            return enemy_pieces

        def search_for_check():

            for i in range(len(enemy_pieces)):
                piece_aims = self.get_beams(enemy_pieces[i], False, board)
                for beam in range(len(piece_aims)):
                    for aim in range(len(piece_aims[beam])):
                        sq = piece_aims[beam][aim]
                        sq_n = sq["aim"]
                        if (king_pos == sq_n) and sq["is_aim"]:
                            return True
            return False

        enemy_color = 'W'
        if king_color == 'W':
            enemy_color = 'B'

        enemy_pieces = get_enemy_pieces()
        king_pos = search_king_pos(board, king_color)

        if search_for_check():
            return True
        return False

    ########################################################################################






    ###################################################################################


###################################################################################

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0, }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7, }

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getNotation(self, gs):
        note = ""
        if not gs.whiteToMove:
            note = ""

        note += f'({self.pieceMoved[1].upper()}){self.getRankFile(self.startRow, self.startCol)}  ->  ({self.pieceMoved[1].upper()}){self.getRankFile(self.endRow, self.endCol)}'
        return note

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
