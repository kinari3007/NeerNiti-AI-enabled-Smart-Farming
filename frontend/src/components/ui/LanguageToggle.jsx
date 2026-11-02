import './LanguageToggle.css'
import { useLanguage } from '../../context/language-context'

export default function LanguageToggle() {
  const { language, setLanguage } = useLanguage()
  const nextLanguage = language === 'en' ? 'gu' : 'en'

  return (
    <button
      className="language-toggle"
      type="button"
      onClick={() => setLanguage(nextLanguage)}
      aria-label={language === 'en' ? 'ગુજરાતીમાં ફેરવો' : 'Switch to English'}
      title={language === 'en' ? 'ગુજરાતીમાં ફેરવો' : 'Switch to English'}
    >
      {language === 'en' ? 'ગુજરાતી' : 'English'}
    </button>
  )
}
