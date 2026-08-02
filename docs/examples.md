# Exemples Bou.Bel

## Hello World

```boubel
ikteb("Salam Alaikum! 🌍");
```

## Variables et types

```boubel
khdem nom = "Ayoub";
khdem age = 25;
khdem taille = 1.80;
khdem actif = s7i7;

ikteb("Nom: " + nom);
ikteb("Age: " + age);
ikteb("Taille: " + taille);
ikteb("Actif: " + actif);
```

## Conditions

```boubel
khdem score = 85;

ken score >= 90 a3mel {
    ikteb("Excellent!");
} sinon_ken score >= 75 a3mel {
    ikteb("Bien!");
} sinon_ken score >= 60 a3mel {
    ikteb("Passable!");
} sinon {
    ikteb("Échec!");
}
```

## Boucles

### For
```boubel
# Comptage de 1 à 10
i men 1 7ata 10 a3mel {
    ikteb(i);
}

# Table de multiplication
i men 1 7ata 10 a3mel {
    ikteb("5 × " + i + " = " + (5 * i));
}
```

### While
```boubel
khdem x = 10;
tawa x > 0 a3mel {
    ikteb(x);
    x = x - 2;
}
```

## Fonctions

### Fonction simple
```boubel
dallel addition(a, b) {
    rejje a + b;
}

khdem result = addition(15, 30);
ikteb("15 + 30 = " + result);
```

### Fonction récursive
```boubel
dallel factorielle(n) {
    ken n <= 1 a3mel {
        rejje 1;
    } sinon {
        rejje n * factorielle(n - 1);
    }
}

ikteb("Factorielle de 5 = " + factorielle(5));
ikteb("Factorielle de 7 = " + factorielle(7));
```

## Classes

### Classe simple
```boubel
class Animal {
    hetha.nom = "Inconnu";
    hetha.age = 0;
    
    jdid(n, a) {
        hetha.nom = n;
        hetha.age = a;
    }
    
    dallel parler() {
        ikteb(hetha.nom + " fait un bruit.");
    }
    
    dallel afficher() {
        ikteb("Nom: " + hetha.nom + ", Age: " + hetha.age);
    }
}

khdem animal = new Animal("Max", 3);
animal.afficher();
animal.parler();
```

### Héritage
```boubel
class Chien toroth Animal {
    hetha.race = "Inconnue";
    
    jdid(n, a, r) {
        super(n, a);
        hetha.race = r;
    }
    
    dallel parler() {
        ikteb(hetha.nom + " dit: Woof Woof! 🐶");
    }
    
    dallel afficher() {
        ikteb("🐕 Chien - Nom: " + hetha.nom + ", Age: " + hetha.age + ", Race: " + hetha.race);
    }
}

khdem chien = new Chien("Rex", 5, "Berger Allemand");
chien.afficher();
chien.parler();
```

## Exceptions

```boubel
7awel {
    khdem result = 10 / 0;
    ikteb("Résultat: " + result);
} ebsed(e) {
    ikteb("❌ Erreur attrapée: " + e);
} akhir {
    ikteb("✅ Finally exécuté");
}
```

## Fichiers

```boubel
# Écrire un fichier
ikteb_fi_mlf("test.txt", "Bienvenue dans Bou.Bel!\nCeci est un test.");

# Lire un fichier
khdem contenu = iqra_mlf("test.txt");
ikteb("Contenu du fichier:");
ikteb(contenu);
```

## Tableaux

```boubel
khdem notes = [15, 18, 12, 20, 9, 14];
ikteb("Notes: " + notes);
ikteb("Première note: " + notes[0]);
ikteb("Nombre de notes: " + len(notes));
```

## Statistiques

```boubel
dallel calculer_moyenne(tab) {
    khdem sum = 0;
    i men 0 7ata len(tab)-1 a3mel {
        sum = sum + tab[i];
    }
    rejje sum / len(tab);
}

khdem notes = [12, 15, 18, 14, 16, 20, 13];
khdem moyenne = calculer_moyenne(notes);
ikteb("Moyenne: " + moyenne);
```

## Programme complet

Voir [examples/test_complete.bou](../examples/test_complete.bou) pour un programme complet testant toutes les fonctionnalités.