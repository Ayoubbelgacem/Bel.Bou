class CodeExample {
  final String title;
  final String code;
  const CodeExample({required this.title, required this.code});
}

const List<CodeExample> tounsiExamples = [
  CodeExample(
    title: '👋 Salut basique',
    code: '''# Exemple simple
ikteb("Salam Ayoub");

khdem age = 25;

ken age > 18 a3mel {
    ikteb("Kbir");
}
''',
  ),
  CodeExample(
    title: '🔁 Boucles (for / while)',
    code: '''ikteb("Comptage de 1 à 5:");
men i 1 7ata 5 a3mel {
    ikteb("  " + i);
}
ikteb("");
ikteb("Table de multiplication de 3:");
men i 1 7ata 10 a3mel {
    ikteb("  3 × " + i + " = " + (3 * i));
}
ikteb("");
ikteb("Nombres pairs de 1 à 10:");
men i 1 7ata 10 a3mel {
    ken i % 2 == 0 a3mel {
        ikteb("  " + i + " est pair");
    }
}
ikteb("");
ikteb("Boucle WHILE:");
khdem compteur = 0;
tawa compteur < 5 a3mel {
    ikteb("  Compteur: " + compteur);
    compteur = compteur + 1;
}
''',
  ),
  CodeExample(
    title: '🧮 Fonction',
    code: '''dallel somme(a, b) {
    rejje a + b;
}

ikteb(somme(3, 4));
''',
  ),
  CodeExample(
    title: '🏛️ Classe (OOP)',
    code: '''class Personne {
    hetha.nom = "Inconnu";

    jdid(n) {
        hetha.nom = n;
    }

    dallel salam() {
        ikteb("Salam ken enti " + hetha.nom);
    }
}

khdem p = new Personne("Ayoub");
p.salam();
''',
  ),
  CodeExample(
    title: '🐕 Héritage (Animal → Chien)',
    code: '''class Animal {
    hetha.nom = "Inconnu";
    hetha.age = 0;
    jdid(n, a) { hetha.nom = n; hetha.age = a; }
    dallel parler() { ikteb(hetha.nom + " fait un bruit."); }
    dallel afficher() { ikteb("Nom: " + hetha.nom + ", Age: " + hetha.age); }
}

class Chien toroth Animal {
    hetha.race = "Inconnue";
    jdid(n, a, r) { super(n, a); hetha.race = r; }
    dallel parler() { ikteb(hetha.nom + " dit: Woof Woof! 🐶"); }
    dallel afficher() {
        ikteb("🐕 Chien - Nom: " + hetha.nom + ", Age: " + hetha.age + ", Race: " + hetha.race);
    }
}

khdem chien1 = new Chien("Rex", 5, "Berger Allemand");
chien1.afficher();
chien1.parler();
''',
  ),
  CodeExample(
    title: '🧯 Try / Catch / Finally',
    code: '''7awel {
    ikteb("Tentative: Division par zéro...");
    khdem result = 10 / 0;
    ikteb("Résultat: " + result);
} ebsed(e) {
    ikteb("❌ Erreur attrapée: " + e);
} akhir {
    ikteb("✅ Finally");
}
''',
  ),
  CodeExample(
    title: '⏱️ Modules: wa9t + json',
    code: '''jib "wa9t";
jib "json";

ikteb("⏱️ Test de wa9t.bou");
khdem t1 = time_now();
ikteb("Timestamp avant: " + t1);

ikteb("🛌 Pause de 2 secondes...");
rqed(2);

khdem t2 = time_now();
ikteb("Timestamp après: " + t2);
ikteb("Différence: " + (t2 - t1) + " secondes");

ikteb("");

ikteb("📝 Test de json.bou");
khdem liste = [1, 2, 3, "test", s7i7];
khdem json_list = to_json(liste);
ikteb("Liste originale: " + liste);
ikteb("JSON encodé: " + json_list);

ikteb("✅ Test terminé");
''',
  ),
  CodeExample(
    title: '🧪 Test natif (récursivité)',
    code: '''# examples/test_native.bou
khdem x = 10;
khdem y = 20;
khdem z = x + y;

ikteb("x = ");
ikteb(x);
ikteb("\\ny = ");
ikteb(y);
ikteb("\\nz = ");
ikteb(z);

dallel factorial(n) {
    ken n <= 1 a3mel {
        rejje 1;
    } sinon {
        rejje n * factorial(n - 1);
    }
}

ikteb("\\nFactorial 5 = ");
ikteb(factorial(5));
''',
  ),
  CodeExample(
    title: '🐪 Test complet (tout-en-un)',
    code: '''# ============================================
# BOU.BEL - TEST COMPLET (version LLVM)
# ============================================

ikteb("========================================");
ikteb("  🐪 BOU.BEL - TEST COMPLET");
ikteb("========================================");
ikteb("");

# --- 1. VARIABLES ---
ikteb("--- 1. VARIABLES ---");
khdem nom = "Ayoub";
khdem age = 25;
khdem taille = 1.80;
khdem actif = s7i7;
khdem lettre = 'A';
ikteb("Nom: " + nom);
ikteb("Age: " + age);
ikteb("Taille: " + taille);
ikteb("Actif: " + actif);
ikteb("Lettre: " + lettre);
ikteb("");

# --- 2. ARRAYS ---
ikteb("--- 2. ARRAYS ---");
khdem notes = [15, 18, 12, 20, 9, 14];
ikteb("Notes: " + notes);
ikteb("Première: " + notes[0]);
ikteb("Dernière: " + notes[5]);
ikteb("Nombre: " + len(notes));
notes[2] = 16;
men i 0 7ata 5 a3mel {
    ikteb("  Notes[" + i + "] = " + notes[i]);
}
ikteb("");

# --- 3. CONDITIONS ---
ikteb("--- 3. CONDITIONS ---");
khdem score = 85;
ken score >= 90 a3mel {
    ikteb("Score: " + score + " → Excellent!");
} sinon_ken score >= 75 a3mel {
    ikteb("Score: " + score + " → Bien!");
} sinon {
    ikteb("Score: " + score + " → Échec!");
}
ikteb("");

# --- 4. FONCTIONS ---
ikteb("--- 4. FONCTIONS ---");
dallel factorielle(n) {
    ken n <= 1 a3mel { rejje 1; }
    rejje n * factorielle(n - 1);
}
ikteb("Factorielle de 5 = " + factorielle(5));
ikteb("");

# --- 5. CLASSES ET HÉRITAGE ---
ikteb("--- 5. CLASSES ET HÉRITAGE ---");
class Animal {
    hetha.nom = "Inconnu";
    jdid(n) { hetha.nom = n; }
    dallel parler() { ikteb(hetha.nom + " fait un bruit."); }
}
class Chien toroth Animal {
    jdid(n) { super(n); }
    dallel parler() { ikteb(hetha.nom + " dit: Woof Woof! 🐶"); }
}
khdem chien1 = new Chien("Rex");
chien1.parler();
ikteb("");

# --- 6. TRY/CATCH ---
ikteb("--- 6. TRY/CATCH ---");
7awel {
    khdem result = 10 / 0;
} ebsed(e) {
    ikteb("❌ Erreur attrapée: " + e);
} akhir {
    ikteb("✅ Finally");
}
ikteb("");

ikteb("========================================");
ikteb("  🎉 PROGRAMME TERMINÉ AVEC SUCCÈS!");
ikteb("========================================");
''',
  ),
];
