import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Cloud, Loader2, Pause, Volume2 } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { weather as fetchWeather } from "../api/predictions";
import { request } from "../api/client";
import { Button, Card, Skeleton } from "../components/ui";
import { formatTemperature, formatWindSpeed } from "../lib/format";
import { translateWeather } from "../i18n/domain";

export default function WeatherPage() {
  const { user, token, units, language, t } = useAuth();
  const targetLang = language === "Hindi" ? "hi" : language === "Gujarati" ? "gu" : "en";

  const [localTranslations, setLocalTranslations] = useState<Record<string, string>>({});
  const [isTranslating, setIsTranslating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const inFlightLangRef = useRef<string | null>(null);
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ["weather", user?.latitude, user?.longitude, targetLang],
    queryFn: () => fetchWeather(user?.latitude || 0, user?.longitude || 0, token!, targetLang),
    enabled: !!token,
  });

  const advisoryFallback = (data?.humidity_percent || 0) > 70 
    ? t("weatherAdvisoryHighHumidity")
    : (data?.temperature_celsius || 0) > 35
    ? t("weatherAdvisoryHighHeat")
    : t("weatherAdvisoryOptimal");

  const canonicalAdvisory = data?.advisory || advisoryFallback;
  const activeAdvisory = targetLang === "en"
    ? canonicalAdvisory
    : localTranslations[targetLang] || data?.translations?.[targetLang] || (data?.translated_advisory ? data.translated_advisory : advisoryFallback);

  // Auto-translate if user switches language and translation is not yet present
  useEffect(() => {
    if (targetLang !== "en" && canonicalAdvisory && token) {
      const alreadyHas = localTranslations[targetLang] || data?.translations?.[targetLang] || !!data?.translated_advisory;
      if (!alreadyHas && inFlightLangRef.current !== targetLang) {
        inFlightLangRef.current = targetLang;
        setIsTranslating(true);
        request<{ translated_text: string }>("/weather/translate", {
          method: "POST",
          body: JSON.stringify({ text: canonicalAdvisory, target_language: targetLang }),
        }, token)
          .then((res) => {
            if (res?.translated_text) {
              setLocalTranslations((prev) => ({ ...prev, [targetLang]: res.translated_text }));
            }
          })
          .catch((err) => console.error("Weather advisory translation error:", err))
          .finally(() => {
            inFlightLangRef.current = null;
            setIsTranslating(false);
          });
      }
    }
  }, [targetLang, canonicalAdvisory, data, localTranslations, token]);

  // Reset audio playback when language or advisory text changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
  }, [targetLang, activeAdvisory]);

  const toggleAudio = async (text: string) => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
      return;
    }
    try {
      setIsLoadingAudio(true);
      const response: any = await request("/tts", {
        method: "POST",
        body: JSON.stringify({ text, language: targetLang }),
      }, token!);
      if (response?.audioContent) {
        const format = response.format || (response.audioContent.startsWith("UklGR") ? "wav" : "mpeg");
        const mimeType = format === "wav" ? "audio/wav" : "audio/mpeg";
        const audio = new Audio(`data:${mimeType};base64,${response.audioContent}`);
        audioRef.current = audio;
        audio.onended = () => setIsPlaying(false);
        audio.onpause = () => setIsPlaying(false);
        audio.onplay = () => setIsPlaying(true);
        await audio.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error("Weather advisory TTS failed:", error);
      setIsPlaying(false);
    } finally {
      setIsLoadingAudio(false);
    }
  };

  if (isLoading) return (
    <div className="space-y-6 pb-12">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="rounded-sm border border-line bg-surface p-8 space-y-4">
        <Skeleton className="h-14 w-36" />
        <Skeleton className="h-5 w-52" />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-sm border border-line bg-surface p-6 space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-8 w-24" />
        </div>
        <div className="rounded-sm border border-line bg-surface p-6 space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-8 w-24" />
        </div>
        <div className="rounded-sm border border-line bg-surface p-6 space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-8 w-24" />
        </div>
      </div>
    </div>
  );
  if (isError || !data) return (
    <div className="rounded-sm border border-red-300 bg-red-50 p-6 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
      {t("failedWeatherData")}
    </div>
  );

  const temp = formatTemperature(data.temperature_celsius, units);
  const hum = data.humidity_percent ?? "N/A";
  const wind = formatWindSpeed(data.wind_speed_mps, units);
  const conditionTranslated = translateWeather(data.condition, language);

  const AudioButton = ({ text }: { text: string }) => (
    <Button variant="secondary" size="sm" onClick={() => toggleAudio(text)} disabled={isLoadingAudio || !text}>
      {isLoadingAudio ? <Loader2 size={16} className="animate-spin" /> : isPlaying ? <Pause size={16} /> : <Volume2 size={16} />}
      {isLoadingAudio ? t("loading") : isPlaying ? t("pauseAudio") : t("listenAdvisory")}
    </Button>
  );

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("meteorologicalIntelligence")}</span>
          <h1 className="mt-1 font-display text-2xl sm:text-3xl text-ink">{t("regionalWeatherContext")}</h1>
          <p className="mt-1 text-xs text-muted">{t("currentConditionsAroundFarm")}</p>
        </div>
        <Link to="/dashboard"><Button variant="secondary" size="sm">{t("backToDashboard")}</Button></Link>
      </div>

      <div className="flex flex-col justify-between gap-8 rounded-sm border border-line bg-surface p-6 sm:flex-row sm:items-center sm:p-8">
        <div>
          <h2 className="font-display text-5xl text-ink">{temp}</h2>
          <p className="mt-2 text-xs font-semibold uppercase tracking-wider text-muted">
            {conditionTranslated.toUpperCase()} - {user?.location || t("farmLocation")}
          </p>
        </div>
        <div className="text-farmer-700 dark:text-farmer-300">
          <Cloud size={64} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="text-center">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("humidity")}</h4>
          <p className="mt-2 font-display text-2xl text-ink">{hum}%</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("windSpeed")}</h4>
          <p className="mt-2 font-display text-2xl text-ink">{wind}</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("status")}</h4>
          <p className="mt-2 font-display text-2xl text-farmer-700 dark:text-farmer-300 font-semibold">{t("active")}</p>
        </Card>
      </div>

      <Card className="border-line bg-surface" padding="lg">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
          <div className="flex items-center gap-3">
            <h3 className="font-display text-xl text-ink">{t("agronomicWeatherAdvisory")}</h3>
            {isTranslating && (
              <span className="inline-flex items-center gap-1.5 text-xs text-muted">
                <Loader2 size={12} className="animate-spin text-farmer-700" /> {t("translating")}
              </span>
            )}
          </div>
          <AudioButton text={activeAdvisory} />
        </div>
        <p className="mt-4 leading-7 text-muted dark:text-farmer-100/90 whitespace-pre-wrap">
          {activeAdvisory}
        </p>
      </Card>
    </div>
  );
}
