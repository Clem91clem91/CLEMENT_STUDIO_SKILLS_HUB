# CLEMENT STUDIO SKILLS HUB

Source de vérité privée, versionnée, déterministe et testable des skills de
CLEMENT STUDIO.

Le Hub ne lit jamais les copies Mega à l'exécution. Mega reste la source
originale READ-ONLY et n'est utilisée que pendant un import explicitement
déclenché. Le registre et les copies normalisées produits par cet import
deviennent ensuite la source active de P0-02 (CLEMENT Skills MCP).

## Contrat d'audit certifié

| Métrique | Valeur |
|---|---:|
| `TOTAL_SKILL_FILES` | 1 805 |
| `UNIQUE_BY_SHA256` | 905 |
| `EXACT_DUPLICATES` | 900 |
| `UNIQUE_SKILL_NAMES` | 905 |
| `NAME_CONFLICTS` | 0 |
| `INCOMPLETE_SKILLS` | 5 |
| `INVALID_MANIFESTS` | 0 |

Empreinte du snapshot source :
`4206D8DC3405EB5E5F17E73911F7940D197DB3D657405F3AD88B1509B74541D5`.

Le contrat complet est dans [`config/audit_contract.json`](config/audit_contract.json).
L'import s'arrête si l'une de ces preuves ne correspond pas.

## Garanties

- import déterministe par SHA256 ;
- déduplication de 1 805 fichiers vers 905 entrées ;
- aucune écriture dans la bibliothèque source ;
- contrôle des chemins pour empêcher toute sortie de la racine autorisée ;
- double vérification des hashes source avant et après l'import ;
- génération transactionnelle avec backup et rollback automatique ;
- aucun skill activé automatiquement : statut initial `CANDIDATE`,
  `NEEDS_REVIEW`, `CONFLICT` ou `INCOMPLETE` ;
- schémas JSON stricts, validation des dépendances et conflits ;
- registre stable et reproductible, sans horodatage variable ;
- CI Windows et Linux avec Python 3.11 et 3.13.

## Commandes locales

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe scripts\validate_repository.py --root .
```

Le workflow d'installation ne télécharge aucune dépendance. Le paquet peut
néanmoins être installé avec `pip install -e .` dans un environnement de
développement disposant de `setuptools>=68`.

L'import réel et son rollback sont décrits dans
[`docs/IMPORT_RUNBOOK.md`](docs/IMPORT_RUNBOOK.md). L'import est en mode
simulation par défaut et exige `--apply` ainsi qu'un dossier de backup pour
modifier le Hub.

## Branches

- `main` : releases certifiées ;
- `develop` : intégration validée ;
- `feat/p0-skills-hub` : développement P0-01.
