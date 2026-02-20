/**
 * Sistema di error tracking avanzato per React
 * Traccia errori API, validazione e runtime con dettagli completi
 */

interface ErrorLog {
  id: string;
  timestamp: string;
  type: "api" | "validation" | "runtime" | "network";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  details: Record<string, unknown>;
  stackTrace?: string;
  context?: Record<string, unknown>;
}

class ErrorTracker {
  private logs: ErrorLog[] = [];
  private maxLogs = 100;
  private listeners: ((logs: ErrorLog[]) => void)[] = [];
  private sessionId = new Date().getTime().toString();

  constructor() {
    this.setupGlobalErrorHandler();
  }

  private setupGlobalErrorHandler() {
    // Cattura errori globali non gestiti
    window.addEventListener("error", (event) => {
      this.trackRuntimeError(
        event.message,
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          stack: event.error?.stack,
        }
      );
    });

    // Cattura Promise rejections non gestiti
    window.addEventListener("unhandledrejection", (event) => {
      this.trackRuntimeError(
        "Unhandled Promise Rejection",
        {
          reason: event.reason,
          stack: event.reason?.stack,
        }
      );
    });
  }

  private generateId(): string {
    return `${this.sessionId}-${this.logs.length}-${Date.now()}`;
  }

  private addLog(log: ErrorLog) {
    const completeLog = {
      ...log,
      id: this.generateId(),
      timestamp: new Date().toISOString(),
    };

    this.logs.push(completeLog);

    // Mantieni solo gli ultimi N log
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Notifica i listener
    this.notifyListeners();

    // Log in console con colore
    this.logToConsole(completeLog);
  }

  private logToConsole(log: ErrorLog) {
    const color = {
      low: "#FFA500",      // Arancione
      medium: "#FF8C00",   // Arancione scuro
      high: "#FF0000",     // Rosso
      critical: "#8B0000", // Rosso scuro
    }[log.severity];

    const prefix = `%c[${log.type.toUpperCase()}]%c ${log.message}`;
    console.log(
      prefix,
      `color: ${color}; font-weight: bold; font-size: 12px;`,
      `color: ${color}; font-size: 12px;`
    );

    if (Object.keys(log.details).length > 0) {
      console.log("%cDetails:", "font-weight: bold; color: gray;", log.details);
    }

    if (log.stackTrace) {
      console.log("%cStack Trace:", "font-weight: bold; color: gray;", log.stackTrace);
    }
  }

  trackAPIError(
    endpoint: string,
    method: string,
    status: number | undefined,
    error: unknown,
    context?: Record<string, unknown>
  ) {
    let severity: "low" | "medium" | "high" | "critical" = "medium";
    if (status === undefined) severity = "critical"; // Network error
    else if (status >= 500) severity = "high";
    else if (status === 401 || status === 403) severity = "medium";

    this.addLog({
      id: "",
      timestamp: "",
      type: "api",
      severity,
      message: `API Error: ${method} ${endpoint}`,
      details: {
        endpoint,
        method,
        status: status || "Network Error",
        error: error instanceof Error ? error.message : String(error),
        errorType: error instanceof Error ? error.name : typeof error,
      },
      stackTrace: error instanceof Error ? error.stack : undefined,
      context,
    });
  }

  trackValidationError(
    field: string,
    error: string,
    context?: Record<string, unknown>
  ) {
    this.addLog({
      id: "",
      timestamp: "",
      type: "validation",
      severity: "low",
      message: `Validation Error: ${field}`,
      details: {
        field,
        error,
      },
      context,
    });
  }

  trackRuntimeError(
    message: string,
    details: Record<string, unknown> = {}
  ) {
    this.addLog({
      id: "",
      timestamp: "",
      type: "runtime",
      severity: "high",
      message,
      details,
      stackTrace: details.stack as string | undefined,
    });
  }

  trackNetworkError(
    endpoint: string,
    error: unknown,
    context?: Record<string, unknown>
  ) {
    this.addLog({
      id: "",
      timestamp: "",
      type: "network",
      severity: "critical",
      message: `Network Error: ${endpoint}`,
      details: {
        endpoint,
        error: error instanceof Error ? error.message : String(error),
      },
      context,
    });
  }

  getLogs(): ErrorLog[] {
    return [...this.logs];
  }

  getLogsByType(type: string): ErrorLog[] {
    return this.logs.filter((log) => log.type === type);
  }

  getLogsBySeverity(severity: string): ErrorLog[] {
    return this.logs.filter((log) => log.severity === severity);
  }

  getRecentErrors(minutes: number = 5): ErrorLog[] {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    return this.logs.filter((log) => new Date(log.timestamp) > cutoff);
  }

  clearLogs() {
    this.logs = [];
    this.notifyListeners();
  }

  subscribe(listener: (logs: ErrorLog[]) => void) {
    this.listeners.push(listener);
  }

  unsubscribe(listener: (logs: ErrorLog[]) => void) {
    this.listeners = this.listeners.filter((l) => l !== listener);
  }

  private notifyListeners() {
    this.listeners.forEach((listener) => listener([...this.logs]));
  }

  exportLogs(): string {
    return JSON.stringify(
      {
        sessionId: this.sessionId,
        exportedAt: new Date().toISOString(),
        logs: this.logs,
      },
      null,
      2
    );
  }

  downloadLogs() {
    const data = this.exportLogs();
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `error-logs-${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

// Istanza globale singleton
export const errorTracker = new ErrorTracker();

export type { ErrorLog };
export default ErrorTracker;
