import { en } from './en'
import { gu } from './gu'
import { hi } from './hi'

export type Language = 'English' | 'Gujarati' | 'Hindi'
const dictionaries = { English: en, Gujarati: gu, Hindi: hi }
export function dictionary(language: Language) { return dictionaries[language] }
