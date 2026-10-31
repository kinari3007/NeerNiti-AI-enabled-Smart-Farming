import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { session } from '../../api/session'
import './AppLayout.css'

export default function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  // useLocation triggers a re-render on navigation, so the name stays fresh
  // after it's changed on the Profile page.
  useLocation()
  const name = session.getName() || 'Farmer'

  return (
    <div className="app-layout">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="app-layout__main">
        <div className="app-layout__container">
          <TopBar
            onMenu={() => setMenuOpen(true)}
            name={name}
            subtitle="Let's make your farm more productive with the right fertilizer."
          />
          <Outlet />
        </div>
      </div>
    </div>
  )
}
