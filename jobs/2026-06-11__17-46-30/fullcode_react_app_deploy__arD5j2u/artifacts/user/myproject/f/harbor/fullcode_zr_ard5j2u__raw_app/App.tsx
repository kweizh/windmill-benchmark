import React, { useState } from 'react';
import { backend } from './wmill';

export default function App() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  async function handleGreet() {
    setLoading(true);
    try {
      const res = await backend.greet({ name: 'Windmill' });
      setResult(typeof res === 'string' ? res : JSON.stringify(res));
    } catch (err) {
      setResult('Error: ' + String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 600, margin: '40px auto', padding: '0 20px' }}>
      <h1>Harbor Fullcode App</h1>
      <p>A Full-Code React app connected to Windmill backend runnables.</p>
      <button
        onClick={handleGreet}
        disabled={loading}
        style={{
          padding: '10px 20px',
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: 6,
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: 16,
        }}
      >
        {loading ? 'Loading...' : 'Greet via Backend'}
      </button>
      {result && (
        <div style={{ marginTop: 20, padding: 16, background: '#f0fdf4', borderRadius: 6, border: '1px solid #86efac' }}>
          <strong>Result:</strong> {result}
        </div>
      )}
    </div>
  );
}
