# 🎯 Système d'Annotation et Test pour Messages Chinois

## 🚀 Démarrage Rapide

### Installation (une seule fois)
```bash
# Option 1: Script automatique (macOS/Linux)
bash install.sh

# Option 2: Manuel
pip install flask telethon opencc
```

### Lancement
```bash
# Menu interactif (recommandé)
python launcher.py

# Ou directement:
python annotation_app.py    # Port 5000 - Annotation
python model_tester.py      # Port 5001 - Test
python demo_feedback.py     # CLI Interactive
```

---

## 📋 Ce que vous pouvez faire

### 1. Annoter des Messages
```
Entrez un message en chinois
↓
Spécifiez l'action (activate/deactivate)
↓
Spécifiez le type (platform/channel)
↓
Le modèle apprend
```

### 2. Tester le Modèle
```
Entrez un message
↓
Voyez la prédiction et la confiance
↓
Validez ou corrigez
↓
Le modèle s'améliore automatiquement
```

### 3. Suivre les Progrès
```
Consultez les statistiques
↓
Accuracy % augmente avec le feedback
↓
Sauvegarde automatique des résultats
```

---

## 📁 Structure du Projet

```
├── 📝 Annotation
│   ├── data_annotator.py (425 lignes)
│   ├── annotation_app.py (310 lignes)
│   └── templates/
│
├── 🧪 Test & Feedback
│   ├── model_tester.py (360 lignes)
│   ├── demo_feedback.py (interactive CLI)
│   └── templates/
│
├── 🧠 Moteur d'Apprentissage
│   ├── rule_engine.py (~400 lignes)
│   └── integration_with_main.py (280 lignes)
│
├── 📊 Données
│   ├── training_data.json
│   ├── annotated_messages.json
│   ├── test_feedback.json
│   └── sample_messages_zh.json
│
├── 📚 Documentation
│   ├── QUICKSTART.md ⭐
│   ├── README_COMPLETE.md
│   ├── PROJECT_SUMMARY.md
│   └── 5+ guides supplémentaires
│
└── 🛠️ Utilitaires
    ├── launcher.py (menu principal)
    ├── verify_system.py (vérification)
    └── install.sh (installation)
```

---

## 🎯 Exemples

### Messages supportés
```
启用 Wangpai 平台      → Activate platform Wangpai
关闭 ID:156 频道      → Deactivate channel 156
开启 Jincheng 频道    → Activate channel Jincheng
停用 WeChat 平台      → Deactivate platform WeChat
```

### Cycle de Feedback
```
1. Message: "启用 Wangpai 平台"
   ↓
2. Prédiction: action=activate, type=platform, id=Wangpai (85%)
   ↓
3. Verdict: Correct ✅
   ↓
4. Modèle réentraîné: +3% confiance
   ↓
5. Prochaine fois: 88% (amélioration!)
```

---

## 📊 Statistiques Actuelles

- **Lignes de code**: 2500+
- **Modules**: 12 fichiers Python
- **Endpoints API**: 15+
- **Templates**: 6 interfaces HTML
- **Documentation**: 8 guides complets
- **Tests**: 3 suites

---

## ✨ Fonctionnalités

### Annotation
- ✅ Import/Export JSON & CSV
- ✅ Support complet du chinois
- ✅ Tokenization
- ✅ Interface Web moderne

### Test & Feedback
- ✅ Prédiction en temps réel
- ✅ Affichage de confiance (couleurs)
- ✅ Verdict utilisateur (Correct/Corrigé/Faux)
- ✅ Historique complet
- ✅ Statistiques en direct

### Apprentissage
- ✅ Réentraînement automatique
- ✅ Amélioration de confiance
- ✅ Persistance des règles
- ✅ Pas de machine learning - Règles simples

---

## 📖 Documentation

### Pour débuter vite (5 min)
→ `QUICKSTART.md`

### Pour tout savoir (30 min)
→ `README_COMPLETE.md`

### Vue d'ensemble du projet
→ `PROJECT_SUMMARY.md`

### Index de tous les fichiers
→ `INDEX.md`

---

## 🆘 Besoin d'aide?

### Erreur: Port déjà utilisé
```bash
# Changez le port dans le fichier:
# annotation_app.py ligne: port=5000
# model_tester.py ligne: port=5001
```

### Erreur: Paquets manquants
```bash
pip install flask telethon opencc
```

### Pas de prédiction
```
Vérifiez que training_data.json existe
Annotez d'abord 10+ messages
```

---

## 🚀 Prochaines Étapes

1. **Maintenant**: `python launcher.py`
2. **Ensuite**: Annoter 10+ messages
3. **Puis**: Tester et donner du feedback
4. **Enfin**: Vérifier l'amélioration

---

## 📞 Support

Chaque fichier Python contient:
- Docstrings détaillées
- Exemples d'utilisation
- Comments explicatifs

Consultez les fichiers README_*.md pour des explications détaillées.

---

## 📝 Notes

- Tous les fichiers utilisent **UTF-8** encoding
- Les données sont sauvegardées automatiquement
- Aucune API externe requise (sauf Telegram optionnel)
- 100% local - Pas de cloud

---

## 🎓 Pour Apprendre

1. Lisez `QUICKSTART.md` (5 min)
2. Exécutez `launcher.py` (choix 5 pour l'état)
3. Annoter quelques messages
4. Exécutez `demo_feedback.py`
5. Observez les améliorations
6. Lisez `README_COMPLETE.md` pour les détails

---

## ✅ Status

**✨ SYSTÈME COMPLET ET OPÉRATIONNEL**

Tous les composants demandés sont implémentés et testés:
- ✅ Annotation de messages chinois
- ✅ Interface Web interactive
- ✅ Moteur de règles
- ✅ Test et feedback
- ✅ Réentraînement automatique
- ✅ Documentation exhaustive

**Prêt pour la production!** 🚀

---

## 📄 Fichier de Démarrage

Pour commencer maintenant, exécutez:
```bash
python launcher.py
```

Ou visitez directement:
- **Annotation**: `python annotation_app.py`
- **Test**: `python model_tester.py`
- **Demo**: `python demo_feedback.py`

---

**Créé avec ❤️ pour l'annotation de messages chinois**
