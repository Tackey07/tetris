from datetime import datetime
import pprint
import copy
class mycounter_func:  #何回実行されたかをカウントするクラス。
    def __init__(self):
        self.x = 0
    def __call__(self):
        self.x += 1
        return self.x
mycounter = mycounter_func()  #mycounter()を呼び出すたびに、値が１ずつ増える

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    

    
    
    
    def GetNextMove(self, nextMove, GameStatus): #〈p1s~p4sの変数で、fulllines等のパラメータに掛ける係数を受け取れるようにしました〉
        COUNTER=mycounter()
        print("COUNTER="+str(COUNTER))

        t1 = datetime.now()
        if COUNTER==1:
            nextMove["strategy"]["direction"] = 0      #前述の入れ子forループで導いた最も評価の高い手の回転状態を入力
            nextMove["strategy"]["x"] = 0              #前述の入れ子forループで導いた最も評価の高い手のｘ座標を入力
            nextMove["strategy"]["y_operation"] = 1    #縦方向に一気に落とす1か、少しずつ落とす2か。通常は１
            nextMove["strategy"]["y_moveblocknum"] = 1 #y_operation=0の場合に、y方向に何座標動かすか。y_operation=1なら無視される。
            nextMove["strategy"]["use_hold_function"]="y"  #strategy[4]=="y" or "n"                 

            return nextMove
        #print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]  #この変数に、現在のshapeがとりうる回転状態のリストを受け取ります。
        CurrentShapeIndex = GameStatus["block_info"]["currentShape"]["index"]  #この変数に、現在のshapeがとりうる回転状態のリストを受け取ります。
                #game_managerのcurrentShapeRange = BOARD_DATA.getShapeData(0)
                #BOARD_DATA.getShapeData(0)=
        # current shape info
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]   #この変数に、次に来るshapeがとりうる回転状態のリストを受け取ります。
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]  #この変数に、現在のshapeがとりうる回転状態のリストを受け取ります。
        HoldShapeIndex = GameStatus["block_info"]["holdShape"]["index"]  #この変数に、現在のshapeがとりうる回転状態のリストを受け取ります。
        self.HoldShape_class = GameStatus["block_info"]["holdShape"]["class"]
        
        EvalValue_org ,nHoles_org,LIST_TOP_org,LIST_BOTTOM_org,Right_Side_Exist_org,fullLine_CANDIDATE_org,Right_Side_TOP_org,Valley_Index_org= self.calcEvaluationValueSample(self.board_backboard,"Start",0,0,0)  #ボード配列を評価しscore値を受け取る。〈fulllines等に掛ける係数を入力するようにしました〉
        # print(f"EvalValue_org,nHoles_org,LIST_TOP_org,LIST_BOTTOM_org,Right_Side_Exist_org,fullLine_CANDIDATE_org={EvalValue_org}, {nHoles_org}, {LIST_TOP_org}, {LIST_BOTTOM_org} ,{Right_Side_Exist_org}, {fullLine_Candidate_org}")
    
        # search best nextMove -->
        strategy = [0,0,1,1,"n"]
        LatestEvalValue = -100000
        CHECKMATE="n"
        # search with current block Shape
        if LIST_BOTTOM_org<15:
            if CurrentShapeIndex==1:
                Target_Option=["n","y"]
            else:
                Target_Option=["n","y"]
        else:
            Target_Option=["n","y"]

        Valley_Attack="n"
        
        if len(Valley_Index_org)>0:
            if CurrentShapeIndex==1:
                Valley_Attack="y"
                strategy = [0,Valley_Index_org[0],1,1,"n"]
            elif HoldShapeIndex==1:
                Valley_Attack="y"
                strategy = [0,Valley_Index_org[0],1,1,"y"]
        else:
            Valley_Attack="n"


        if Valley_Attack=="n":
            for UseHold0 in Target_Option:   #次の手でhold機能を使うかどうかを評価するforループ（holdされたミノとの交換を行うかどうか）
                if UseHold0=="n" :   #holdとの交換を行わない場合は、
                    TargetShapeRange=CurrentShapeDirectionRange   #for文を回し評価する対象をCurrentShapeとする。
                    targetShape_class= self.CurrentShape_class
                    TargetIndex=CurrentShapeIndex

                else:                #holdとの交換を行う場合は、
                    TargetShapeRange=HoldShapeDirectionRange      #for文を回し評価する対象をHoldShapeとする。
                    targetShape_class= self.HoldShape_class
                    TargetIndex=HoldShapeIndex
                if fullLine_CANDIDATE_org>=4 and Right_Side_TOP_org<LIST_TOP_org:

                    if TargetIndex==1:
                        CHECKMATE = "y1"     #変数UseHold0が"y"なら、holdされたミノに交換されてnextMove操作を実行。
                    if TargetIndex==2:
                        CHECKMATE=="y2"
                    

                if CHECKMATE=="n":
                    for direction0 in TargetShapeRange:               
                                            # search with x range
                        x0Min, x0Max = self.getSearchXRange(targetShape_class, direction0)
                        if nHoles_org==0 and fullLine_CANDIDATE_org<=4:
                            x0Adj=x0Max-1
                        # elif nHoles_org==0 and LIST_TOP_org<8:
                        #     x0Adj=x0Max-1
                        else:
                            x0Adj=x0Max
                        for x0 in range(x0Min, x0Adj):
                            # get board data, as if dropdown block
                            board = self.getBoard(self.board_backboard, targetShape_class, direction0, x0)
                            # evaluate board
                            EvalValue_eval ,nHoles_eval,LIST_TOP_eval,LIST_BOTTOM_eval,Right_Side_Exist_eval,fullLine_CANDIDATE_eval,Right_Side_TOP_eval,Valley_Index_eval= self.calcEvaluationValueSample(board,"Evaluate",nHoles_org,LIST_TOP_org,LIST_BOTTOM_org)  #ボード配列を評価しscore値を受け取る。〈fulllines等に掛ける係数を入力するようにしました〉
                            # print(f"absDy_org={absDy_org}")
                            # print(f"absDy_eval={absDy_eval}")
                            if EvalValue_eval > LatestEvalValue:
                                strategy = (direction0, x0, 1, 1,UseHold0)     #変数UseHold0が"y"なら、holdされたミノに交換されてnextMove操作を実行。
                                LatestEvalValue = EvalValue_eval
                if CHECKMATE=="y1":
                    strategy = (0, 9, 1, 1,UseHold0)
                    break
                if CHECKMATE=="y2":
                    strategy = (2, 8, 1, 1,UseHold0)
                    break

                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
        # search best nextMove <--
        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]      #前述の入れ子forループで導いた最も評価の高い手の回転状態を入力
        nextMove["strategy"]["x"] = strategy[1]              #前述の入れ子forループで導いた最も評価の高い手のｘ座標を入力
        nextMove["strategy"]["y_operation"] = strategy[2]    #縦方向に一気に落とす1か、少しずつ落とす2か。通常は１
        nextMove["strategy"]["y_moveblocknum"] = strategy[3] #y_operation=0の場合に、y方向に何座標動かすか。y_operation=1なら無視される。
        nextMove["strategy"]["use_hold_function"] = strategy[4] #y_operation=0の場合に、y方向に何座標動かすか。y_operation=1なら無視される。
        
        print(nextMove)
        # print("###### SAMPLE CODE ######")
        return nextMove

    def getSearchXRange(self, Shape_class, direction):  #与えられたshape種類とその回転状態から、x方向の可動範囲を取得する関数
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def calcEvaluationValueSample(self, board,mode,nHoles_prev,LIST_TOP_prev,LIST_BOTTOM_prev):  #ボード配列を評価しscore出力する関数。〈p1~p4でfulllines等に掛ける係数を受け取れるようにしました〉
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height
        LIST_ONEZERO=[1 if x>0 else 0 for x in board]

        # if 1 in LIST_ONEZERO:
        #     LIST_TOP_Current=22-LIST_ONEZERO.index(1)//10
        # else:
        #     LIST_TOP_Current=0
        xLIST=[]
        for x in range(10):
            xLIST.append([LIST_ONEZERO[y*10+x] for y in range(22) ])
        yLIST=[LIST_ONEZERO[y*10:y*10+10] for y in range(22)]

        # print(len(xLIST))
        # for x in range(10):
        #     print(x,xLIST[x])
        # print("")
        # print(len(yLIST))

        # for y in range(22):
        #     print(str(22-y).zfill(2),yLIST[y])

        xTOP_LIST=[]
        for x in range(10):
            if 1 in xLIST[x]:
                xTOP_LIST.append(22-xLIST[x].index(1))
            else:
                xTOP_LIST.append(0)
        # print(" ",xTOP_LIST)

        # CappedValley=False
        # for x in range(10):
        #     if xLIST[x]==1 and xLIST[x+1]==0 and xLIST[x+2]==0:
        #         CappedValley=True

        Valley_Index=[]
        for x in range(0,10):
            if x==0:
                LEFT_CLIFF=22
                RIGHT_CLIFF=xTOP_LIST[x+1]
            elif x==9:
                LEFT_CLIFF=xTOP_LIST[x-1]
                RIGHT_CLIFF=22
            else:
                LEFT_CLIFF=xTOP_LIST[x-1]
                RIGHT_CLIFF=xTOP_LIST[x+1]

            if LEFT_CLIFF>xTOP_LIST[x]+3 and RIGHT_CLIFF>xTOP_LIST[x]+3:
                Valley_Index.append(x)


        LIST_BOTTOM_Current=min(xTOP_LIST[0:9])
        LIST_BOTTOM_INDEX=xTOP_LIST[0:9].index(LIST_BOTTOM_Current)
        LIST_TOP_Current=max(xTOP_LIST)
        LIST_TOP_INDEX=xTOP_LIST.index(LIST_TOP_Current)
        DyBOTTOM_Change=LIST_BOTTOM_Current-LIST_BOTTOM_prev
        DyTOP_Change=LIST_TOP_Current-LIST_TOP_prev
        DyTOP_BOTTOM=LIST_TOP_Current-LIST_BOTTOM_Current

        fullLine_CANDIDATE=0
        for y in range(height-1,0,-1): 
            if yLIST[y]==[1, 1, 1, 1, 1, 1, 1, 1, 1, 0]:
                fullLine_CANDIDATE+=1
        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0  #たぶん高さの差の合計値をカウントする変数
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        Right_Side_Exist=False
        Right_Side_TOP_Current=xTOP_LIST[9]
        ### check board
        # each y line
        for y in range(height - 1, 0, -1): #内側のfor ループで横一列をサーチし、このforループで縦方向をサーチ
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):      #横一列のブロック、穴の有無の判定を行う（サーチ）
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:   #サーチした座標にShapeNone_index=0を見つけたら
                    # hole
                    hasHole = True #穴あり判定を行う
                    holeCandidates[x] += 1  # just candidates in each column..　その列における穴候補の空白の数（上にブロックがあれば穴と確定される）をインクリメント
                else:      #サーチした座標が0以外なら、
                    # block
                    hasBlock = True  #ブロックあり判定を行う
                    if x == 9:
                        Right_Side_Exist=True
                    BlockMaxY[x] = height - y                # update blockMaxY ブロックを見つけた最も高い位置、を更新する。
                    if holeCandidates[x] > 0:   #ブロックがそこにある事が確定した時点で、その下の穴候補は穴と確定される。
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column.. その行における穴の数を確定
                        holeCandidates[x] = 0                # reset  その行における穴の数候補変数をリセット
                    if holeConfirm[x] > 0:                   # 確定穴数が０以上なら
                        nIsolatedBlocks += 1                 # update number of isolated blocks　　その列に、下にブロックがない孤立したブロックの数を１増やす

            if hasBlock == True and hasHole == False: #hasblockがTrueでhasholeがFalseなら、フルで埋まっている
                # filled with block                   #↓↓ 
                fullLines += 1                        #その場合はfullLinesを１インクリメント
            elif hasBlock == True and hasHole == True:   #hasblockもhasholeもTrueなら何もしない
                # do nothing
                pass
            elif hasBlock == False:     #hasblockがfalseなら何もないので何もしない
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)
        nHoles_Add=nHoles-nHoles_prev


        # calc Evaluation Value
        score = 0
        score = score + fullLines * 5           # try to delete line 
        score = score - nHoles_Add *  25             # try not to make hole   これを10倍にしたらめっちゃスコア上がった
        score = score - nIsolatedBlocks * 20     # try not to make isolated block
        score = score - absDy * 5                # try to put block smoothly
        # score = score - DyTOP_Change * 19              # try to put block smoothly
        # score = score - DyTOP_BOTTOM *10
        score = score + DyBOTTOM_Change*10


        # score = 0
        # score = score + fullLines * 5           # try to delete line 
        # score = score - nHoles_Add *  25             # try not to make hole   これを10倍にしたらめっちゃスコア上がった
        # score = score - nIsolatedBlocks * 20     # try not to make isolated block
        # score = score - absDy * 5                # try to put block smoothly
        # # score = score - DyTOP_Change * 19              # try to put block smoothly
        # # score = score - DyTOP_BOTTOM *10
        # score = score + DyBOTTOM_Change*10

        # if LIST_TOP_prev>=10:
        #     score = score - DyTOP_Change*10


        # score = score - CappedValley*5
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score,nHoles,LIST_TOP_Current,LIST_BOTTOM_Current,Right_Side_Exist,fullLine_CANDIDATE,Right_Side_TOP_Current,Valley_Index

BLOCK_CONTROLLER = Block_Controller()
