import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Cloud, Loader2, Pause, Volume2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { weather as fetchWeather } from "../api/predictions";
import { request } from "../api/client";
import { Button, Card } from "../components/ui";
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
        const audio = new Audio(`data:audio/mp3;base64,${response.audioContent}`);
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
    <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" />
      <span className="ml-3">{t("loadingWeatherData")}</span>
    </div>
  );
  if (isError || !data) return (
    <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">
      {t("failedWeatherData")}
    </div>
  );

  const temp = formatTemperature(data.temperature_celsius, units);
  const hum = data.humidity_percent ?? "--";
  const wind = formatWindSpeed(data.wind_speed_mps, units);
  const conditionTranslated = translateWeather(data.condition, language);

  const AudioButton = ({ text }: { text: string }) => (
    <Button variant="secondary" size="sm" onClick={() => toggleAudio(text)} disabled={isLoadingAudio || !text}>
      {isLoadingAudio ? <Loader2 size={16} className="animate-spin" /> : isPlaying ? <Pause size={16} /> : <Volume2 size={16} />}
      {isLoadingAudio ? "Loading..." : isPlaying ? t("pauseAudio") : t("listenAdvisory")}
    </Button>
  );

  return (
    <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("regionalWeatherContext")}</h1>
          <p className="mt-2 text-muted">{t("currentConditionsAroundFarm")}</p>
        </div>
        <Link to="/dashboard"><Button variant="secondary" size="sm">{t("backToDashboard")}</Button></Link>
      </div>

      <div className="flex flex-col justify-between gap-8 rounded-lg bg-farmer-900 p-7 text-white shadow-card sm:flex-row sm:items-center sm:p-10">
        <div>
          <h2 className="font-display text-6xl text-farmer-200">{temp}</h2>
          <p className="mt-3 text-sm font-semibold uppercase tracking-wide text-white/70">
            {conditionTranslated.toUpperCase()} • {user?.location || t("farmLocation")}
          </p>
        </div>
        <div className="text-farmer-300">
          <Cloud size={100} />
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("humidity")}</h4>
          <p className="mt-3 font-display text-3xl text-ink">{hum}%</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("windSpeed")}</h4>
          <p className="mt-3 font-display text-3xl text-ink">{wind}</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("status")}</h4>
          <p className="mt-3 font-display text-3xl text-farmer-700">{t("active")}</p>
        </Card>
      </div>

      <Card className="border-farmer-200 bg-farmer-50" padding="lg">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <h3 className="font-display text-2xl text-farmer-900">{t("agronomicWeatherAdvisory")}</h3>
            {isTranslating && (
              <span className="inline-flex items-center gap-1.5 text-xs text-farmer-700">
                <Loader2 size={12} className="animate-spin" /> {t("translating")}
              </span>
            )}
          </div>
          <AudioButton text={activeAdvisory} />
        </div>
        <p className="mt-4 leading-7 text-muted whitespace-pre-wrap">
          {activeAdvisory}
        </p>
      </Card>
    </motion.div>
  );
}
