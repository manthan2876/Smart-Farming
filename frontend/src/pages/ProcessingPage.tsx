import { useState, useEffect } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getPrediction } from "../api/predictions";
import { motion } from "motion/react";
import { Loader2, Check, Wheat, Leaf, TreeDeciduous, Sprout, Clover, Bug, Activity, Sparkles, Wand2 } from "lucide-react";
import { Button, Card } from "../components/ui";

export default function ProcessingPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const predictionId = Number(id);
  const { token } = useAuth();

  const queryClient = useQueryClient();
  const { data: prediction, error } = useQuery({
    queryKey: ["prediction", predictionId],
    queryFn: () => getPrediction(String(predictionId), token || ''),
    enabled: !isNaN(predictionId),
    refetchInterval: false, // Replaced by WebSocket
  });

  // WebSocket Integration
  useEffect(() => {
    if (isNaN(predictionId)) return;
    
    // Resolve host dynamically, replacing http with ws
    const host = window.location.hostname || "localhost";
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${host}:8000/ws/predictions/${predictionId}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const stage = data.stage;
        
        // Update React Query cache optimistically based on WS stage
        queryClient.setQueryData(["prediction", predictionId], (oldData: any) => {
          if (!oldData) return oldData;
          const newData = { ...oldData };
          if (!newData.status) newData.status = {};
          
          if (stage === "crop_identification") newData.status.crop_identification = "completed";
          if (stage === "disease_classification") newData.status.disease_classification = "completed";
          if (stage === "pest_detection") newData.status.pest_detection = "completed";
          if (stage === "severity_calculation") newData.status.severity_calculation = "completed";
          if (stage === "llm_advisory") newData.status.recommendation = "completed";
          
          if (stage === "completed") {
             newData.status.pipeline = "completed";
             // Trigger a final fetch to get actual labels/results from DB
             queryClient.invalidateQueries({ queryKey: ["prediction", predictionId] });
          }
          return newData;
        });
      } catch (e) {
        console.error("WS parse error", e);
      }
    };
    
    let isClosing = false;
    ws.onopen = () => {
      if (isClosing) {
        ws.close();
      }
    };
    
    return () => {
      isClosing = true;
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      // If readyState is CONNECTING (0), we don't call close() immediately to avoid the 
      // "WebSocket is closed before the connection is established" Chrome console error.
      // Instead, the onopen handler will catch the isClosing flag and close it gracefully.
    };
  }, [predictionId, queryClient]);

  const [activeCropIdx, setActiveCropIdx] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActiveCropIdx(prev => (prev + 1) % 5), 400);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (prediction) {
      const latest = prediction.follow_up || prediction;
      const isProcessing = (latest.status as any)?.pipeline === "processing" || (latest.status as any)?.preprocessing === "processing";
      
      // If it's no longer processing, wait 1.5s for the user to see the final "Advisory Ready" state, then navigate

      if (!isProcessing) {
        navigate(`/predictions/${predictionId}`, { replace: true });
      }
    }
  }, [prediction, navigate, predictionId]);


  const targetPred = prediction?.follow_up || prediction;
  const statusDict: any = targetPred?.status || {};
  
  const isPreprocDone = statusDict.preprocessing === "completed";
  const isCropDone = statusDict.crop_identification === "completed";
  const isDiseaseDone = statusDict.disease_classification === "completed";
  const isPestDone = statusDict.pest_detection === "completed";
  const isAdvisoryDone = statusDict.recommendation === "completed";

  const cropLabel = targetPred?.crop?.label;
  const diseaseLabel = targetPred?.disease?.label;
  const pestLabel = targetPred?.pests && targetPred.pests.length > 0 ? targetPred.pests[0].label : (isPestDone ? "No Pests" : null);

  const CROP_ICONS = [<Wheat size={20}/>, <Leaf size={20}/>, <TreeDeciduous size={20}/>, <Sprout size={20}/>, <Clover size={20}/>];

  const renderStage = (stageNumber: number, title: string, isUnlocked: boolean, isComplete: boolean, icon: React.ReactNode, detail: React.ReactNode) => (
    <div className={`flex items-start gap-4 transition-opacity sm:gap-6 ${isUnlocked ? "opacity-100" : "opacity-40"}`}>
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${isComplete ? "bg-farmer-600 text-white" : isUnlocked ? "bg-expert-100 text-expert-700" : "bg-canvas text-muted"}`}>
        {isComplete ? <Check size={22} /> : icon || stageNumber}
      </div>
      <div className="min-w-0 pt-1">
        <h4 className="font-semibold text-ink">{stageNumber}. {title}</h4>
        <div className="mt-1 text-sm text-muted">{detail}</div>
      </div>
    </div>
  );

  if (error) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center text-center text-danger">
        <h2 className="font-display text-2xl">Error Loading Status</h2>
        <p className="mt-2 text-sm text-muted">Something went wrong. Please check your network connection.</p>
        <Button variant="secondary" className="mt-5" onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
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
        </div>
        <div className="mt-10 space-y-8">
          {renderStage(1, "Image Preprocessing", true, true, null, "Verified leaf presence and clarity.")}
          {renderStage(2, "Crop Identification", true, isCropDone, isCropDone ? null : CROP_ICONS[activeCropIdx], isCropDone ? <span className="font-semibold text-farmer-700">Detected: {cropLabel}</span> : "Scanning species...")}
          {renderStage(3, "Disease Classification", isCropDone, isDiseaseDone, isCropDone ? <Loader2 size={22} className="animate-spin" /> : null, isDiseaseDone ? <span className="font-semibold text-admin-500">Identified: {diseaseLabel || "Unknown"}</span> : isCropDone ? <span className="inline-flex items-center gap-2"><span className="h-2 w-24 animate-pulse rounded-full bg-line" />Analyzing pathology...</span> : "Waiting for crop identification...")}
          {renderStage(4, "Pest Detection", isDiseaseDone, isPestDone, isDiseaseDone ? <Loader2 size={22} className="animate-spin" /> : null, isPestDone ? <span className="font-semibold text-admin-500">Result: {pestLabel}</span> : isDiseaseDone ? <span className="inline-flex items-center gap-2"><span className="h-2 w-24 animate-pulse rounded-full bg-line" />Scanning for insects...</span> : "Waiting for disease classification...")}
          {renderStage(5, "Advisory Generation", isPestDone, isAdvisoryDone, isPestDone ? <Sparkles size={22} className="animate-pulse" /> : null, isAdvisoryDone ? <span className="font-semibold text-farmer-700">Advisory Ready.</span> : isPestDone ? <span className="inline-flex items-center gap-2 text-expert-700"><Sparkles size={18} className="animate-pulse" />Synthesizing expert recommendations...</span> : "Waiting for pest detection..." )}
        </div>
      </Card>
    </div>
  );
}
