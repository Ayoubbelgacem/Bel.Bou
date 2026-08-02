#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>

long long addition(long long a, long long b) {
    return (long long)(a + b);
}

long long factorielle(long long n) {
    if ((n <= 1)) {
        return (long long)1;
    } else {
        return (long long)(n * factorielle((n - 1)));
    }
    return 0;
}

long long est_pair(long long n) {
    if ((((2 != 0) ? (n % 2) : 0) == 0)) {
        return (long long)1;
    } else {
        return (long long)0;
    }
    return 0;
}

long long max3(long long a, long long b, long long c) {
    long long max = a;
    if ((b > max)) {
        max = b;
    }
    if ((c > max)) {
        max = c;
    }
    return (long long)max;
}

long long moyenne3(long long a, long long b, long long c) {
    return (long long)((3 != 0) ? (((a + b) + c) / 3) : 0);
}

long long fibonacci(long long n) {
    if ((n <= 1)) {
        return (long long)n;
    } else {
        return (long long)(fibonacci((n - 1)) + fibonacci((n - 2)));
    }
    return 0;
}

int main(int argc, char** argv) {
    printf("%s\n", "========================================");
    printf("%s\n", "  🐪 BOU.BEL - TEST COMPILATEUR");
    printf("%s\n", "========================================");
    printf("%s\n", "");
    printf("%s\n", "--- 1. VARIABLES ---");
    long long x = 10;
    long long y = 20;
    long long z = (x + y);
    printf("%s\n", "x = ");
    printf("%lld\n", (long long)x);
    printf("%s\n", "\ny = ");
    printf("%lld\n", (long long)y);
    printf("%s\n", "\nz = ");
    printf("%lld\n", (long long)z);
    printf("%s\n", "\n");
    printf("%s\n", "--- 2. ARITHMÉTIQUE ---");
    long long a = 15;
    long long b = 7;
    printf("%s\n", "a = ");
    printf("%lld\n", (long long)a);
    printf("%s\n", ", b = ");
    printf("%lld\n", (long long)b);
    printf("%s\n", "\n");
    printf("%s\n", "a + b = ");
    printf("%lld\n", (long long)(a + b));
    printf("%s\n", "\n");
    printf("%s\n", "a - b = ");
    printf("%lld\n", (long long)(a - b));
    printf("%s\n", "\n");
    printf("%s\n", "a * b = ");
    printf("%lld\n", (long long)(a * b));
    printf("%s\n", "\n");
    printf("%s\n", "a / b = ");
    printf("%lld\n", (long long)((b != 0) ? (a / b) : 0));
    printf("%s\n", "\n");
    printf("%s\n", "a % b = ");
    printf("%lld\n", (long long)((b != 0) ? (a % b) : 0));
    printf("%s\n", "\n");
    printf("%s\n", "--- 3. COMPARAISONS ---");
    long long p = 10;
    long long q = 20;
    printf("%s\n", "p = ");
    printf("%lld\n", (long long)p);
    printf("%s\n", ", q = ");
    printf("%lld\n", (long long)q);
    printf("%s\n", "\n");
    printf("%s\n", "p == q: ");
    printf("%lld\n", (long long)(p == q));
    printf("%s\n", "\n");
    printf("%s\n", "p != q: ");
    printf("%lld\n", (long long)(p != q));
    printf("%s\n", "\n");
    printf("%s\n", "p > q: ");
    printf("%lld\n", (long long)(p > q));
    printf("%s\n", "\n");
    printf("%s\n", "p < q: ");
    printf("%lld\n", (long long)(p < q));
    printf("%s\n", "\n");
    printf("%s\n", "p >= q: ");
    printf("%lld\n", (long long)(p >= q));
    printf("%s\n", "\n");
    printf("%s\n", "p <= q: ");
    printf("%lld\n", (long long)(p <= q));
    printf("%s\n", "\n");
    printf("%s\n", "--- 4. CONDITIONS ---");
    long long score = 85;
    if ((score >= 90)) {
        printf("%s\n", "Score: Excellent!\n");
    } else {
        if ((score >= 75)) {
            printf("%s\n", "Score: Bien!\n");
        } else {
            if ((score >= 60)) {
                printf("%s\n", "Score: Passable!\n");
            } else {
                printf("%s\n", "Score: Échec!\n");
            }
        }
    }
    long long age = 17;
    if ((age >= 18)) {
        printf("%s\n", "Vous êtes majeur.\n");
    } else {
        printf("%s\n", "Vous êtes mineur.\n");
    }
    printf("%s\n", "--- 5. BOUCLES FOR ---");
    printf("%s\n", "Comptage de 1 à 5:\n");
    for (long long i = 1; i <= 5; i++) {
        printf("%lld\n", (long long)i);
        printf("%s\n", " ");
    }
    printf("%s\n", "\n");
    printf("%s\n", "Table de multiplication de 3:\n");
    for (long long i = 1; i <= 10; i++) {
        printf("%s\n", "3 × ");
        printf("%lld\n", (long long)i);
        printf("%s\n", " = ");
        printf("%lld\n", (long long)(3 * i));
        printf("%s\n", "\n");
    }
    printf("%s\n", "--- 6. BOUCLES WHILE ---");
    long long compteur = 0;
    while ((compteur < 5)) {
        printf("%s\n", "Compteur: ");
        printf("%lld\n", (long long)compteur);
        printf("%s\n", "\n");
        compteur = (compteur + 1);
    }
    printf("%s\n", "--- 7. FONCTIONS ---");
    long long resultat = addition(15, 30);
    printf("%s\n", "15 + 30 = ");
    printf("%lld\n", (long long)resultat);
    printf("%s\n", "\n");
    printf("%s\n", "Factorielle de 5 = ");
    printf("%lld\n", (long long)factorielle(5));
    printf("%s\n", "\n");
    printf("%s\n", "7 est pair? ");
    printf("%lld\n", (long long)est_pair(7));
    printf("%s\n", "\n");
    printf("%s\n", "8 est pair? ");
    printf("%lld\n", (long long)est_pair(8));
    printf("%s\n", "\n");
    printf("%s\n", "--- 8. FONCTIONS MULTIPLES ---");
    printf("%s\n", "Max de 10, 20, 30 = ");
    printf("%lld\n", (long long)max3(10, 20, 30));
    printf("%s\n", "\n");
    printf("%s\n", "Moyenne de 10, 20, 30 = ");
    printf("%lld\n", (long long)moyenne3(10, 20, 30));
    printf("%s\n", "\n");
    printf("%s\n", "--- 9. BOUCLES IMBRIQUÉES ---");
    printf("%s\n", "Table de multiplication (5x5):\n");
    for (long long i = 1; i <= 5; i++) {
        for (long long j = 1; j <= 5; j++) {
            printf("%lld\n", (long long)(i * j));
            printf("%s\n", " ");
        }
        printf("%s\n", "\n");
    }
    printf("%s\n", "--- 10. RÉCURSIVITÉ ---");
    printf("%s\n", "Fibonacci(0) = ");
    printf("%lld\n", (long long)fibonacci(0));
    printf("%s\n", "\n");
    printf("%s\n", "Fibonacci(1) = ");
    printf("%lld\n", (long long)fibonacci(1));
    printf("%s\n", "\n");
    printf("%s\n", "Fibonacci(5) = ");
    printf("%lld\n", (long long)fibonacci(5));
    printf("%s\n", "\n");
    printf("%s\n", "Fibonacci(10) = ");
    printf("%lld\n", (long long)fibonacci(10));
    printf("%s\n", "\n");
    printf("%s\n", "--- 11. RÉSULTAT FINAL ---");
    long long notes[10];
    notes[0] = 14;
    notes[1] = 16;
    notes[2] = 18;
    notes[3] = 12;
    notes[4] = 15;
    notes[5] = 17;
    notes[6] = 19;
    notes[7] = 13;
    notes[8] = 16;
    notes[9] = 15;
    long long sum = 0;
    for (long long i = 0; i <= (10 - 1); i++) {
        sum = (sum + notes[i]);
    }
    long long moyenne = ((10 != 0) ? (sum / 10) : 0);
    printf("%s\n", "Notes: ");
    printf("%lld\n", (long long)notes);
    printf("%s\n", "\n");
    printf("%s\n", "Somme: ");
    printf("%lld\n", (long long)sum);
    printf("%s\n", "\n");
    printf("%s\n", "Moyenne: ");
    printf("%lld\n", (long long)moyenne);
    printf("%s\n", "\n");
    if ((moyenne >= 15)) {
        printf("%s\n", "✅ Félicitations! Excellente moyenne!\n");
    } else {
        if ((moyenne >= 12)) {
            printf("%s\n", "👍 Bien! Moyenne satisfaisante.\n");
        } else {
            printf("%s\n", "📚 Travaillez encore plus fort!\n");
        }
    }
    printf("%s\n", "\n");
    printf("%s\n", "========================================\n");
    printf("%s\n", "  🎉 TEST COMPILATEUR TERMINÉ AVEC SUCCÈS!\n");
    printf("%s\n", "========================================\n");
    return 0;
}
