import React, { useEffect, useState } from 'react'
import './styles.css'

export default function App() {
	const [users, setUsers] = useState([])
	const BASE = import.meta.env.VITE_BACKEND_URL || ''
	const [selectedUser, setSelectedUser] = useState(null)
	const [habits, setHabits] = useState([])
	const [loadingUsers, setLoadingUsers] = useState(true)

	useEffect(() => {
		setLoadingUsers(true)
		fetch(`${BASE}/users`)
			.then(r => r.json())
			.then(d => setUsers(d || []))
			.catch(() => setUsers([]))
			.finally(() => setLoadingUsers(false))
	}, [BASE])

	const loadUser = id => {
		setSelectedUser(id)
		setHabits([])
		fetch(`${BASE}/users/${id}/habits`)
			.then(r => r.json())
			.then(setHabits)
			.catch(() => setHabits([]))
	}

	return (
		<div className='app-root'>
			<header className='app-header'>
				<h1>🧭 Habit Tracker</h1>
				<p className='muted'>Лёгкий трекер привычек — бот + API + SPA</p>
			</header>

			<main className='container'>
				<section className='panel'>
					<h2>Пользователи</h2>
					<p className='muted'>
						Запросы к бэкенду: <code>{BASE || 'тот же хост'}</code>
					</p>

					{loadingUsers ? (
						<div className='placeholder'>Загрузка...</div>
					) : users.length === 0 ? (
						<div className='placeholder'>
							Пока нет пользователей — подключите бота и отправьте /start
						</div>
					) : (
						<ul className='list'>
							{users.map(u => (
								<li
									key={u.id}
									className='list-item'
									onClick={() => loadUser(u.id)}
								>
									<div className='item-title'>
										{u.username || `user-${u.id}`}
									</div>
									<div className='item-sub'>
										id: {u.id} • {u.registered_at}
									</div>
								</li>
							))}
						</ul>
					)}
				</section>

				<section className='panel'>
					{selectedUser ? (
						<>
							<div className='panel-header'>
								<h2>Привычки пользователя {selectedUser}</h2>
								<button
									className='btn'
									onClick={() => {
										setSelectedUser(null)
										setHabits([])
									}}
								>
									← Назад
								</button>
							</div>

							{habits.length === 0 ? (
								<div className='placeholder'>
									Привычек нет или они ещё не загружены.
								</div>
							) : (
								<div className='grid'>
									{habits.map(h => (
										<div key={h.id} className='card'>
											<div className='card-title'>{h.name}</div>
											<div className='card-sub'>Отмечено: {h.done_count}</div>
										</div>
									))}
								</div>
							)}
						</>
					) : (
						<div className='placeholder'>
							Выберите пользователя слева, чтобы посмотреть его привычки.
						</div>
					)}
				</section>
			</main>
		</div>
	)
}
