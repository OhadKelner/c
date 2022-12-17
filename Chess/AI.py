from ChessEngine import imaginary_board as i_board


class AI:
    def __init__(self):
        self.name = ""

    def get_board_rating(self, board, gs):
        def pieces_on_board_para():
            piece_value_dic = {'q': 9, 'r': 5, 'n': 3, 'b': 3, 'p': 1, 'k': 200}
            white_val = 0
            black_val = 0
            for r in range(len(board)):
                for c in range(len(board)):
                    piece = board[r][c]
                    if piece[0] == 'W':
                        white_val += piece_value_dic[piece[1]]
                    elif piece[0] == 'B':
                        black_val += piece_value_dic[piece[1]]
            board_rate = white_val - black_val

            return board_rate

        def control_squares_para():
            def color_control_val(color):
                color_pieces = self.get_color_sqs(color, gs)
                color_control_val = 0
                for piece_index, piece in enumerate(color_pieces):
                    piece_ways = gs.get_beams(piece, True, board)
                    color_control_val += len(piece_ways)
                return color_control_val

            white_control = color_control_val('W')
            black_control = color_control_val('B')
            control_val = white_control - black_control

            return control_val

        board_rating = pieces_on_board_para() + control_squares_para()/20
        return board_rating

    def calc_ai_move(self, gs):
        def imagine_move_on_board(move, board):
            board = i_board(move[0], move[1], board)
            return board

        blacks_pieces_sqs = self.get_color_sqs("B", gs)

        whites_pieces_sqs = self.get_color_sqs("W", gs)

        b_potential_moves = self.get_color_moves(blacks_pieces_sqs, gs)

        w_potential_moves = self.get_color_moves(whites_pieces_sqs, gs)

        if not b_potential_moves:
            return None

        best_move = {"move": (None, None), "rating": 100}
        old_board_rating = self.get_board_rating(gs.board, gs)
        print(f'old_board_rating : {old_board_rating}')
        print("_____________________________________")
        for piece_index in range(len(b_potential_moves)):
            print("________________________")
            piece_info = b_potential_moves[piece_index]
            print(f'piece_info : {piece_info}')
            all_piece_moves = list(piece_info.values())[0]
            print(f'all_piece_moves : {all_piece_moves}')
            for piece_move_index in range(len(all_piece_moves)):
                print("____________")
                square_move = all_piece_moves[piece_move_index]
                print(f'square_move : {square_move}')

                piece_pos = list(piece_info.keys())[0]
                print(f'piece_pos : {piece_pos}')
                move = (piece_pos, square_move)
                print(f'move : {move}')

                old_board = gs.board
                new_board = imagine_move_on_board(move, old_board)
                new_board_rating = self.get_board_rating(new_board, gs)
                print(f'new_board_rating : {new_board_rating}')

                move_rating = new_board_rating - old_board_rating
                print(f'move_rating : {move_rating}')

                if move_rating < best_move["rating"]:
                    best_move["move"] = move
                    best_move["rating"] = move_rating

        return best_move["move"]

    def get_color_moves(self, color_pieces_sqs, gs):
        all_color_moves = []

        for piece in color_pieces_sqs:

            piece_beams = gs.get_beams(piece, True, gs.board)
            piece_moves = []

            for beam in range(len(piece_beams)):
                if type(piece_beams[beam]) is list:
                    for aim in range(len(piece_beams[beam])):
                        if piece_beams[beam][aim]["is_way"]:
                            piece_moves.append(piece_beams[beam][aim]["aim"])
            if piece_moves:
                piece_dict = {}
                piece_dict[piece] = piece_moves
                all_color_moves.append(piece_dict)

        return all_color_moves

    def get_color_sqs(self, color, gs):
        sqs = []
        for r in range(8):
            for c in range(8):
                if gs.board[r][c][0] == color:
                    sqs.append((r, c))
        return sqs
