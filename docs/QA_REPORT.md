# Rapport QA P0-01

Date : 20/08/2026

## Audit GitHub READ-ONLY

- dépôt : `Clem91clem91/CLEMENT_STUDIO_SKILLS_HUB` ;
- visibilité : privée ;
- permissions du compte connecté : administration et push ;
- branche par défaut : `main` ;
- branches présentes : `main`, `develop` ;
- commit commun : `df9b589551c64f16d641ac809903f52f5a9cc040` ;
- comparaison `main...develop` : identique, 0 commit d'écart ;
- contenu observé : README minimal identique ;
- PR ouverte ou fermée : aucune ;
- publication effectuée pendant ce développement : aucune.

## Contrat fonctionnel

Le code accepte le contrat réel 1 805 / 905 / 900 / 905 / 0 / 5 / 0 et
refuse toute divergence. Le test d'échelle recrée exactement ce volume avec
1 805 fichiers sources, vérifie les hashes deux fois et construit 905 entrées,
dont 900 `CANDIDATE` et 5 `INCOMPLETE`.

## Commandes exécutées

```text
python -m compileall -q src scripts tests
python scripts/validate_repository.py --root .
python -m unittest discover -s tests -v
```

Résultat :

```text
SKILLS_HUB_TESTS=PASS
Ran 10 tests
OK
```

Test d'installation du paquet exécuté dans un environnement virtuel isolé :

```text
Successfully built clement-studio-skills-hub
Successfully installed clement-studio-skills-hub-0.1.0
SKILLS_HUB_TESTS=PASS
Ran 10 tests
OK
```

## Couverture de QA

- calcul exact des métriques certifiées ;
- détection des conflits de nom ;
- lien cryptographique entre inventaire et index de preuves ;
- déterminisme du plan ;
- préservation de la source ;
- matérialisation et validation du payload ;
- backup, application transactionnelle et idempotence ;
- schémas et statuts ;
- test d'échelle exact ;
- rejet d'un chemin sortant de la racine source.

## Limite explicite

La bibliothèque Windows et le bundle d'audit ne sont pas montés dans
l'environnement de développement. Les 905 contenus réels ne sont donc pas
copiés dans cet arbre local. Leur import reste un gate réel à exécuter sur
Shadow avec `scripts/Install-P0SkillsHub.ps1`, suivi d'un commit, d'une PR et de
la CI. Aucun résultat synthétique ne remplace ce test réel.

