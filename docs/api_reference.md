# API Référence - Fonctions Built-in

## len()

Retourne la longueur d'une chaîne ou d'un tableau.

**Syntaxe :** `len(valeur)`

**Paramètres :**
- `valeur` : Une chaîne ou un tableau

**Retour :** Entier (longueur)

**Exemple :**
```boubel
khdem texte = "Bonjour";
khdem taille = len(texte);  # 7

khdem tab = [1, 2, 3, 4, 5];
khdem taille_tab = len(tab);  # 5
```

---

## str()

Convertit une valeur en chaîne de caractères.

**Syntaxe :** `str(valeur)`

**Paramètres :**
- `valeur` : N'importe quel type

**Retour :** Chaîne de caractères

**Exemple :**
```boubel
khdem nombre = 42;
khdem texte = str(nombre);  # "42"
```

---

## int()

Convertit une valeur en entier.

**Syntaxe :** `int(valeur)`

**Paramètres :**
- `valeur` : Chaîne ou nombre

**Retour :** Entier

**Exemple :**
```boubel
khdem texte = "123";
khdem nombre = int(texte);  # 123
```

---

## float()

Convertit une valeur en flottant.

**Syntaxe :** `float(valeur)`

**Paramètres :**
- `valeur` : Chaîne ou nombre

**Retour :** Flottant

**Exemple :**
```boubel
khdem texte = "3.14";
khdem nombre = float(texte);  # 3.14
```

---

## type()

Retourne le type d'une valeur.

**Syntaxe :** `type(valeur)`

**Paramètres :**
- `valeur` : N'importe quel type

**Retour :** Chaîne de caractères (nom du type)

**Exemple :**
```boubel
khdem x = 42;
ikteb(type(x));  # "int"

khdem y = "Bonjour";
ikteb(type(y));  # "str"
```

---

## print()

Affiche une ou plusieurs valeurs dans la console.

**Syntaxe :** `print(valeur1, valeur2, ...)`

**Paramètres :**
- `valeur1, valeur2, ...` : Valeurs à afficher

**Retour :** Aucun

**Exemple :**
```boubel
print("Bonjour", "monde");
```

---

## input()

Lit une entrée utilisateur.

**Syntaxe :** `input(prompt)`

**Paramètres :**
- `prompt` : (Optionnel) Message affiché avant la saisie

**Retour :** Chaîne de caractères (saisie utilisateur)

**Exemple :**
```boubel
khdem nom = input("Entrez votre nom: ");
ikteb("Bonjour " + nom);
```

---

## sum()

Calcule la somme des éléments d'un tableau.

**Syntaxe :** `sum(tableau)`

**Paramètres :**
- `tableau` : Tableau de nombres

**Retour :** Nombre (somme)

**Exemple :**
```boubel
khdem tab = [1, 2, 3, 4, 5];
khdem total = sum(tab);  # 15
```

---

## max()

Retourne la valeur maximale d'un tableau.

**Syntaxe :** `max(tableau)`

**Paramètres :**
- `tableau` : Tableau de nombres

**Retour :** Nombre (maximum)

**Exemple :**
```boubel
khdem tab = [3, 7, 2, 9, 5];
khdem maxi = max(tab);  # 9
```

---

## min()

Retourne la valeur minimale d'un tableau.

**Syntaxe :** `min(tableau)`

**Paramètres :**
- `tableau` : Tableau de nombres

**Retour :** Nombre (minimum)

**Exemple :**
```boubel
khdem tab = [3, 7, 2, 9, 5];
khdem mini = min(tab);  # 2
```

---

## abs()

Retourne la valeur absolue d'un nombre.

**Syntaxe :** `abs(nombre)`

**Paramètres :**
- `nombre` : Un nombre

**Retour :** Nombre (valeur absolue)

**Exemple :**
```boubel
khdem x = -42;
khdem absolu = abs(x);  # 42
```

---

## concat()

Concatène deux chaînes.

**Syntaxe :** `concat(chaîne1, chaîne2)`

**Paramètres :**
- `chaîne1` : Première chaîne
- `chaîne2` : Deuxième chaîne

**Retour :** Chaîne concaténée

**Exemple :**
```boubel
khdem a = "Bonjour ";
khdem b = "monde";
khdem result = concat(a, b);  # "Bonjour monde"
```

---

## iqra_mlf()

Lit un fichier et retourne son contenu.

**Syntaxe :** `iqra_mlf(nom_fichier)`

**Paramètres :**
- `nom_fichier` : Chemin du fichier

**Retour :** Contenu du fichier (chaîne)

**Exemple :**
```boubel
khdem contenu = iqra_mlf("fichier.txt");
ikteb(contenu);
```

---

## ikteb_fi_mlf()

Écrit du contenu dans un fichier.

**Syntaxe :** `ikteb_fi_mlf(nom_fichier, contenu)`

**Paramètres :**
- `nom_fichier` : Chemin du fichier
- `contenu` : Contenu à écrire

**Retour :** `s7i7` si succès, `ghalet` si erreur

**Exemple :**
```boubel
ikteb_fi_mlf("fichier.txt", "Contenu du fichier");
```

---

## range()

Génère une séquence de nombres.

**Syntaxes :**
- `range(stop)`
- `range(start, stop)`
- `range(start, stop, step)`

**Paramètres :**
- `start` : (Optionnel) Début (défaut: 0)
- `stop` : Fin (exclue)
- `step` : (Optionnel) Pas (défaut: 1)

**Retour :** Tableau de nombres

**Exemple :**
```boubel
khdem seq = range(5);     # [0, 1, 2, 3, 4]
khdem seq2 = range(2, 7); # [2, 3, 4, 5, 6]
khdem seq3 = range(0, 10, 2); # [0, 2, 4, 6, 8]
```

---

## append()

Ajoute un élément à un tableau.

**Syntaxe :** `append(tableau, élément)`

**Paramètres :**
- `tableau` : Tableau à modifier
- `élément` : Élément à ajouter

**Retour :** Tableau modifié

**Exemple :**
```boubel
khdem tab = [1, 2, 3];
append(tab, 4);  # [1, 2, 3, 4]
```

---

## pop()

Supprime et retourne le dernier élément d'un tableau.

**Syntaxe :** `pop(tableau)`

**Paramètres :**
- `tableau` : Tableau à modifier

**Retour :** Dernier élément supprimé

**Exemple :**
```boubel
khdem tab = [1, 2, 3];
khdem dernier = pop(tab);  # 3, tab = [1, 2]
```

---

## sorted()

Retourne un tableau trié.

**Syntaxe :** `sorted(tableau)`

**Paramètres :**
- `tableau` : Tableau à trier

**Retour :** Tableau trié

**Exemple :**
```boubel
khdem tab = [5, 2, 8, 1, 9];
khdem trie = sorted(tab);  # [1, 2, 5, 8, 9]
```