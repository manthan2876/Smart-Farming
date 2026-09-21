import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getPrediction } from "../api/predictions";
import { AlertCircle, Loader2, Check, Wheat, Leaf, TreeDeciduous, Sprout, Clover, Sparkles } from "lucide-react";
import { Button, Card } from "../components/ui";
import { getWebSocketUrl } from "../api/client";

interface StageStatus {
  preprocessing: boolean;
  crop_identification: boolean;
  disease_classification: boolean;
  pest_detection: boolean;
  recommendation: boolean;
  pipeline: boolean;
}

const INITIAL_STAGES: StageStatus = {
  preprocessing: true,
  crop_identification: false,
  disease_classification: false,
  pest_detection: false,
  recommendation: false,
  pipeline: false,
};

const ALL_STAGES_DONE: StageStatus = {
  preprocessing: true,
  crop_identification: true,
  disease_classification: true,
  pest_detection: true,
  recommendation: true,
  pipeline: true,
};

const MAX_WS_RETRIES = 6;
// Show the finished checklist briefly if the user actually watched it run; jump straight to
// the result when everything was already done on arrival (cached / very fast scans).
const REDIRECT_DELAY_LIVE_MS = 1500;
const REDIRECT_DELAY_INSTANT_MS = 400;

export default function ProcessingPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const predictionId = Number(id);
  const { token } = useAuth();
  const queryClient = useQueryClient();

  // Local state for tracking real-time pipeline events
  const [stages, setStages] = useState<StageStatus>(INITIAL_STAGES);
  const [detectedCrop, setDetectedCrop] = useState<{ label?: string; confidence?: number } | null>(null);
  const [detectedDisease, setDetectedDisease] = useState<{ label?: string; confidence?: number } | null>(null);
  const [detectedPests, setDetectedPests] = useState<Array<{ label?: string; confidence?: number }>>([]);
  const [liveMessage, setLiveMessage] = useState("");
  const [failure, setFailure] = useState<string | null>(null);

  // true once the pipeline reached a final state (completed / failed): stops WS reconnects
  const terminalRef = useRef(false);
  // true once we received at least one "processing" event, i.e. the user watched it run live
  const wasLiveRef = useRef(false);

  // Background fetch + gentle poll. This is the safety net when the WebSocket is down or an
  // event was lost, so every stage still shows up (at poll granularity).
  const { data: prediction, error } = useQuery({
    queryKey: ["prediction", predictionId],
    queryFn: () => getPrediction(String(predictionId), token || ''),
    enabled: !isNaN(predictionId),
    refetchInterval: (query) => {
      const latest = (query.state.data as any)?.follow_up || query.state.data;
      const pipelineStatus = typeof latest?.status === "object" ? (latest?.status as any)?.pipeline : latest?.status;
      const isDone = pipelineStatus === "completed" || pipelineStatus === "failed" || pipelineStatus === "ready";
      return isDone ? false : 1500;
    },
  });

  // Sync state if prediction already has fields in DB
  useEffect(() => {
    if (!prediction) return;
    const target: any = prediction.follow_up || prediction;
    const st = target.status as any;

    // Failed runs: stop the spinner and show the reason.
    if (st === "failed" || (typeof st === "object" && st !== null && st.pipeline === "failed")) {
      terminalRef.current = true;
      setFailure(target.error || (prediction as any).error || "Analysis failed. Please try again with a clearer photo.");
      return;
    }

    if (target.crop?.label) {
      setDetectedCrop((prev) => prev || target.crop);
      setStages((prev) => ({ ...prev, crop_identification: true }));
    }

    if (target.disease?.label) {
      setDetectedDisease((prev) => prev || target.disease);
      setStages((prev) => ({ ...prev, disease_classification: true, crop_identification: true }));
    }

    if (target.pests && target.pests.length > 0) {
      setDetectedPests((prev) => (prev.length > 0 ? prev : target.pests));
      setStages((prev) => ({
        ...prev,
        pest_detection: true,
        disease_classification: true,
        crop_identification: true,
      }));
    }

    if (typeof st === "object" && st !== null) {
      setStages((prev) => ({
        ...prev,
        crop_identification: prev.crop_identification || st.crop_identification === "completed" || Boolean(target.crop?.label),
        disease_classification: prev.disease_classification || st.disease_classification === "completed" || Boolean(target.disease?.label),
        pest_detection: prev.pest_detection || st.pest_detection === "completed" || Boolean(target.pests?.length),
        recommendation: prev.recommendation || st.recommendation === "completed",
        pipeline: prev.pipeline || st.pipeline === "completed",
      }));
      if (st.pipeline === "completed") terminalRef.current = true;
    } else if (st === "ready" || st === "completed") {
      terminalRef.current = true;
      setStages(ALL_STAGES_DONE);
    }
  }, [prediction]);

  // WebSocket for real-time progress, with automatic reconnect.
  // The server replays already-completed stages on every (re)connect, so a reconnect
  // always catches up without needing any client-side bookkeeping.
  useEffect(() => {
    if (isNaN(predictionId)) return;

    let ws: WebSocket | null = null;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;
    let attempt = 0;
    let disposed = false;

    const handleEvent = (raw: string) => {
      let data: any;
      try {
        data = JSON.parse(raw);
      } catch (e) {
        console.error("WS parse error", e);
        return;
      }

      const stage: string = data.stage;
      const msg: string = data.message || "";
      const payload = data.data || {};

      // Terminal failure reported by the worker
      if (stage === "failed" || data.status === "failed") {
        terminalRef.current = true;
        setFailure(data.error || msg || "Analysis failed. Please try again with a clearer photo.");
        return;
      }

      // "A stage just started": drives the live status line under the title
      if (data.status === "processing") {
        wasLiveRef.current = true;
        if (msg) setLiveMessage(msg);
        return;
      }

      // Ingest any payload data received across all messages
      if (payload.crop?.label) {
        setDetectedCrop(payload.crop);
        setStages((prev) => ({ ...prev, crop_identification: true }));
      }
      if (payload.disease?.label) {
        setDetectedDisease(payload.disease);
        setStages((prev) => ({ ...prev, disease_classification: true, crop_identification: true }));
      }
      if (payload.pests && payload.pests.length > 0) {
        setDetectedPests(payload.pests);
        setStages((prev) => ({
          ...prev,
          pest_detection: true,
          disease_classification: true,
          crop_identification: true,
        }));
      }

      const isCompleted = data.status === "completed";

      if (stage === "crop_identification" && isCompleted) {
        setStages((prev) => ({ ...prev, crop_identification: true }));
        if (!payload.crop?.label && msg) {
          const match = msg.match(/Detected\s+(.+?)(?:\s+\(([\d.]+)%\))?$/i);
          if (match) {
            setDetectedCrop({ label: match[1], confidence: match[2] ? parseFloat(match[2]) / 100 : 1.0 });
          }
        }
      } else if (stage === "disease_classification" && isCompleted) {
        setStages((prev) => ({
          ...prev,
          disease_classification: true,
          crop_identification: true,
        }));
        if (!payload.disease?.label && msg) {
          const match = msg.match(/Classified as\s+(.+?)(?:\s+\(([\d.]+)%\))?$/i);
          if (match) {
            setDetectedDisease({ label: match[1], confidence: match[2] ? parseFloat(match[2]) / 100 : 1.0 });
          }
        }
      } else if (stage === "pest_detection" && isCompleted) {
        setStages((prev) => ({
          ...prev,
          pest_detection: true,
          disease_classification: true,
          crop_identification: true,
        }));
        if ((!payload.pests || payload.pests.length === 0) && msg) {
          if (msg.toLowerCase().includes("no pests")) {
            setDetectedPests([]);
          } else {
            setDetectedPests(msg.split(", ").map((label: string) => ({ label: label.trim() })));
          }
        }
      } else if ((stage === "llm_advisory" || stage === "recommendation") && isCompleted) {
        setStages((prev) => ({ ...prev, recommendation: true }));
      } else if (stage === "completed" && isCompleted) {
        terminalRef.current = true;
        setLiveMessage("");
        setStages(ALL_STAGES_DONE);
        queryClient.invalidateQueries({ queryKey: ["prediction", predictionId] });
      }
    };

    const connect = () => {
      if (disposed || terminalRef.current) return;

      const socket = new WebSocket(getWebSocketUrl(`/ws/predictions/${predictionId}`));
      ws = socket;

      socket.onopen = () => {
        attempt = 0;
      };
      socket.onmessage = (event) => handleEvent(event.data);
      socket.onerror = () => {
        // onclose fires right after onerror and handles the retry.
        console.warn("[ProcessingPage] WebSocket error; polling continues as fallback");
      };
      socket.onclose = () => {
        if (disposed || terminalRef.current) return;
        if (attempt >= MAX_WS_RETRIES) {
          console.warn("[ProcessingPage] WebSocket gave up reconnecting; relying on polling");
          return;
        }
        const delay = Math.min(1000 * 2 ** attempt, 8000);
        attempt += 1;
        retryTimer = setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      disposed = true;
      if (retryTimer) clearTimeout(retryTimer);
      if (ws) {
        const socket = ws;
        socket.onmessage = null;
        socket.onerror = null;
        socket.onclose = null;
        if (socket.readyState === WebSocket.CONNECTING) {
          // Closing a still-connecting socket logs a browser warning (React StrictMode
          // double-mount), so close it as soon as it opens instead.
          socket.onopen = () => socket.close();
        } else if (socket.readyState === WebSocket.OPEN) {
          socket.close();
        }
      }
    };
  }, [predictionId, queryClient]);

  // Animated icon rotation for the active scanning stage
  const [activeCropIdx, setActiveCropIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setActiveCropIdx((prev) => (prev + 1) % 5), 400);
    return () => clearInterval(t);
  }, []);

  // When the pipeline is complete, show the finished checklist briefly, then navigate.
  // (No "already redirected" ref: it broke the redirect whenever this effect re-ran, because
  // the cleanup cleared the timer and the guard then prevented re-arming it.)
  useEffect(() => {
    if (!stages.pipeline || failure) return;
    const delay = wasLiveRef.current ? REDIRECT_DELAY_LIVE_MS : REDIRECT_DELAY_INSTANT_MS;
    const timer = setTimeout(() => {
      navigate(`/predictions/${predictionId}`, { replace: true });
    }, delay);
    return () => clearTimeout(timer);
  }, [stages.pipeline, failure, navigate, predictionId]);

  // Derived display values with logical pipeline invariance
  const isPreprocDone = stages.preprocessing;
  const isCropDone =
    stages.crop_identification ||
    stages.disease_classification ||
    stages.pest_detection ||
    stages.recommendation ||
    stages.pipeline ||
    Boolean(detectedCrop?.label);

  const isDiseaseDone =
    stages.disease_classification ||
    stages.pest_detection ||
    stages.recommendation ||
    stages.pipeline ||
    Boolean(detectedDisease?.label);

  const isPestDone =
    stages.pest_detection ||
    stages.recommendation ||
    stages.pipeline ||
    detectedPests.length > 0;

  const isAdvisoryDone = stages.recommendation || stages.pipeline;

  const cropConfStr = detectedCrop?.confidence ? ` (${(detectedCrop.confidence * 100).toFixed(1)}%)` : "";
  const cropText = detectedCrop?.label ? `${detectedCrop.label}${cropConfStr}` : (isCropDone ? "Identified" : "Scanning species...");

  const diseaseConfStr = detectedDisease?.confidence ? ` (${(detectedDisease.confidence * 100).toFixed(1)}%)` : "";
  const diseaseText = detectedDisease?.label ? `${detectedDisease.label}${diseaseConfStr}` : (isDiseaseDone ? "Identified" : "Analyzing pathology...");

  const pestText = detectedPests.length > 0
    ? detectedPests.map((p) => p.label || "Pest").join(", ")
    : isPestDone
    ? "No Pests Detected"
    : null;

  const CROP_ICONS = [<Wheat size={20} key="1" />, <Leaf size={20} key="2" />, <TreeDeciduous size={20} key="3" />, <Sprout size={20} key="4" />, <Clover size={20} key="5" />];

  const renderStage = (
    stageNumber: number,
    title: string,
    isUnlocked: boolean,
    isComplete: boolean,
    icon: React.ReactNode,
    detail: React.ReactNode
  ) => (
    <div className={`flex items-start gap-4 transition-opacity sm:gap-6 ${isUnlocked ? "opacity-100" : "opacity-40"}`}>
      <div
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${
          isComplete ? "bg-farmer-600 text-white" : isUnlocked ? "bg-expert-100 text-expert-700" : "bg-canvas text-muted"
        }`}
      >
        {isComplete ? <Check size={22} /> : icon || stageNumber}
      </div>
      <div className="min-w-0 pt-1">
        <h4 className="font-semibold text-ink">
          {stageNumber}. {title}
        </h4>
        <div className="mt-1 text-sm text-muted">{detail}</div>
      </div>
    </div>
  );

  // Only show the blocking error screen if we have nothing to show. A single failed poll while
  // we already hold data (or while the WebSocket is still delivering events) is not fatal.
  if (error && !prediction) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center text-center text-danger">
        <h2 className="font-display text-2xl">Error Loading Status</h2>
        <p className="mt-2 text-sm text-muted">Something went wrong. Please check your network connection.</p>
        <Button variant="secondary" className="mt-5" onClick={() => navigate("/dashboard")}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  if (failure) {
    return (
      <div className="mx-auto max-w-3xl py-4 sm:py-8">
        <Card padding="lg">
          <div className="text-center">
            <AlertCircle size={48} className="mx-auto text-danger" />
            <h2 className="mt-6 font-display text-2xl text-ink">Analysis Failed</h2>
            <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted">{failure}</p>
            <Button variant="secondary" className="mt-6" onClick={() => navigate("/dashboard")}>
              Back to Dashboard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl py-4 sm:py-8">
      <Card padding="lg">
        <div className="text-center">
          <Loader2 size={48} className="mx-auto animate-spin text-farmer-600" />
          <h2 className="mt-6 font-display text-2xl text-ink">Running AI Pipeline</h2>
          <p className="mt-2 text-sm text-muted">Analyzing your crop and generating diagnostics in real-time...</p>
          {liveMessage && !stages.pipeline && (
            <p className="mt-2 text-xs font-medium text-expert-700" aria-live="polite">
              {liveMessage}
            </p>
          )}
        </div>
        <div className="mt-10 space-y-8">
          {renderStage(1, "Image Preprocessing", true, isPreprocDone, null, "Verified leaf presence and clarity.")}

          {renderStage(
            2,
            "Crop Identification",
            true,
            isCropDone,
            isCropDone ? null : CROP_ICONS[activeCropIdx],
            isCropDone ? (
              <span className="font-semibold text-farmer-700">Detected: {cropText}</span>
            ) : (
              "Scanning species..."
            )
          )}

          {renderStage(
            3,
            "Disease Classification",
            isCropDone || isDiseaseDone,
            isDiseaseDone,
            isCropDone ? <Loader2 size={22} className="animate-spin text-farmer-600" /> : null,
            isDiseaseDone ? (
              <span className="font-semibold text-farmer-700">Identified: {diseaseText}</span>
            ) : isCropDone ? (
              <span className="inline-flex items-center gap-2 text-muted">
                <span className="h-2 w-24 animate-pulse rounded-full bg-line" />
                Analyzing pathology...
              </span>
            ) : (
              "Waiting for crop identification..."
            )
          )}

          {renderStage(
            4,
            "Pest Detection",
            isDiseaseDone || isPestDone,
            isPestDone,
            isDiseaseDone ? <Loader2 size={22} className="animate-spin text-farmer-600" /> : null,
            isPestDone ? (
              <span className="font-semibold text-farmer-700">Result: {pestText || "No Pests Detected"}</span>
            ) : isDiseaseDone ? (
              <span className="inline-flex items-center gap-2 text-muted">
                <span className="h-2 w-24 animate-pulse rounded-full bg-line" />
                Scanning for insects...
              </span>
            ) : (
              "Waiting for disease classification..."
            )
          )}

          {renderStage(
            5,
            "Advisory Generation",
            isPestDone || isAdvisoryDone,
            isAdvisoryDone,
            isPestDone ? <Sparkles size={22} className="animate-pulse text-expert-600" /> : null,
            isAdvisoryDone ? (
              <span className="font-semibold text-farmer-700">Advisory Ready.</span>
            ) : isPestDone ? (
              <span className="inline-flex items-center gap-2 text-expert-700">
                <Sparkles size={18} className="animate-pulse" />
                Synthesizing expert recommendations...
              </span>
            ) : (
              "Waiting for pest detection..."
            )
          )}
        </div>
      </Card>
    </div>
  );
}
