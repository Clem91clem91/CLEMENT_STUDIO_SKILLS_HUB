# Runbook d'import certifié

## Préconditions

- Windows 11 et PowerShell ;
- Python 3.11 ou plus récent ;
- checkout propre de `feat/p0-skills-hub` ;
- bibliothèque source inchangée ;
- audit récupéré du 20/08/2026 ;
- aucun merge ou tag avant CI verte.

## Entrées attendues

| Entrée | Preuve attendue |
|---|---|
| `SKILLS_LIBRARY_AUDIT_RECOVERED_*.md` | SHA256 `23726C...58E49` |
| `EVIDENCE_SHA256_RECOVERED_*.txt` | SHA256 `588EE8...75084` |
| bundle ZIP récupéré | SHA256 `17ABD5...83F25` |
| `skills_inventory.csv` | snapshot source `4206D8...541D5` |

Les valeurs complètes sont dans `config/audit_contract.json`.

## Simulation obligatoire

La commande suivante ne modifie ni Mega ni le Hub :

```powershell
& .\.venv\Scripts\python.exe scripts\import_skills.py `
  --source-root "C:\Users\Shadow\Documents\CLEMENT_STUDIO\09_Drive\Mega\skill" `
  --inventory "$AuditDirectory\skills_inventory.csv" `
  --contract ".\config\audit_contract.json" `
  --audit-report "$AuditDirectory\SKILLS_LIBRARY_AUDIT_RECOVERED_20260820_092934_132.md" `
  --evidence-index "$AuditDirectory\EVIDENCE_SHA256_RECOVERED_20260820_092934_132.txt" `
  --audit-bundle "$AuditBundle" `
  --repository-root $PWD
```

Résultat minimal :

```text
NORMALIZED_ENTRIES=905
MODE=DRY_RUN
FILE_CHANGED=NO
RESULT=PASS
```

## Application transactionnelle

Ajouter seulement après une simulation `PASS` :

```powershell
--apply --backup-root "$env:USERPROFILE\Downloads\CLEMENT_P0\P0-01_BACKUPS"
```

Résultat minimal :

```text
APPLY_RESULT=APPLIED
SKILLS_HUB_TESTS=PASS
RESULT=PASS
```

Le chemin `BACKUP_PATH=` est la preuve locale de rollback. Une seconde
exécution identique doit rendre `APPLY_RESULT=NO_CHANGE`.

## Rollback

Le rollback Git reste la méthode principale après commit :

```powershell
git revert <COMMIT_SHA_IMPORT>
```

Avant commit, restaurer `skills/` et `registry/skills_registry.json` depuis le
`BACKUP_PATH` imprimé par l'importeur. Comparer impérativement les empreintes du
fichier `BACKUP_RECEIPT.json` avant restauration. Ne jamais utiliser ce backup
sur un autre checkout : le champ `repository_root` doit correspondre.

## Gate de certification

- registre : 905 entrées ;
- aucune entrée `ACTIVE` sans revue ;
- tests locaux : PASS ;
- arbre Git propre après commit ;
- branche poussée ;
- PR vers `develop` ;
- CI verte ;
- merge interdit si une preuve manque.

