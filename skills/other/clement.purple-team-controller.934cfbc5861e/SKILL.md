---
name: purple-team-controller
description: "Orchestre le cycle Red Team–Blue Team sur les 904 Skills : cadrage et autorisation, sélection de trois à sept spécialistes, attaque adversariale, réponse défensive, débat fondé sur les preuves, retest, statut final et journal du risque résiduel."
---

# Purple Team Controller

## Mission

Orchestrer un affrontement utile entre :

- une Red Team sans complaisance ;
- une Blue Team radicalement honnête ;
- les Skills spécialisés de la bibliothèque ;
- un responsable humain pour les décisions conséquentes.

Le contrôleur ne cherche pas un compromis artificiel. Il cherche une conclusion **mieux prouvée**.

## Activation

Utiliser cette Skill comme point d'entrée par défaut pour tout audit Red/Blue complet.

## Cycle obligatoire

1. **Cadrage** : objectif, système, décision, propriétaire, autorisation, environnement, exclusions.
2. **Classification du risque** : standard, supervisé ou contrôlé.
3. **Sélection des Skills** : trois à sept par passe, rôles non redondants.
4. **Passe Red Team** : constats, preuves, scénarios et critères de fermeture.
5. **Passe Blue Team** : vérification, cause racine, contrôles, preuves et plan de traitement.
6. **Confrontation** : tableau des accords, désaccords et preuves manquantes.
7. **Retest Red Team** : test des critères de fermeture.
8. **Décision Blue Team** : statut réel et niveau de preuve.
9. **Arbitrage** : risque résiduel, acceptation, escalade ou travaux supplémentaires.
10. **Journal final** : décisions, propriétaires, échéances, inconnues et prochaine revue.

## Routage des 900 Skills

Lire `../../database/skill-routing-index.json` ou exécuter :

```bash
python scripts/select_team_skills.py --query "<mission>" --team red --limit 5
python scripts/select_team_skills.py --query "<mission>" --team blue --limit 5
```

Règles :

- tous les Skills restent accessibles aux deux équipes ;
- l'alignement `RED_PRIMARY`, `BLUE_PRIMARY` ou `SHARED` est une priorité, pas une interdiction ;
- sélectionner des capacités complémentaires ;
- éviter deux personnalités ou deux professions redondantes sans justification ;
- inclure les Skills à risque moyen/élevé uniquement avec validation humaine visible ;
- ne jamais charger la bibliothèque entière dans un seul contexte.

## Gestion des demandes sensibles

Le contrôleur autorise l'analyse détaillée des risques et des mécanismes, mais transforme les éléments directement exploitables contre une vraie cible en :

- simulation ;
- environnement de laboratoire ;
- exemple synthétique ;
- indicateurs de détection ;
- plan de correction ;
- test de validation sûr.

Le rapport indique les détails neutralisés, afin de rester transparent sans créer un mode d'emploi nuisible.

## Arbitrage des désaccords

Pour chaque désaccord :

1. conserver les deux positions ;
2. identifier la proposition vérifiable ;
3. demander la preuve qui réduirait le plus l'incertitude ;
4. exécuter ou spécifier le test minimal ;
5. mettre à jour la confiance ;
6. ne clore qu'avec critères de fermeture satisfaits ou acceptation explicite du risque.

## Sortie obligatoire

1. **Résumé exécutif**.
2. **Périmètre, autorité et limites**.
3. **Skills sélectionnés et justification**.
4. **Constats Red Team**.
5. **Réponses Blue Team**.
6. **Matrice accords/désaccords**.
7. **Résultats du retest**.
8. **Statut final par constat**.
9. **Risque résiduel**.
10. **Décisions humaines requises**.
11. **Plan d'action priorisé**.
12. **Journal de preuves et d'hypothèses**.

## Condition de fin

Une mission est terminée uniquement lorsque chaque constat possède :

- un statut ;
- une preuve ou une preuve manquante explicitée ;
- un propriétaire ;
- un critère de fermeture ;
- une décision sur le risque résiduel.
