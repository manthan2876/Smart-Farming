import { useState } from "react";
import { Check, MessageSquare, ThumbsDown, ThumbsUp } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { submitFeedback } from "../api/predictions";
import { useAuth } from "../context/AuthContext";

export function FeedbackPanel({ predictionId }: { predictionId?: number }) {
  const { token } = useAuth();
  const [choice, setChoice] = useState<boolean | null>(null);
  const [reason, setReason] = useState("Disease");
  const [note, setNote] = useState("");
  const mutation = useMutation({
    mutationFn: () =>
      submitFeedback(predictionId!, choice === true, note, token!),
    onSuccess: () => setChoice(true),
  });
  if (!predictionId || !token) return null;
  return (
    <section className="feedback-panel">
      <div>
        <p className="eyebrow">Close the loop</p>
        <h3>Was this diagnosis helpful?</h3>
      </div>
      {mutation.isSuccess ? (
        <span className="feedback-thanks">
          <Check size={16} /> Thank you. Your feedback helps improve future
          readings.
        </span>
      ) : (
        <>
          <div className="feedback-actions">
            <button
              className={choice === true ? "feedback-selected yes" : ""}
              onClick={() => {
                setChoice(true);
                mutation.mutate();
              }}
            >
              <ThumbsUp size={16} /> Yes, helpful
            </button>
            <button
              className={choice === false ? "feedback-selected no" : ""}
              onClick={() => setChoice(false)}
            >
              <ThumbsDown size={16} /> Needs correction
            </button>
          </div>
          {choice === false && (
            <div className="feedback-form">
              <label>
                What was incorrect?
                <select
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                >
                  <option>Crop</option>
                  <option>Disease</option>
                  <option>Severity</option>
                  <option>Recommendation</option>
                  <option>Other</option>
                </select>
              </label>
              <label>
                Additional note
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Tell us what you observed…"
                />
              </label>
              <button
                className="primary"
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending}
              >
                <MessageSquare size={15} /> Submit feedback
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
