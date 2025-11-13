import React, { useEffect, useState } from 'react'

export default function App() {
	const [users, setUsers] = useState([])
	const BASE = import.meta.env.VITE_BACKEND_URL || ''
	const [selectedUser, setSelectedUser] = useState(null)
	const [habits, setHabits] = useState([])
	useEffect(() => {
		fetch(`${BASE}/users`)
			.then(r => r.json())
			.then(setUsers)
			.catch(() => {})
	}, [])
	const loadUser = (id) => {
		setSelectedUser(id)
		fetch(`${BASE}/users/${id}/habits`)
			.then(r => r.json())
			.then(setHabits)
			.catch(()=> setHabits([]))
	}
	return (
		<div style={{ padding: 20 }}>
			<h1>Habit Tracker — frontend (skeleton)</h1>
			<p>
				Запросы идут к бэкенду: <code>{BASE || 'тот же хост'}</code>
			</p>
			<h2>Users</h2>
			<ul>
				{users.map(u => (
					<li key={u.id} style={{cursor:'pointer'}} onClick={()=>loadUser(u.id)}>
						{u.id} — {u.username} — {u.registered_at}
					</li>
				))}
			</ul>

			{selectedUser && (
				<div style={{marginTop:20}}>
					<h2>User {selectedUser} — Habits</h2>
					<button onClick={()=>{setSelectedUser(null); setHabits([])}}>Back</button>
					<ul>
						{habits.map(h => (
							<li key={h.id}>{h.name} — done: {h.done_count}</li>
						))}
					</ul>
				</div>
			)}
		</div>
	)
}
