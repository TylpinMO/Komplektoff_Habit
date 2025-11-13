import React, { useEffect, useState } from 'react'

export default function App() {
	const [users, setUsers] = useState([])
	useEffect(() => {
		fetch('/api/users')
			.then(r => r.json())
			.then(setUsers)
			.catch(() => {})
	}, [])
	return (
		<div style={{ padding: 20 }}>
			<h1>Habit Tracker — frontend (skeleton)</h1>
			<p>Запросы идут к `/api` (настройте proxy или укажите полный URL)</p>
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
