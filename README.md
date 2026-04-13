# Widget éolien en mer — Production électrique offshore

Mise à jour automatique toutes les heures via GitHub Actions → RTE API.

## Setup (5 minutes)

### 1. Créer le repo GitHub
Créer un repo **public** (nécessaire pour accéder à `raw.githubusercontent.com` sans token).

### 2. Ajouter les secrets RTE
Dans le repo → **Settings → Secrets and variables → Actions → New repository secret** :

| Nom               | Valeur                               |
|-------------------|--------------------------------------|
| `RTE_CLIENT_ID`   | `66c46445-121c-4e9a-98c3-89488f393a19` |
| `RTE_CLIENT_SECRET` | `1293d144-c33c-42b7-b66f-2fe43d0c55fa` |

### 3. Pousser les fichiers
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/TON_USER/TON_REPO.git
git push -u origin main
```

### 4. Premier run manuel
Dans le repo → **Actions → Fetch éolien offshore RTE → Run workflow**  
→ Vérifier que `data_eolien.json` apparaît dans le repo.

### 5. URL du JSON pour le widget
```
https://raw.githubusercontent.com/TON_USER/TON_REPO/main/data_eolien.json
```
→ Remplacer dans `eolien_mer_widget.html` la constante `RTE_JSON_URL`.

## Structure de data_eolien.json
```json
{
  "generated_at": "2026-04-13T12:00:00+02:00",
  "source": "RTE Actual Generation API v1.1",
  "parcs": [
    {
      "nom": "SAINT-NAZAIRE",
      "eic_code": "...",
      "serie": [{"t": "2026-04-13T10:00:00+02:00", "mw": 450}]
    }
  ]
}
```

## Cron
Le workflow tourne automatiquement toutes les heures (`:00` UTC).  
GitHub peut accuser jusqu'à ~15 min de retard en cas de forte charge.
