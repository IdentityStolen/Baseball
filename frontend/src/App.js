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
  const [descriptions, setDescriptions] = useState({});
  const [loadingDesc, setLoadingDesc] = useState({});
  const [modalPlayerId, setModalPlayerId] = useState(null);
  const [editPlayerId, setEditPlayerId] = useState(null);
  const [editForm, setEditForm] = useState(null);
  const [editError, setEditError] = useState(null);
  const [editLoading, setEditLoading] = useState(false);
  const [sortField, setSortField] = useState('hits');

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

  const fetchDescription = async (player) => {
    if (!player?.id) return;
    // Close edit modal if open
    closeEditModal();
    if (descriptions[player.id]) {
      setModalPlayerId(player.id);
      return;
    }
    setLoadingDesc((s) => ({ ...s, [player.id]: true }));
    setModalPlayerId(player.id);
    try {
      const res = await fetch(`/api/baseball/players/${player.id}/description/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDescriptions((s) => ({ ...s, [player.id]: data.description }));
    } catch (err) {
      setDescriptions((s) => ({ ...s, [player.id]: `Error: ${err.message}` }));
    } finally {
      setLoadingDesc((s) => ({ ...s, [player.id]: false }));
    }
  };

  const openEditModal = (player) => {
    // Close description modal if open
    setModalPlayerId(null);
    setEditPlayerId(player.id);
    setEditForm({
      position: player.position || '',
      games: player.games ?? '',
      at_bat: player.at_bat ?? '',
      hits: player.hits ?? '',
      doubles: player.doubles ?? '',
      triples: player.triples ?? '',
      home_runs: player.home_runs ?? '',
      rbi: player.rbi ?? '',
      walks: player.walks ?? '',
      strikeouts: player.strikeouts ?? '',
      stolen_bases: player.stolen_bases ?? '',
      caught_stealing: player.caught_stealing ?? '',
      batting_average: player.batting_average ?? '',
      slugging_percentage: player.slugging_percentage ?? '',
      on_base_plus_slugging: player.on_base_plus_slugging ?? '',
    });
    setEditError(null);
    setEditLoading(false);
  };

  const closeEditModal = () => {
    setEditPlayerId(null);
    setEditForm(null);
    setEditError(null);
    setEditLoading(false);
  };

  const closeModal = () => setModalPlayerId(null);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditForm((f) => ({ ...f, [name]: value }));
  };

  const positionOptions = ["LF", "RF", "CF", "1B", "2B", "3B", "SS", "C", "DH", "P"];
  // Define min/max constants for each field based on dataset
  const intFields = {
    games: [0, 3500],
    at_bat: [0, 14053],
    hits: [0, 4256],
    doubles: [8, 746],
    triples: [4, 177],
    home_runs: [117, 762],
    rbi: [418, 2499],
    walks: [183, 2558],
    strikeouts: [183, 2597],
    stolen_bases: [1, 808],
    caught_stealing: [0, 149],
  };
  const floatFields = {
    batting_average: [0.231, 0.43],
    slugging_percentage: [0.34, 0.69],
    on_base_plus_slugging: [0.671, 1.164],
  };

  const handleEditSave = async () => {
    setEditLoading(true);
    setEditError(null);
    const body = { ...editForm };
    try {
      const res = await fetch(`/api/baseball/players/${editPlayerId}/update/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setEditError(data.errors ? Object.values(data.errors).join(' | ') : (data.error || 'Unknown error'));
        setEditLoading(false);
        return;
      }
      // Update local state
      setPlayers((ps) => ps.map(p => p.id === editPlayerId ? { ...p, ...editForm } : p));
      closeEditModal();
    } catch (err) {
      setEditError(err.message);
      setEditLoading(false);
    }
  };

  // Sort players by selected field (descending)
  const sortedPlayers = [...players].sort((a, b) => {
    const field = sortField;
    const va = a[field] ?? 0;
    const vb = b[field] ?? 0;
    return vb - va;
  });

  const modalContent = (() => {
    if (!modalPlayerId) return null;
    const player = players.find(p => p.id === modalPlayerId);
    return (
      <div className="modal-overlay" onClick={closeModal}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <button className="modal-close" onClick={closeModal}>&times;</button>
          <h2>{player?.name}</h2>
          {loadingDesc[modalPlayerId] ? (
            <em>Loading description...</em>
          ) : (
            <div>{descriptions[modalPlayerId]}</div>
          )}
        </div>
      </div>
    );
  })();

  const editModalContent = (() => {
    if (!editPlayerId || !editForm) return null;
    const player = players.find(p => p.id === editPlayerId);
    return (
      <div className="modal-overlay" onClick={closeEditModal}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <button className="modal-close" onClick={closeEditModal}>&times;</button>
          <h2>Edit {player.name}</h2>
          <form className="edit-form" onSubmit={e => { e.preventDefault(); handleEditSave(); }}>
            <div><label>Name: <input value={player.name} readOnly /></label></div>
            <div>
              <label>Pos:
                <select name="position" value={editForm.position} onChange={handleEditChange} required>
                  <option value="" disabled>Select position</option>
                  {positionOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              </label>
            </div>
            {Object.entries(intFields).map(([field, [min, max]]) => (
              <div key={field}>
                <label>{field.replace(/_/g, ' ').toUpperCase()}: <input type="number" name={field} value={editForm[field]} min={min} max={max} onChange={handleEditChange} required /></label>
              </div>
            ))}
            {Object.entries(floatFields).map(([field, [min, max]]) => (
              <div key={field}>
                <label>{field.replace(/_/g, ' ').toUpperCase()}: <input type="number" name={field} value={editForm[field]} min={min} max={max} step="0.001" onChange={handleEditChange} required /></label>
              </div>
            ))}
            {editError && <div className="error">{editError}</div>}
            <div style={{marginTop:12}}>
              <button type="submit" disabled={editLoading}>Save</button>
              <button type="button" onClick={closeEditModal} disabled={editLoading} style={{marginLeft:8}}>Cancel</button>
            </div>
          </form>
        </div>
      </div>
    );
  })();

  return (
    <div className="container">
      <h1>Baseball Players</h1>
      <div style={{marginBottom: '16px'}}>
        <label htmlFor="sortField">Sort by: </label>
        <select id="sortField" value={sortField} onChange={e => setSortField(e.target.value)}>
          <option value="hits">Hits</option>
          <option value="home_runs">HR</option>
        </select>
      </div>
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
                <th>Doubles</th>
                <th>Triples</th>
                <th>HR</th>
                <th>RBI</th>
                <th>Walks</th>
                <th>Strikeouts</th>
                <th>SB</th>
                <th>CS</th>
                <th>AVG</th>
                <th>OBP</th>
                <th>SLG</th>
                <th>OPS</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sortedPlayers.map((p, idx) => (
                <tr key={`${p.id}-${idx}`}>
                  <td>
                    <button className="link-button" onClick={() => fetchDescription(p)}>
                      {p.name}
                    </button>
                  </td>
                  <td>{p.position}</td>
                  <td>{p.games ?? '-'}</td>
                  <td>{p.at_bat ?? '-'}</td>
                  <td>{p.hits ?? '-'}</td>
                  <td>{p.doubles ?? '-'}</td>
                  <td>{p.triples ?? '-'}</td>
                  <td>{p.home_runs ?? '-'}</td>
                  <td>{p.rbi ?? '-'}</td>
                  <td>{p.walks ?? '-'}</td>
                  <td>{p.strikeouts ?? '-'}</td>
                  <td>{p.stolen_bases ?? '-'}</td>
                  <td>{p.caught_stealing ?? '-'}</td>
                  <td>{p.batting_average ?? '-'}</td>
                  <td>{p.on_base_percentage ?? '-'}</td>
                  <td>{p.slugging_percentage ?? '-'}</td>
                  <td>{p.on_base_plus_slugging ?? '-'}</td>
                  <td><button className="edit-button" onClick={() => openEditModal(p)}>EDIT</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {modalContent}
      {editModalContent}
    </div>
  );
}
