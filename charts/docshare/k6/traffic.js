// Trafic constant d'une équipe DocShare.
//
// Chaque itération suit un document de bout en bout : upload, consultation de
// son statut jusqu'à « done », puis recherche de son jeton unique. On ne cherche
// donc que des documents traités : un résultat vide signale un défaut de
// qualité (stale_index), jamais un simple retard (worker_slow).
//
// Les métriques de k6 ne sont exportées nulle part : les SLI se mesurent côté serveur.
import http from 'k6/http';
import { sleep } from 'k6';

const API = __ENV.API_URL || 'http://api';
const UPLOAD_RATE = Number(__ENV.UPLOAD_RATE || 1);          // uploads par seconde
const SEARCHES_PER_DOC = Number(__ENV.SEARCHES_PER_DOC || 2); // recherches par document traité
const FOLLOW_TIMEOUT = Number(__ENV.FOLLOW_TIMEOUT || 60);    // secondes d'attente du statut « done »
const POLL_INTERVAL = 2;                                      // secondes entre deux consultations

export const options = {
  scenarios: {
    documents: {
      // Débit constant même quand l'API ralentit : sinon upload_latency ferait
      // baisser le trafic et fausserait les ratios.
      executor: 'constant-arrival-rate',
      rate: UPLOAD_RATE,
      timeUnit: '1s',
      duration: __ENV.DURATION || '3h',
      // Sous worker_slow, chaque itération dure FOLLOW_TIMEOUT secondes. Tous les VU
      // sont créés d'avance : k6 abandonne des itérations le temps d'en créer de
      // nouveaux, ce qui ferait chuter le débit d'upload au début de la panne.
      preAllocatedVUs: Math.ceil(UPLOAD_RATE * (FOLLOW_TIMEOUT + 20)),
      maxVUs: Math.ceil(UPLOAD_RATE * (FOLLOW_TIMEOUT + 20)),
    },
  },
  summaryTrendStats: ['avg', 'p(95)'],
};

const CORPUS = [
  'facture électricité trimestre',
  'contrat de location appartement',
  'relevé bancaire mensuel',
  'attestation assurance habitation',
  'bulletin de salaire',
  'avis d imposition',
  'devis travaux cuisine',
  'ordonnance médicale',
];

const JSON_HEADERS = { headers: { 'Content-Type': 'application/json' } };

function token() {
  return 'doc-' + Math.random().toString(36).slice(2, 10).padEnd(8, '0');
}

export default function () {
  const tok = token();
  const text = CORPUS[Math.floor(Math.random() * CORPUS.length)];
  const res = http.post(`${API}/documents`, JSON.stringify({ title: text, content: `${text} ${tok}` }), JSON_HEADERS);
  if (res.status !== 202) {
    return; // upload en erreur (upload_error_rate) : rien à suivre
  }
  const id = res.json('id');

  for (let waited = 0; waited < FOLLOW_TIMEOUT; waited += POLL_INTERVAL) {
    sleep(POLL_INTERVAL);
    const doc = http.get(`${API}/documents/${id}`, { tags: { name: `${API}/documents/{id}` } });
    if (doc.status === 200 && doc.json('status') === 'done') {
      for (let i = 0; i < SEARCHES_PER_DOC; i++) {
        http.get(`${API}/search?q=${tok}`, { tags: { name: `${API}/search` } });
      }
      return;
    }
  }
  // Pas « done » à temps (worker_slow) : on ne cherche pas, la qualité reste intacte.
}
