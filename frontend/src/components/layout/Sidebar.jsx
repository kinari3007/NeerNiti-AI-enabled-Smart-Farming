import { NavLink, Link } from 'react-router-dom'
import {
  LeafMark,
  LeafSprig,
  IconHome,
  IconSoil,
  IconHistory,
  IconProfile,
  IconClose,
} from '../../assets/illustrations/decor'
import './Sidebar.css'

const NAV_ITEMS = [
  { to: '/app', label: 'Home', icon: <IconHome />, end: true },
  { to: '/app/analyze', label: 'Analyze Soil', icon: <IconSoil /> },
  { to: '/app/history', label: 'History', icon: <IconHistory /> },
  { to: '/app/profile', label: 'Profile', icon: <IconProfile /> },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      <div
        className={`sidebar__scrim ${open ? 'sidebar__scrim--visible' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
        <div className="sidebar__header">
          <Link to="/" className="sidebar__brand" onClick={onClose}>
            <LeafMark size={30} />
            <span className="sidebar__brand-text">
              <span className="sidebar__brand-name">NeerNiti</span>
              <span className="sidebar__brand-tag">Smarter Soil. Better Harvests.</span>
            </span>
          </Link>
          <button className="sidebar__close" onClick={onClose} aria-label="Close menu">
            <IconClose size={22} />
          </button>
        </div>

        <nav className="sidebar__nav" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
              }
            >
              <span className="sidebar__link-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__footer">
          <LeafSprig className="sidebar__sprig" />
          <p className="sidebar__quote">"Healthy soil builds a better tomorrow."</p>
        </div>
      </aside>
    </>
  )
}
