import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _catalog_path() -> Path:
    workspace_root = Path(__file__).resolve().parents[2]
    return workspace_root / "metadata" / "catalog.db"


def _get_connection():
    return sqlite3.connect(_catalog_path())


_METADATA_LIKE = "metadata LIKE ?"


def _build_clauses(filters: Dict[str, Any]) -> Tuple[List[str], List[Any]]:
    clauses: List[str] = []
    params: List[Any] = []
    if term := filters.get("term"):
        clauses.append("(title LIKE ? OR artist LIKE ?)")
        params.extend([f"%{term}%", f"%{term}%"])
    if dataset := filters.get("dataset"):
        clauses.append("dataset = ?")
        params.append(dataset)
    if min_tempo := filters.get("min_tempo"):
        clauses.append("tempo >= ?")
        params.append(min_tempo)
    if max_tempo := filters.get("max_tempo"):
        clauses.append("tempo <= ?")
        params.append(max_tempo)
    if has_metadata := filters.get("has_metadata"):
        if has_metadata:
            clauses.append("metadata IS NOT NULL AND metadata != ''")
        else:
            clauses.append("(metadata IS NULL OR metadata = '')")
    if key := filters.get("key"):
        clauses.append(_METADATA_LIKE)
        params.append(f'%\"key\": \"{key}\"%')
    if mode := filters.get("mode"):
        clauses.append(_METADATA_LIKE)
        params.append(f'%\"mode\": \"{mode}\"%')
    if cadence := filters.get("cadence"):
        clauses.append(_METADATA_LIKE)
        params.append(f'%\"cadence\": \"{cadence}\"%')
    if chord := filters.get("chord"):
        safe_chord = chord.replace('"', "")
        clauses.append(_METADATA_LIKE)
        params.append(f"%{safe_chord}%")
    return clauses, params


def list_songs(filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    filters = filters or {}
    query = "SELECT id,title,artist,dataset,sections_count,chords_count,tempo,timesig_num,timesig_denom,metadata,project_file,source FROM song_catalog"
    clauses, params = _build_clauses(filters)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY title COLLATE NOCASE LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = _get_connection()
    cur = conn.execute(query, params)
    rows = cur.fetchall()
    columns = [d[0] for d in cur.description]
    conn.close()

    result = []
    for row in rows:
        entry = dict(zip(columns, row))
        entry["metadata"] = json.loads(entry["metadata"]) if entry["metadata"] else {}
        result.append(entry)
    return result


def count_songs(filters: Dict[str, Any] = None) -> int:
    filters = filters or {}
    query = "SELECT COUNT(*) FROM song_catalog"
    clauses, params = _build_clauses(filters)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    conn = _get_connection()
    cur = conn.execute(query, params)
    value = cur.fetchone()[0]
    conn.close()
    return value


def list_datasets() -> List[str]:
    conn = _get_connection()
    cur = conn.execute("SELECT DISTINCT dataset FROM song_catalog ORDER BY dataset")
    datasets = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return datasets


def get_song_by_id(song_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cur = conn.execute("SELECT * FROM song_catalog WHERE id = ?", (song_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    columns = [d[0] for d in cur.description]
    entry = dict(zip(columns, row))
    entry["metadata"] = json.loads(entry["metadata"]) if entry["metadata"] else {}
    return entry
