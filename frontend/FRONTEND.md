# Frontend (Vue 3 + Vite)

Application Vue 3/TypeScript avec Vite, Vuetify et Vue Router. Le code vit dans `frontend/vue-cafe`.

## Prérequis
- Node.js ^20.19.0 ou >=22.12.0, npm
- Accès au repo (pas de dépendances globales nécessaires)

## Installation et démarrage
```bash
cd frontend/vue-cafe
npm install
npm run dev   # http://localhost:5173
```

## Configuration .env
`frontend/vue-cafe/.env.developpment` et `frontend/vue-cafe/.env.production` permettent de configurer les URLs de l’API backend et optionnellement de la source iCalendar.


## TO production
- `npm run build` : build production dans `dist/`
- puis envoyer `dist/` sur le serveur (via scp)
- sur la RPI : 
    - mettre le dist dans /var/www/html
    - remove cafe_old, rename cafe to cafe_old, rename dist to cafe (pour rollback rapide)


## Arborescence principale (`src/`)
```
src/
├── App.vue
├── api/
├── assets/css/
├── components/ (Header, Calendar_compo*, Sidebar, etc.)
├── main.ts
├── router/index.ts
├── stores/counter.ts
├── utils/ (authEvents.ts, utils.ts)
└── views/ (Home, Calendar, Login, Superuser, ...)
```

## Tunnel SSH vers la Pi
```
sudo ssh -L 8080:localhost:8000 tpreso01@cafe.zpq.ens-paris-saclay.fr
```
Permet d’exposer le backend distant en local sur le port 8080.

## Patch @fullcalendar/icalendar (patch-package)
### Pourquoi
Le plugin iCalendar de FullCalendar ne fournit pas d’`id` pour les événements importés ; on ajoute l’`id` basé sur l’UID iCal pour éviter les doublons et permettre la mise à jour correcte des événements.

### Comment
- Le patch est stocké dans `frontend/vue-cafe/patches/@fullcalendar+icalendar+6.1.19.patch` et est appliqué automatiquement après `npm install` via `postinstall`.
- Si le patch casse après une mise à jour de dépendances : modifier `node_modules/@fullcalendar/icalendar/index.js` puis régénérer avec `npx patch-package @fullcalendar/icalendar` depuis `frontend/vue-cafe`. Commiter le fichier `patches/` mis à jour.
