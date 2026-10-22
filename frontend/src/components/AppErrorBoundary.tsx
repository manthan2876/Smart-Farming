import { Component, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  fallback: ReactNode;
};

type State = {
  hasError: boolean;
};

export default class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: { componentStack?: string | null }) {
    console.error("Unhandled frontend rendering error", error, info.componentStack);
    // Phase 5 telemetry integration: forward error to Sentry if initialized
    if (typeof window !== "undefined" && (window as unknown as { Sentry?: { captureException: (err: unknown, ctx: unknown) => void } }).Sentry?.captureException) {
      (window as unknown as { Sentry: { captureException: (err: unknown, ctx: unknown) => void } }).Sentry.captureException(error, {
        extra: { componentStack: info.componentStack },
      });
    }
  }

  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}
