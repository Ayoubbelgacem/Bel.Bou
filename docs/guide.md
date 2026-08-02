# Guide de démarrage - Bou.Bel

## Premier programme

Créez un fichier `hello.bou` :

```boubel
ikteb("Salam Alaikum! 🌍");
```

Exécutez-le :

```bash
python main.py hello.bou
```

Sortie :
```
Salam Alaikum! 🌍
```

## Variables

```boubel
khdem nom = "Mohamed";     # Chaîne de caractères
khdem age = 25;            # Entier
khdem taille = 1.75;       # Flottant
khdem actif = s7i7;        # Booléen (s7i7 = true, ghalet = false)
khdem lettre = 'A';        # Caractère
```

## Conditions

```boubel
khdem score = 85;

ken score >= 90 a3mel {
    ikteb("Excellent!");
} sinon_ken score >= 75 a3mel {
    ikteb("Bien!");
} sinon {
    ikteb("Échec!");
}
```

## Boucles

### FOR (men ... 7ata)

```boubel
i men 1 7ata 5 a3mel {
    ikteb(i);
}
# Affiche 1, 2, 3, 4, 5
```

### WHILE (tawa)

```boubel
khdem compteur = 0;
tawa compteur < 5 a3mel {
    ikteb(compteur);
    compteur = compteur + 1;
}
```

## Fonctions

```boubel
dallel addition(a, b) {
    rejje a + b;
}

khdem resultat = addition(10, 20);
ikteb(resultat);  # Affiche 30
```

## Récursivité

```boubel
dallel factorielle(n) {
    ken n <= 1 a3mel {
        rejje 1;
    } sinon {
        rejje n * factorielle(n - 1);
    }
}

ikteb(factorielle(5));  # Affiche 120
```

## Classes et OOP

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
}

khdem animal = new Animal("Max", 3);
animal.parler();  # Affiche "Max fait un bruit."
```

## Héritage

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
}

khdem chien = new Chien("Rex", 5, "Berger");
chien.parler();  # Affiche "Rex dit: Woof Woof! 🐶"
```

## Try / Catch / Finally

```boubel
7awel {
    khdem result = 10 / 0;
    ikteb(result);
} ebsed(e) {
    ikteb("Erreur: " + e);
} akhir {
    ikteb("Finally exécuté");
}
```

## Fichiers

```boubel
# Écrire
ikteb_fi_mlf("data.txt", "Contenu du fichier");

# Lire
khdem contenu = iqra_mlf("data.txt");
ikteb(contenu);
```

## Prochaines étapes

Consultez les [exemples](../examples/) pour plus de programmes complets.