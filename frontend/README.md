This is the Front End branch

tree -I "node_modules|dist|.git|.vscode|e2e|*.log" -L 3

# Architecture src
``
src/
├── App.vue              ← squelette global (layout principal)
├── assets/              ← CSS, images, icônes, etc.
│   └── css/
│       ├── main.css
│       ├── calendar.css
│       └── fontawesome-all.min.css
├── components/          ← petits composants réutilisables
│   └── icons/
│       ├── IconCommunity.vue
│       ├── IconSupport.vue
│       └── ...
├── main.ts              ← point d’entrée (crée l’app + router)
├── router/
│   └── index.ts         ← gère les routes (URL ↔ vue)
├── stores/              ← état global (Pinia)
│   └── counter.ts
└── views/               ← les pages principales (liées au router)
    ├── Home.vue
    ├── Calendar.vue
    └── Contact.vue
``
