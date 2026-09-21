import { en } from "./en";
import { gu } from "./gu";
import { hi } from "./hi";

export type Language = "English" | "Gujarati" | "Hindi";
export type Units = "Metric" | "Imperial";

export type TranslationKey = keyof typeof en;

const dictionaries: Record<Language, Record<TranslationKey, string>> = {
  English: en,
  Gujarati: gu,
  Hindi: hi,
};

export function dictionary(language: Language = "English") {
  return dictionaries[language] || dictionaries.English;
}

export function t(key: TranslationKey, language: Language = "English"): string {
  const dict = dictionary(language);
  return dict[key] || en[key] || key;
}
