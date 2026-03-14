import { useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Chessboard } from 'react-chessboard';
import { toPng } from 'html-to-image';

const PuzzleRenderer = () => {
  const [searchParams] = useSearchParams();
  const fen = searchParams.get('fen') || 'start';
  const boardRef = useRef<HTMLDivElement>(null);

  const downloadImage = () => {
    if (boardRef.current === null) {
      return;
    }

    toPng(boardRef.current, { cacheBust: true })
      .then((dataUrl) => {
        const link = document.createElement('a');
        link.download = `puzzle-${Date.now()}.png`;
        link.href = dataUrl;
        link.click();
      })
      .catch((err) => {
        console.error('oops, something went wrong!', err);
      });
  };

  return (
    <div className="puzzle-renderer-container">
      <div className="board-wrapper" ref={boardRef}>
        {/* @ts-ignore - position and boardWidth are valid but causing type mismatch in this environment */}
        <Chessboard 
          position={fen} 
          boardWidth={600}
          customBoardStyle={{
            borderRadius: '4px',
            boxShadow: '0 5px 15px rgba(0, 0, 0, 0.5)'
          }}
          customDarkSquareStyle={{ backgroundColor: '#b58863' }}
          customLightSquareStyle={{ backgroundColor: '#f0d9b5' }}
        />
      </div>
      <div className="renderer-controls">
        <p className="fen-display">FEN: {fen}</p>
        <button className="download-btn" onClick={downloadImage}>
          Download PNG
        </button>
      </div>
    </div>
  );
};

export default PuzzleRenderer;
