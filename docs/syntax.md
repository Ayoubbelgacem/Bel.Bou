# Syntaxe de Bou.Bel

## Mots-clés

| Mot-clé | Signification | Équivalent Python |
|---------|---------------|-------------------|
| `khdem` | Déclarer une variable | `var` / `let` |
| `dallel` | Définir une fonction | `def` / `function` |
| `rejje` | Retourner une valeur | `return` |
| `ikteb` | Afficher un message | `print` |
| `ken` | Si | `if` |
| `sinon_ken` | Sinon si | `elif` |
| `sinon` | Sinon | `else` |
| `tawa` | Tant que | `while` |
| `men ... 7ata` | De ... à (boucle for) | `for i in range(...)` |
| `a3mel` | Faire (début de bloc) | `:` / `do` |
| `s7i7` | Vrai | `True` |
| `ghalet` | Faux | `False` |
| `toroth` | Hérite de | `extends` / `inherits` |
| `jdid` | Constructeur | `__init__` / `constructor` |
| `hetha` | Ceci (self/this) | `this` / `self` |
| `7awel` | Essayer | `try` |
| `ebsed` | Attraper | `catch` / `except` |
| `akhir` | Finalement | `finally` |
| `t7at` | Lancer une exception | `throw` / `raise` |
| `ktif` | Arrêter une boucle | `break` |
| `kaml` | Continuer une boucle | `continue` |

## Types

| Type | Description | Exemple |
|------|-------------|---------|
| `int` | Entier | `42`, `-10` |
| `float` | Flottant | `3.14`, `-1.5` |
| `string` | Chaîne de caractères | `"Bonjour"` |
| `bool` | Booléen | `s7i7`, `ghalet` |
| `char` | Caractère | `'A'` |
| `array` | Tableau | `[1, 2, 3]` |

## Opérateurs

### Arithmétiques
| Opérateur | Description |
|-----------|-------------|
| `+` | Addition / Concaténation |
| `-` | Soustraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |

### Comparaisons
| Opérateur | Description |
|-----------|-------------|
| `==` | Égalité |
| `!=` | Différence |
| `>` | Supérieur |
| `<` | Inférieur |
| `>=` | Supérieur ou égal |
| `<=` | Inférieur ou égal |

### Logiques
| Opérateur | Description |
|-----------|-------------|
| `AND` | ET logique |
| `OR` | OU logique |
| `NOT` | NON logique |

## Exemples de syntaxe

### Déclaration de variable
```boubel
khdem nom = "Ayoub";
khdem age = 25;
```

### Fonction
```boubel
dallel addition(a, b) {
    rejje a + b;
}
```

### Condition
```boubel
ken age >= 18 a3mel {
    ikteb("Majeur");
} sinon {
    ikteb("Mineur");
}
```

### Boucle for
```boubel
i men 0 7ata 10 a3mel {
    ikteb(i);
}
```

### Boucle while
```boubel
tawa x > 0 a3mel {
    ikteb(x);
    x = x - 1;
}
```

### Classe
```boubel
class Personne {
    hetha.nom = "";
    hetha.age = 0;
    
    jdid(n, a) {
        hetha.nom = n;
        hetha.age = a;
    }
    
    dallel afficher() {
        ikteb(hetha.nom + ", " + hetha.age);
    }
}
```

### Try/Catch
```boubel
7awel {
    khdem x = 10 / 0;
} ebsed(e) {
    ikteb("Erreur: " + e);
}
```

### Fichiers
```boubel
ikteb_fi_mlf("fichier.txt", "Contenu");
khdem contenu = iqra_mlf("fichier.txt");
```

## Commentaires

```boubel
# Ceci est un commentaire sur une ligne

/*
   Ceci est un commentaire
   sur plusieurs lignes
*/
```