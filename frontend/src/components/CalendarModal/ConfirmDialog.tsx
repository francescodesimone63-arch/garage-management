import { format } from 'date-fns';
import { it } from 'date-fns/locale';
import './ConfirmDialog.css';

interface ConfirmDialogProps {
  start: Date;
  end: Date;
  duration: number;
  loading: boolean;
  onDurationChange: (minutes: number) => void;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  start,
  end,
  duration,
  loading,
  onDurationChange,
  onConfirm,
  onCancel
}: ConfirmDialogProps) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
        <h3>📅 Conferma Prenotazione</h3>
        
        <div className="confirm-field">
          <label>Inizio:</label>
          <div className="confirm-value">
            {format(start, 'dd MMM yyyy, HH:mm', { locale: it })}
          </div>
        </div>

        <div className="confirm-field">
          <label>Durata:</label>
          <select 
            value={duration} 
            onChange={(e) => onDurationChange(Number(e.target.value))}
            disabled={loading}
            className="duration-select"
          >
            <option value={30}>30 minuti</option>
            <option value={60}>1 ora</option>
            <option value={90}>1.5 ore</option>
            <option value={120}>2 ore</option>
            <option value={180}>3 ore</option>
            <option value={240}>4 ore</option>
          </select>
        </div>

        <div className="confirm-field">
          <label>Fine:</label>
          <div className="confirm-value">
            {format(end, 'dd MMM yyyy, HH:mm', { locale: it })}
          </div>
        </div>

        <div className="confirm-actions">
          <button 
            className="btn-cancel" 
            onClick={onCancel}
            disabled={loading}
          >
            Annulla
          </button>
          <button 
            className="btn-confirm"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? '⏳ Salvataggio...' : '✓ Conferma Prenotazione'}
          </button>
        </div>
      </div>
    </div>
  );
}
