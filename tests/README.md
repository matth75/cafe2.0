# Test de charge avec Locust

Ce document explique comment lancer et utiliser **Locust** pour effectuer des tests de charge sur l’API backend.

---

## Prérequis

- Python ≥ 3.10
- Environnement virtuel activé
- Le serveur backend doit être fonctionnel
- Locust installé :
```bash
pip install locus
```

## Structure minimale attendue
```bash
À la racine du projet :
.
├── locustfile.py
├── backend/
├── tests/
└── README.md
```

## Démarrer le serveur API
Dans un premier terminal :
```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8000
```

Vérifier que l'API réponde : 
```bash
curl http://127.0.0.1:8000/status/healthcheck
```
## Lancer Locust (mode interface web)
Dans un second terminal :
```bash
locust -f locustfile.py --host http://127.0.0.1:8000
```
Locust démarre une interface web :
```bash
http://localhost:8089
```
## Paramétrer le test
Dans l’interface web :
- Number of users : nombre de clients simultanés (ex: 10, 50, 100)Number of users : nombre de clients simultanés (ex: 10, 50, 100)
- Spawn rate : nombre d’utilisateurs ajoutés par seconde (ex: 2, 5)
- Cliquer sur Start

## Interprétation des résultats
- Requests/s (RPS) : débit du serveur
- Median / p95 / p99 : latence sous charge
- Failures : erreurs HTTP ou timeouts

Bon comportement attendu :
- Peu ou pas d’erreurs
- Latence stable quand la charge augmente
- Débit proportionnel au nombre d’utilisateurs