# Preuves d'audit

Le contrat immuable se trouve dans `config/audit_contract.json`.

Lors du déploiement sur Shadow, copier sur la branche de fonctionnalité les
preuves récupérées sous `docs/audit/evidence/`, sans inclure le ZIP lourd dans
Git. Le rapport Markdown, l'inventaire CSV et l'index SHA256 doivent être
versionnés. La CI vérifie le contrat et le registre ; l'importeur vérifie les
artefacts binaires externes avant toute modification.

