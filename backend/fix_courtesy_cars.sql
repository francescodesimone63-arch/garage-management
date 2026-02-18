-- Metti a true SOLO i veicoli di Tiber Car
UPDATE vehicles SET courtesy_car = 1 WHERE customer_id = 6;

-- Metti a false tutti gli altri
UPDATE vehicles SET courtesy_car = 0 WHERE customer_id != 6;

-- Verifica il risultato
.print "📊 RIEPILOGO AGGIORNAMENTO:"
SELECT 
  'Auto CORTESIA (Tiber Car)' as categoria,
  COUNT(*) as numero
FROM vehicles 
WHERE courtesy_car = 1

UNION ALL

SELECT 
  'Auto NORMALI (Non Tiber Car)' as categoria,
  COUNT(*) as numero
FROM vehicles 
WHERE courtesy_car = 0;

.print ""
.print "📋 ESEMPI AUTO DI CORTESIA (Tiber Car):"
SELECT v.id, v.targa, v.marca, v.modello, c.ragione_sociale FROM vehicles v JOIN customers c ON v.customer_id = c.id WHERE v.courtesy_car = 1 LIMIT 5;

.print ""
.print "📋 ESEMPI AUTO NORMALI:"
SELECT v.id, v.targa, v.marca, v.modello, c.ragione_sociale FROM vehicles v JOIN customers c ON v.customer_id = c.id WHERE v.courtesy_car = 0 LIMIT 5;
