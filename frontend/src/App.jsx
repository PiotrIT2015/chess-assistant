import { useRef, useState } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";

const BACKEND_URL = "http://localhost:4000";

export default function App() {
  const gameRef = useRef(new Chess());
  const [fen, setFen] = useState(gameRef.current.fen());
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  function onPieceDrop(sourceSquare, targetSquare) {
    console.log("DROP:", sourceSquare, "->", targetSquare);

    const move = gameRef.current.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    });

    if (!move) return false;

    setFen(gameRef.current.fen());
    sendMoveToBackend(sourceSquare, targetSquare);
    return true;
  }

  async function sendMoveToBackend(from, to) {
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gameId: "game1",
          from_square: from,
          to_square: to,
        }),
      });

      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (e) {
      console.error("Backend error:", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ width: 500, margin: "40px auto", textAlign: "center" }}>
      <h2>♟ Chess Assistant</h2>

      <Chessboard
        position={fen}
        onPieceDrop={onPieceDrop}
        arePiecesDraggable={true}
      />

      <div style={{ marginTop: 20, textAlign: "left" }}>
        <h3>Rekomendacje</h3>
        {loading && <p>Analiza...</p>}
        {!loading && recommendations.length === 0 && <p>Brak rekomendacji</p>}
        {!loading &&
          recommendations.map((r, i) => (
            <div key={i}>
              <strong>{r.move}</strong> ({r.eval})
            </div>
          ))}
      </div>
    </div>
  );
}













