import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

/**
 * OAuthCallback - Pagina intermedia che gestisce il ritorno da Google OAuth
 * 
 * Il backend reindirizza direttamente qui con il return_url già incluso.
 * Il backend ha salvato il return_url nello state token durante authorize.
 * 
 * Flow:
 * 1. Frontend: Chiama /authorize?return_url=ENCODED_URL
 * 2. Backend: Salva return_url nello state token nel DB
 * 3. Google: Autentica e reindirizza a /callback
 * 4. Backend: Legge return_url dal DB e reindirizza il browser
 * 5. Browser: Arriva qui a /oauth/callback?calendar_auth=success
 */
export function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    // Il backend ha già reindirizzato il browser qui
    // Leggi il parametro calendar_auth=success
    const authSuccess = searchParams.get('calendar_auth') === 'success';
    
    if (authSuccess) {
      // Auto-redirect dopo 1 secondo per mostrare il messaggio di completamento
      setTimeout(() => {
        // Fallback: vai a work-orders
        // (In realtà il backend avrà già reindirizzato il browser al return_url)
        navigate('/work-orders?calendar_auth=success', { replace: true });
      }, 1000);
    }
  }, [searchParams, navigate]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontSize: '18px',
      color: '#666'
    }}>
      ⏳ Completamento autenticazione...
    </div>
  );
}
