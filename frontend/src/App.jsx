import { useEffect, useMemo, useState } from 'react'
import './styles.css'

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const initialHabits = [
	{ id: 1, name: 'Утренняя разминка', category: 'Здоровье', streak: 18, days: [1, 1, 1, 1, 1, 0, 0], doneToday: true, color: 'mint' },
	{ id: 2, name: '30 минут чтения', category: 'Развитие', streak: 9, days: [1, 1, 0, 1, 1, 1, 0], doneToday: true, color: 'coral' },
	{ id: 3, name: 'Английский', category: 'Обучение', streak: 6, days: [1, 0, 1, 1, 1, 0, 0], doneToday: false, color: 'blue' },
	{ id: 4, name: 'Без телефона после 22:00', category: 'Фокус', streak: 4, days: [0, 1, 1, 1, 0, 0, 0], doneToday: false, color: 'sand' },
]

function MarkIcon({ type }) {
	const paths = {
		grid: <><rect x='4' y='4' width='6' height='6' rx='1' /><rect x='14' y='4' width='6' height='6' rx='1' /><rect x='4' y='14' width='6' height='6' rx='1' /><rect x='14' y='14' width='6' height='6' rx='1' /></>,
		chart: <><path d='M5 19V9' /><path d='M12 19V5' /><path d='M19 19v-7' /></>,
		calendar: <><rect x='3.5' y='5.5' width='17' height='15' rx='2' /><path d='M8 3v5M16 3v5M3.5 10h17' /></>,
		settings: <><circle cx='12' cy='12' r='3' /><path d='M19 12a7 7 0 0 0-.12-1.3l2-1.55-2-3.46-2.46 1A7 7 0 0 0 14.2 5.4L13.85 3h-4l-.35 2.4a7 7 0 0 0-2.22 1.29l-2.46-1-2 3.46 2 1.55A7 7 0 0 0 4.7 12c0 .44.04.87.12 1.3l-2 1.55 2 3.46 2.46-1A7 7 0 0 0 9.5 18.6l.35 2.4h4l.35-2.4a7 7 0 0 0 2.22-1.29l2.46 1 2-3.46-2-1.55c.08-.43.12-.86.12-1.3Z' /></>,
	}

	return <svg viewBox='0 0 24 24' aria-hidden='true'>{paths[type]}</svg>
}

function HabitRow({ habit, onToggle }) {
	return (
		<article className='habit-row'>
			<button
				className={`habit-check ${habit.doneToday ? 'is-done' : ''}`}
				type='button'
				aria-label={`${habit.doneToday ? 'Отменить выполнение' : 'Отметить выполненной'}: ${habit.name}`}
				aria-pressed={habit.doneToday}
				onClick={() => onToggle(habit.id)}
			>
				<span aria-hidden='true'>✓</span>
			</button>
			<div className='habit-copy'>
				<strong>{habit.name}</strong>
				<span><i className={`habit-color ${habit.color}`} />{habit.category}</span>
			</div>
			<div className='week-strip' role='img' aria-label={`Выполнение за неделю: ${habit.name}`}>
				{habit.days.map((done, index) => <i className={done ? 'is-filled' : ''} key={`${habit.id}-${weekDays[index]}`}><span>{weekDays[index]}</span></i>)}
			</div>
			<div className='streak'><strong>{habit.streak}</strong><span>дней подряд</span></div>
		</article>
	)
}

