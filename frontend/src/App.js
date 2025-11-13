import React, { useEffect, useState } from 'react';

// Prefer an explicit override when provided (useful for local host dev or production builds).
// Otherwise use a relative path so the CRA dev-server proxy (package.json "proxy") handles forwarding
// to the Django backend inside Docker.
const defaultApi = process.env.REACT_APP_API_URL || '/api/baseball/players/by-hits/';
const apiUrl = defaultApi;

export default function App() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetch(apiUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!mounted) return;
        const list = data.players ?? data;
        setPlayers(Array.isArray(list) ? list : []);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err.message);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="container">
      <h1>Baseball Players (Sorted by hits)</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="error">Error: {error}</p>}
      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Pos</th>
                <th>Games</th>
                <th>AB</th>
                <th>Hits</th>
                <th>HR</th>
                <th>RBI</th>
                <th>AVG</th>
                <th>OBP</th>
                <th>SLG</th>
                <th>OPS</th>
              </tr>
            </thead>
            <tbody>
              {players.map((p, idx) => (
                <tr key={`${p.name}-${idx}`}>
                  <td>{p.name}</td>
                  <td>{p.position}</td>
                  <td>{p.games ?? '-'}</td>
                  <td>{p.at_bat ?? '-'}</td>
                  <td>{p.hits ?? '-'}</td>
                  <td>{p.home_runs ?? '-'}</td>
                  <td>{p.rbi ?? '-'}</td>
                  <td>{p.batting_average ?? '-'}</td>
                  <td>{p.on_base_percentage ?? '-'}</td>
                  <td>{p.slugging_percentage ?? '-'}</td>
                  <td>{p.on_base_plus_slugging ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
