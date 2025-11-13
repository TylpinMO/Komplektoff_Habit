import React, { useEffect, useState } from 'react'

export default function App() {
	const [users, setUsers] = useState([])
	const BASE = import.meta.env.VITE_BACKEND_URL || ''
	useEffect(() => {
		fetch(`${BASE}/users`)
			.then(r => r.json())
			.then(setUsers)
			.catch(() => {})
	}, [])
	return (
		<div style={{ padding: 20 }}>
			<h1>Habit Tracker — frontend (skeleton)</h1>
			<p>
				Запросы идут к бэкенду: <code>{BASE || 'тот же хост'}</code>
			</p>
			<h2>Users</h2>
			<ul>
				{users.map(u => (
					<li key={u.id}>
						{u.id} — {u.username} — {u.registered_at}
					</li>
				))}
			</ul>
		</div>
	)
}
