from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import chess
import chess.engine
from pathlib import Path
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)



games = {}
engine = None  # <- ważne

STOCKFISH_PATH = Path(
    r"C:\stockfish\stockfish-windows-x86-64-avx2.exe"
)

class MoveRequest(BaseModel):
    gameId: str
    from_square: str
    to_square: str
    promotion: str = "q"


@app.on_event("startup")
async def startup_event():
    global engine
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    print("✅ Stockfish uruchomiony")





@app.on_event("shutdown")
async def shutdown_event():
    global engine
    if engine:
        engine.quit()



@app.post("/move")
async def move(request: MoveRequest):
    board = games.setdefault(request.gameId, chess.Board())

    piece = board.piece_at(chess.parse_square(request.from_square))
    if not piece:
        return {
            "legal": False,
            "fen": board.fen(),
            "recommendations": []
        }

    move_uci = request.from_square + request.to_square

    # promocja tylko dla piona na ostatniej linii
    if (
        piece.piece_type == chess.PAWN
        and request.to_square[1] in ("1", "8")
    ):
        move_uci += request.promotion.lower()

    move = chess.Move.from_uci(move_uci)

    if move not in board.legal_moves:
        return {
            "legal": False,
            "fen": board.fen(),
            "recommendations": []
        }

    board.push(move)

    info = engine.analyse(
        board,
        chess.engine.Limit(depth=12),
        multipv=3
    )

    recommendations = []
    for pv in info:
        best_move = pv["pv"][0]
        score = pv["score"].white().score(mate_score=10000)

        recommendations.append({
            "move": best_move.uci(),
            "eval": score / 100 if score is not None else None
        })

    return {
        "legal": True,
        "fen": board.fen(),
        "recommendations": recommendations
    }


