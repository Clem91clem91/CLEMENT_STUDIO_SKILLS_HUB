# Architecture P0-01

## Position dans CLEMENT STUDIO

```text
Mega / Drive (archive READ-ONLY)
            |
            | audit + import explicite
            v
CLEMENT_STUDIO_SKILLS_HUB
  - skills normalisés
  - manifests stricts
  - registry JSON
  - validation / CI
            |
            | lecture READ-ONLY
            v
CLEMENT Skills MCP (P0-02)
            |
            v
CLEMENT Dynamic Orchestrator (P0-04)
```

P0-01 est un **Hub GitHub** : il possède un registre, un cycle de versions,
des tests et des releases. L'importeur et les validateurs sont des services
internes du Hub. Ils ne sont ni des agents ni des MCP.

## Pipeline déterministe

1. Charger le contrat d'audit immuable.
2. Vérifier les hashes du rapport, de l'index de preuves et du bundle.
3. Recalculer les sept métriques depuis `skills_inventory.csv`.
4. Reproduire l'empreinte globale du snapshot.
5. Refuser tout chemin sortant de la racine Mega autorisée.
6. Vérifier chaque `SKILL.md` et `manifest.json` sur disque.
7. Regrouper les copies par SHA256.
8. Choisir la copie canonique selon un ordre stable.
9. Générer IDs, catégories, manifests et relations.
10. Signaler les références non résolues et cycles sans activer les skills.
11. Relire toutes les sources pour fermer la fenêtre TOCTOU.
12. Générer le payload dans un staging situé sur le même volume.
13. Valider le staging, créer et vérifier le backup.
14. Basculer `skills/` et le registre, puis valider à nouveau.
15. Restaurer automatiquement l'état antérieur si la validation échoue.

## Identité stable

Un ID suit la forme :

```text
clement.<slug-normalisé>.<12-premiers-caractères-du-sha256>
```

Un import exécuté deux fois sur le même snapshot produit exactement les mêmes
fichiers. `generated_at` reste volontairement à `null`; l'heure d'exécution
appartient aux preuves de déploiement, pas au contenu versionné.

## Limites de confiance

- Le contenu importé est non exécuté pendant P0-01.
- Le statut initial n'est jamais `ACTIVE`.
- Les manifests d'origine sont des données non fiables ; seules les propriétés
  explicitement normalisées sont conservées.
- Un skill avec dépendance inconnue devient `NEEDS_REVIEW`.
- Un cycle ou une contradiction devient `CONFLICT`.
- Un skill sans manifest valide devient `INCOMPLETE`.

