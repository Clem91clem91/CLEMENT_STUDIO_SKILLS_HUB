# Politique des statuts

| Statut | Sens | Exposable par P0-02 |
|---|---|---:|
| `ACTIVE` | Revu, certifié et autorisé | Oui |
| `CANDIDATE` | Import valide, revue fonctionnelle nécessaire | Oui, comme candidat |
| `NEEDS_REVIEW` | Référence ou métadonnée à résoudre | Oui, avec avertissement |
| `DEPRECATED` | Remplacé, conservé pour compatibilité | Non par défaut |
| `ARCHIVED` | Historique uniquement | Non |
| `CONFLICT` | Cycle ou contradiction détecté | Non |
| `INCOMPLETE` | Pièce obligatoire manquante | Non |

L'import P0-01 ne produit jamais `ACTIVE`. Le passage à `ACTIVE` nécessite une
revue versionnée, des tests propres au skill et une PR approuvée.

Les dépendances résolues sont enregistrées avec l'ID canonique. Les références
inconnues restent dans `unresolved_dependencies` ou `unresolved_conflicts`, ce
qui interdit le statut `ACTIVE` et empêche une résolution silencieuse.

