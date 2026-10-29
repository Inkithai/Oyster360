'use client'

import React, { createContext, useContext, useState } from 'react'

export type Locale = 'en' | 'si' | 'ta'

type Dictionary = Record<string, { en: string; si: string; ta: string }>

export const TRANSLATIONS: Dictionary = {
  tagline: {
    en: 'Sri Lanka Mushroom Farm Management',
    si: 'ශ්‍රී ලංකා බිම්මල් වගා කළමනාකරණය',
    ta: 'இலங்கை காளான் பண்ணை மேலாண்மை',
  },
  dashboard: {
    en: 'Dashboard',
    si: 'ප්‍රධාන පුවරුව',
    ta: 'முகப்புப் பலகை',
  },
  batches: {
    en: 'Batches',
    si: 'වගා කාණ්ඩ (මලු)',
    ta: 'வளர்ப்பு தொகுதிகள்',
  },
  harvests: {
    en: 'Harvests & Flushes',
    si: 'අස්වැන්න සටහන්',
    ta: 'அறுவடை பதிவுகள்',
  },
  finance: {
    en: 'Profit & Costs (LKR)',
    si: 'ලාභය සහ වියදම් (රු.)',
    ta: 'லாபம் & செலவுகள் (ரூ.)',
  },
  sales: {
    en: 'Buyers & Sales',
    si: 'ගැනුම්කරුවන් සහ විකුණුම්',
    ta: 'வாங்குபவர்கள் & விற்பனை',
  },
  inventory: {
    en: 'Inventory',
    si: 'අමුද්‍රව්‍ය තොග',
    ta: 'கையிருப்பு',
  },
  recipes: {
    en: 'Recipes',
    si: 'වගා මාධ්‍ය වට්ටෝරු',
    ta: 'வளர்ப்பு ஊடக முறைகள்',
  },
  strains: {
    en: 'Strains',
    si: 'බිම්මල් ප්‍රභේද (DOA)',
    ta: 'காளான் வகைகள் (DOA)',
  },
  analytics: {
    en: 'Analytics',
    si: 'විශ්ලේෂණ වාර්තා',
    ta: 'பகுப்பாய்வு',
  },
  quickHarvest: {
    en: '60s Harvest Entry',
    si: 'තත්පර 60 අස්වැන්න ඇතුළත් කිරීම',
    ta: '60 விநாடி அறுவடைப் பதிவு',
  },
}

interface I18nContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: keyof typeof TRANSLATIONS) => string
}

const I18nContext = createContext<I18nContextValue>({
  locale: 'en',
  setLocale: () => undefined,
  t: (key) => TRANSLATIONS[key]?.en ?? String(key),
})

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>('en')

  const t = (key: keyof typeof TRANSLATIONS): string => {
    const entry = TRANSLATIONS[key]
    if (!entry) return String(key)
    return entry[locale] || entry.en
  }

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  return useContext(I18nContext)
}