export default function App() {
	const apiBase = import.meta.env.VITE_BACKEND_URL?.replace(/\/$/, '') || ''
	const [habits, setHabits] = useState(initialHabits)
	const [source, setSource] = useState(apiBase ? 'Подключение…' : 'Демо-режим')
	const [composerOpen, setComposerOpen] = useState(false)
	const [habitName, setHabitName] = useState('')

	useEffect(() => {
		if (!apiBase) return

		const controller = new AbortController()
		async function loadRemoteHabits() {
			try {
				const usersResponse = await fetch(`${apiBase}/users`, { signal: controller.signal })
				if (!usersResponse.ok) throw new Error('Users request failed')
				const users = await usersResponse.json()
				if (!users.length) {
					setSource('API подключён · данных пока нет')
					return
				}

				const habitsResponse = await fetch(`${apiBase}/users/${users[0].id}/habits`, { signal: controller.signal })
				if (!habitsResponse.ok) throw new Error('Habits request failed')
				const remoteHabits = await habitsResponse.json()
				setHabits(remoteHabits.map((habit, index) => ({
					...habit,
					category: 'Из Telegram',
					streak: habit.done_count,
					days: weekDays.map((_, day) => day < Math.min(habit.done_count, 5)),
					doneToday: false,
					color: ['mint', 'coral', 'blue', 'sand'][index % 4],
				})))
				setSource('API подключён')
			} catch (error) {
				if (error.name !== 'AbortError') setSource('Демо-режим · API недоступен')
			}
		}

		loadRemoteHabits()
		return () => controller.abort()
	}, [apiBase])

	const completed = habits.filter(habit => habit.doneToday).length
	const progress = habits.length ? Math.round((completed / habits.length) * 100) : 0
	const totalMarks = useMemo(() => habits.reduce((sum, habit) => sum + habit.days.filter(Boolean).length, 0), [habits])

	function toggleHabit(id) {
		setHabits(current => current.map(habit => habit.id === id ? { ...habit, doneToday: !habit.doneToday } : habit))
	}

	function addHabit(event) {
		event.preventDefault()
		const name = habitName.trim()
		if (!name) return
		setHabits(current => [...current, {
			id: Date.now(),
			name,
			category: 'Новая привычка',
			streak: 0,
			days: [0, 0, 0, 0, 0, 0, 0],
			doneToday: false,
			color: 'mint',
		}])
		setHabitName('')
		setComposerOpen(false)
	}

	return (
		<div className='app-shell'>
			<aside className='sidebar'>
				<a className='brand' href='#top' aria-label='Komplektoff Habit — главная'>
					<span className='brand-mark'><i /><i /><i /></span>
					<span>Komplektoff<span>Habit</span></span>
				</a>
				<nav aria-label='Навигация приложения'>
					<a className='active' href='#today'><MarkIcon type='grid' />Сегодня</a>
					<a href='#progress'><MarkIcon type='chart' />Прогресс</a>
					<a href='#week'><MarkIcon type='calendar' />Календарь</a>
					<a href='#settings'><MarkIcon type='settings' />Настройки</a>
				</nav>
				<div className='sidebar-note'><span>Серия недели</span><strong>6 дней</strong><p>Лучший результат за последние два месяца.</p></div>
				<div className='profile'><span>MT</span><div><strong>Матвей</strong><small>{source}</small></div></div>
			</aside>

			<main id='top'>
				<header className='topbar'>
					<a className='mobile-brand' href='#top'>Komplektoff Habit</a>
					<div><span>{source}</span><i /></div>
					<button type='button' onClick={() => setComposerOpen(true)}>Новая привычка <span>+</span></button>
				</header>

				<div className='dashboard'>
					<section id='today' className='page-heading'>
						<div><p className='eyebrow'>Личный ритм</p><h1>Сегодня</h1><p>Пятница, 28 августа · спокойно продолжайте начатое.</p></div>
						<div className='score-ring' style={{ '--progress': `${progress * 3.6}deg` }}><strong>{progress}%</strong><span>выполнено</span></div>
					</section>

					<section className='summary-grid' aria-label='Сводка за сегодня'>
						<article><span>План на день</span><strong>{completed} <small>/ {habits.length}</small></strong><p>привычки отмечены</p></article>
						<article><span>Текущая серия</span><strong>6 <small>дней</small></strong><p>личный ритм сохраняется</p></article>
						<article><span>За эту неделю</span><strong>{totalMarks}</strong><p>выполнений всего</p></article>
					</section>

					<section id='week' className='habits-panel'>
						<div className='panel-heading'><div><p className='eyebrow'>Неделя 35</p><h2>Привычки</h2></div><div className='week-legend'>{weekDays.map(day => <span key={day}>{day}</span>)}</div></div>
						<div className='habit-list'>{habits.map(habit => <HabitRow habit={habit} onToggle={toggleHabit} key={habit.id} />)}</div>
					</section>

					<section id='progress' className='insights-grid'>
						<article className='rhythm-card'><div><p className='eyebrow'>Последние 8 недель</p><h2>Ритм становится устойчивее</h2></div><div className='bars'>{[43, 56, 49, 68, 64, 77, 82, 88].map((height, index) => <i key={index} style={{ height: `${height}%` }}><span>{index + 1}</span></i>)}</div></article>
						<article className='focus-card'><p className='eyebrow'>Наблюдение</p><h2>Лучший день — четверг</h2><p>В этот день вы выполняете в среднем 87% запланированных привычек.</p><div><span>Стабильность</span><strong>+14%</strong></div></article>
					</section>
				</div>
			</main>

			{composerOpen ? (
				<div className='composer-backdrop' role='presentation' onMouseDown={() => setComposerOpen(false)}>
					<form className='composer' onSubmit={addHabit} onMouseDown={event => event.stopPropagation()}>
						<div><p className='eyebrow'>Новый ритуал</p><button type='button' aria-label='Закрыть' onClick={() => setComposerOpen(false)}>×</button></div>
						<label htmlFor='habit-name'>Что хотите делать регулярно?</label>
						<input id='habit-name' autoFocus value={habitName} onChange={event => setHabitName(event.target.value)} placeholder='Например, вечерняя прогулка' />
						<button type='submit'>Добавить привычку</button>
					</form>
				</div>
			) : null}
		</div>
	)
}
