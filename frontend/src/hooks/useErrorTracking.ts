/**
 * Hook React per il tracking degli errori
 * Semplifica l'uso dell'error tracker all'interno dei componenti
 */

import { useEffect, useCallback, useState } from "react";
import { errorTracker, ErrorLog } from "@/utils/errorTracker";

export const useErrorTracking = () => {
  const [errors, setErrors] = useState<ErrorLog[]>([]);

  useEffect(() => {
    // Subscribe ai cambiamenti degli errori
    errorTracker.subscribe(setErrors);

    // Cleanup
    return () => {
      errorTracker.unsubscribe(setErrors);
    };
  }, []);

  const trackAPIError = useCallback(
    (
      endpoint: string,
      method: string,
      status: number | undefined,
      error: unknown,
      context?: Record<string, unknown>
    ) => {
      errorTracker.trackAPIError(endpoint, method, status, error, context);
    },
    []
  );

  const trackValidationError = useCallback(
    (field: string, error: string, context?: Record<string, unknown>) => {
      errorTracker.trackValidationError(field, error, context);
    },
    []
  );

  const trackRuntimeError = useCallback(
    (message: string, details?: Record<string, unknown>) => {
      errorTracker.trackRuntimeError(message, details);
    },
    []
  );

  const getRecentErrors = useCallback(
    (minutes: number = 5) => errorTracker.getRecentErrors(minutes),
    []
  );

  const getAllErrors = useCallback(() => errorTracker.getLogs(), []);

  const downloadLogs = useCallback(
    () => errorTracker.downloadLogs(),
    []
  );

  const clearErrors = useCallback(() => {
    errorTracker.clearLogs();
    setErrors([]);
  }, []);

  return {
    errors,
    trackAPIError,
    trackValidationError,
    trackRuntimeError,
    getRecentErrors,
    getAllErrors,
    downloadLogs,
    clearErrors,
  };
};
