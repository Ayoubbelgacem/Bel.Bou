/*
 * Bou.Bel Runtime - Header
 * ✅ AJOUT : ref_count pour le garbage collector
 * ✅ AJOUT : fonctions de temps pour wa9t.bou
 */

#ifndef BOUBEL_RUNTIME_H
#define BOUBEL_RUNTIME_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * 0. COMPATIBILITÉ PORTABLE
 * ============================================================ */

#ifdef __GNUC__
    #define BOUBEL_THREAD_LOCAL __thread
#elif defined(_MSC_VER)
    #define BOUBEL_THREAD_LOCAL __declspec(thread)
#else
    #define BOUBEL_THREAD_LOCAL
#endif

/* ============================================================
 * 1. CLASSES ET OBJETS (avec comptage de références)
 * ============================================================ */

typedef struct BouBelObject {
    void* class_ptr;
    uint64_t* fields;
    uint64_t field_count;
    uint64_t ref_count;   // ✅ Nouveau : compteur de références
} BouBelObject;

typedef struct BouBelClass {
    char* name;
    struct BouBelClass* parent;
    uint64_t field_count;
    uint64_t* field_indices;
    char** field_names;
    char** field_types;
    void** methods;
    char** method_names;
    uint64_t method_count;
} BouBelClass;

BouBelObject* boubel_new_object(BouBelClass* class_ptr, uint64_t* args, uint64_t arg_count);
BouBelClass* boubel_new_class(const char* name, BouBelClass* parent);
void boubel_class_add_field(BouBelClass* cls, const char* name, const char* type);
void boubel_class_add_method(BouBelClass* cls, const char* name, void* method_ptr);

// ✅ Fonctions de gestion des références
void boubel_incref(BouBelObject* obj);
void boubel_decref(BouBelObject* obj);

uint64_t boubel_object_get_field(BouBelObject* obj, const char* field_name);
void boubel_object_set_field(BouBelObject* obj, const char* field_name, uint64_t value);
char* boubel_object_get_field_string(BouBelObject* obj, const char* field_name);
void boubel_object_set_field_string(BouBelObject* obj, const char* field_name, const char* value);
uint64_t boubel_object_call_method(BouBelObject* obj, const char* method_name, uint64_t* args, uint64_t arg_count);
void boubel_free_object(BouBelObject* obj);

/* ============================================================
 * 2. TRY / CATCH / FINALLY (modèle coopératif)
 * ============================================================ */

typedef struct BouBelException {
    char* message;
    uint64_t error_code;
} BouBelException;

typedef struct BouBelTryContext {
    BouBelException* exception;
    struct BouBelTryContext* parent;
    uint64_t in_try;
} BouBelTryContext;

extern BOUBEL_THREAD_LOCAL BouBelTryContext* boubel_current_try_context;

int boubel_try_start(void);
int boubel_try_end(void);
void boubel_throw(const char* message, uint64_t error_code);
BouBelException* boubel_get_exception(void);
char* boubel_exception_message(void);
int boubel_exception_pending(void);
void boubel_free_exception(BouBelException* exc);

/* ============================================================
 * 3. CALLBACKS
 * ============================================================ */

typedef uint64_t (*BouBelCallback)(uint64_t arg1, uint64_t arg2);

typedef struct BouBelClosure {
    void* function_ptr;
    uint64_t* env;
    uint64_t env_size;
} BouBelClosure;

BouBelClosure* boubel_create_callback(void* function_ptr);
BouBelClosure* boubel_create_closure(void* function_ptr, uint64_t* env, uint64_t env_size);
uint64_t boubel_call_callback(BouBelClosure* closure, uint64_t* args, uint64_t arg_count);
void boubel_free_callback(BouBelClosure* closure);

/* ============================================================
 * 4. FONCTIONS UTILITAIRES
 * ============================================================ */

char* boubel_value_to_string(uint64_t value, const char* type);
uint64_t boubel_string_to_value(const char* str, const char* type);
void boubel_print_value(uint64_t value, const char* type);
uint64_t boubel_len(void* value, const char* type);

/* ============================================================
 * 5. FICHIERS (FILE I/O)
 * ============================================================ */

int boubel_file_write(const char* filename, const char* content);
char* boubel_file_read(const char* filename);

/* ============================================================
 * 6. FONCTIONS DE TEMPS (pour wa9t.bou)
 * ============================================================ */

uint64_t boubel_time_now(void);
void boubel_sleep(uint64_t seconds);

/* ============================================================
 * 7. FONCTIONS DE DÉBOGUAGE
 * ============================================================ */

void boubel_debug_print(const char* msg);
void boubel_debug_print_int(const char* label, uint64_t value);
void boubel_debug_print_str(const char* label, const char* value);

#ifdef __cplusplus
}
#endif

#endif /* BOUBEL_RUNTIME_H */