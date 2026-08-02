/*
 * Bou.Bel Runtime - Implémentation
 * ✅ AJOUT : comptage de références (incref/decref)
 * ✅ AJOUT : fonctions de temps (time_now, sleep)
 */

#include "boubel_runtime.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/* ============================================================
 * 0. THREAD LOCAL CONTEXT
 * ============================================================ */

BOUBEL_THREAD_LOCAL BouBelTryContext* boubel_current_try_context = NULL;

/* ============================================================
 * 1. GESTION DES CLASSES ET OBJETS
 * ============================================================ */

BouBelClass* boubel_new_class(const char* name, BouBelClass* parent) {
    BouBelClass* cls = (BouBelClass*)malloc(sizeof(BouBelClass));
    if (!cls) return NULL;

    cls->name = strdup(name);
    cls->parent = parent;
    cls->field_count = 0;
    cls->field_indices = NULL;
    cls->field_names = NULL;
    cls->field_types = NULL;
    cls->methods = NULL;
    cls->method_names = NULL;
    cls->method_count = 0;

    if (parent) {
        for (uint64_t i = 0; i < parent->field_count; i++) {
            boubel_class_add_field(cls, parent->field_names[i], parent->field_types[i]);
        }
        for (uint64_t i = 0; i < parent->method_count; i++) {
            boubel_class_add_method(cls, parent->method_names[i], parent->methods[i]);
        }
    }

    return cls;
}

void boubel_class_add_field(BouBelClass* cls, const char* name, const char* type) {
    if (!cls) return;

    cls->field_count++;
    cls->field_names = (char**)realloc(cls->field_names, cls->field_count * sizeof(char*));
    cls->field_types = (char**)realloc(cls->field_types, cls->field_count * sizeof(char*));
    cls->field_indices = (uint64_t*)realloc(cls->field_indices, cls->field_count * sizeof(uint64_t));

    cls->field_names[cls->field_count - 1] = strdup(name);
    cls->field_types[cls->field_count - 1] = strdup(type);
    cls->field_indices[cls->field_count - 1] = cls->field_count - 1;
}

void boubel_class_add_method(BouBelClass* cls, const char* name, void* method_ptr) {
    if (!cls) return;

    for (uint64_t i = 0; i < cls->method_count; i++) {
        if (strcmp(cls->method_names[i], name) == 0) {
            cls->methods[i] = method_ptr;  /* override */
            return;
        }
    }

    cls->method_count++;
    cls->method_names = (char**)realloc(cls->method_names, cls->method_count * sizeof(char*));
    cls->methods = (void**)realloc(cls->methods, cls->method_count * sizeof(void*));

    cls->method_names[cls->method_count - 1] = strdup(name);
    cls->methods[cls->method_count - 1] = method_ptr;
}

BouBelObject* boubel_new_object(BouBelClass* class_ptr, uint64_t* args, uint64_t arg_count) {
    if (!class_ptr) return NULL;

    BouBelObject* obj = (BouBelObject*)malloc(sizeof(BouBelObject));
    if (!obj) return NULL;

    obj->class_ptr = (void*)class_ptr;
    obj->field_count = class_ptr->field_count;
    obj->fields = (uint64_t*)calloc(obj->field_count, sizeof(uint64_t));
    obj->ref_count = 1;

    if (!obj->fields) {
        free(obj);
        return NULL;
    }

    for (uint64_t i = 0; i < arg_count && i < obj->field_count; i++) {
        obj->fields[i] = args[i];
    }

    return obj;
}

void boubel_incref(BouBelObject* obj) {
    if (obj) {
        obj->ref_count++;
    }
}

void boubel_decref(BouBelObject* obj) {
    if (!obj) return;
    obj->ref_count--;
    if (obj->ref_count == 0) {
        boubel_free_object(obj);
    }
}

uint64_t boubel_object_get_field(BouBelObject* obj, const char* field_name) {
    if (!obj || !field_name) return 0;

    BouBelClass* cls = (BouBelClass*)obj->class_ptr;
    if (!cls) return 0;

    for (uint64_t i = 0; i < cls->field_count; i++) {
        if (strcmp(cls->field_names[i], field_name) == 0) {
            return obj->fields[i];
        }
    }
    return 0;
}

void boubel_object_set_field(BouBelObject* obj, const char* field_name, uint64_t value) {
    if (!obj || !field_name) return;

    BouBelClass* cls = (BouBelClass*)obj->class_ptr;
    if (!cls) return;

    for (uint64_t i = 0; i < cls->field_count; i++) {
        if (strcmp(cls->field_names[i], field_name) == 0) {
            obj->fields[i] = value;
            return;
        }
    }
}

char* boubel_object_get_field_string(BouBelObject* obj, const char* field_name) {
    if (!obj || !field_name) return NULL;

    BouBelClass* cls = (BouBelClass*)obj->class_ptr;
    if (!cls) return NULL;

    for (uint64_t i = 0; i < cls->field_count; i++) {
        if (strcmp(cls->field_names[i], field_name) == 0) {
            if (strcmp(cls->field_types[i], "string") == 0) {
                return (char*)(uintptr_t)obj->fields[i];
            }
            return NULL;
        }
    }
    return NULL;
}

void boubel_object_set_field_string(BouBelObject* obj, const char* field_name, const char* value) {
    if (!obj || !field_name) return;

    BouBelClass* cls = (BouBelClass*)obj->class_ptr;
    if (!cls) return;

    for (uint64_t i = 0; i < cls->field_count; i++) {
        if (strcmp(cls->field_names[i], field_name) == 0) {
            obj->fields[i] = (uint64_t)(uintptr_t)value;
            return;
        }
    }
}

uint64_t boubel_object_call_method(BouBelObject* obj, const char* method_name, uint64_t* args, uint64_t arg_count) {
    if (!obj || !method_name) return 0;

    BouBelClass* cls = (BouBelClass*)obj->class_ptr;
    if (!cls) return 0;

    for (uint64_t i = 0; i < cls->method_count; i++) {
        if (strcmp(cls->method_names[i], method_name) == 0) {
            typedef uint64_t (*MethodFunc)(BouBelObject*, uint64_t*, uint64_t);
            MethodFunc func = (MethodFunc)cls->methods[i];
            return func(obj, args, arg_count);
        }
    }
    return 0;
}

void boubel_free_object(BouBelObject* obj) {
    if (obj) {
        if (obj->fields) free(obj->fields);
        free(obj);
    }
}

/* ============================================================
 * 2. TRY / CATCH / FINALLY (modèle coopératif)
 * ============================================================ */

int boubel_try_start(void) {
    BouBelTryContext* ctx = (BouBelTryContext*)malloc(sizeof(BouBelTryContext));
    if (!ctx) return 0;

    ctx->parent = boubel_current_try_context;
    ctx->exception = NULL;
    ctx->in_try = 1;
    boubel_current_try_context = ctx;

    return 1;
}

int boubel_try_end(void) {
    BouBelTryContext* ctx = boubel_current_try_context;
    if (ctx) {
        boubel_current_try_context = ctx->parent;
        int in_try = ctx->in_try;
        if (ctx->exception) {
            boubel_free_exception(ctx->exception);
        }
        free(ctx);
        return in_try;
    }
    return 0;
}

void boubel_throw(const char* message, uint64_t error_code) {
    BouBelTryContext* ctx = boubel_current_try_context;

    if (ctx) {
        if (!ctx->exception) {
            BouBelException* exc = (BouBelException*)malloc(sizeof(BouBelException));
            if (exc) {
                exc->message = strdup(message);
                exc->error_code = error_code;
                ctx->exception = exc;
            }
        }
        return;
    }

    fprintf(stderr, "\n❌ Uncaught exception: %s\n", message);
    exit(1);
}

int boubel_exception_pending(void) {
    BouBelTryContext* ctx = boubel_current_try_context;
    return (ctx && ctx->exception) ? 1 : 0;
}

BouBelException* boubel_get_exception(void) {
    BouBelTryContext* ctx = boubel_current_try_context;
    if (ctx) {
        return ctx->exception;
    }
    return NULL;
}

char* boubel_exception_message(void) {
    BouBelTryContext* ctx = boubel_current_try_context;
    if (!ctx || !ctx->exception || !ctx->exception->message) {
        return "";
    }
    return ctx->exception->message;
}

void boubel_free_exception(BouBelException* exc) {
    if (exc) {
        if (exc->message) free(exc->message);
        free(exc);
    }
}

/* ============================================================
 * 3. CALLBACKS
 * ============================================================ */

BouBelClosure* boubel_create_callback(void* function_ptr) {
    BouBelClosure* closure = (BouBelClosure*)malloc(sizeof(BouBelClosure));
    if (!closure) return NULL;

    closure->function_ptr = function_ptr;
    closure->env = NULL;
    closure->env_size = 0;
    return closure;
}

BouBelClosure* boubel_create_closure(void* function_ptr, uint64_t* env, uint64_t env_size) {
    BouBelClosure* closure = (BouBelClosure*)malloc(sizeof(BouBelClosure));
    if (!closure) return NULL;

    closure->function_ptr = function_ptr;
    closure->env_size = env_size;
    closure->env = (uint64_t*)malloc(env_size * sizeof(uint64_t));
    if (closure->env) {
        memcpy(closure->env, env, env_size * sizeof(uint64_t));
    }
    return closure;
}

uint64_t boubel_call_callback(BouBelClosure* closure, uint64_t* args, uint64_t arg_count) {
    if (!closure || !closure->function_ptr) return 0;

    typedef uint64_t (*CallbackFunc)(uint64_t*, uint64_t, uint64_t*, uint64_t);
    CallbackFunc func = (CallbackFunc)closure->function_ptr;
    return func(closure->env, closure->env_size, args, arg_count);
}

void boubel_free_callback(BouBelClosure* closure) {
    if (closure) {
        if (closure->env) free(closure->env);
        free(closure);
    }
}

/* ============================================================
 * 4. FONCTIONS UTILITAIRES
 * ============================================================ */

char* boubel_value_to_string(uint64_t value, const char* type) {
    static char buffer[256];

    if (!type) {
        snprintf(buffer, sizeof(buffer), "%llu", (unsigned long long)value);
        return buffer;
    }

    if (strcmp(type, "string") == 0) {
        char* str = (char*)(uintptr_t)value;
        if (str != NULL && (uintptr_t)str > 0x1000) {
            return str;
        }
        return "";
    } else if (strcmp(type, "float") == 0) {
        double d;
        memcpy(&d, &value, sizeof(double));
        snprintf(buffer, sizeof(buffer), "%.1f", d);
        return buffer;
    } else if (strcmp(type, "bool") == 0) {
        return value ? "True" : "False";
    } else if (strcmp(type, "int") == 0) {
        snprintf(buffer, sizeof(buffer), "%lld", (long long)value);
        return buffer;
    } else {
        snprintf(buffer, sizeof(buffer), "%llu", (unsigned long long)value);
        return buffer;
    }
}

uint64_t boubel_string_to_value(const char* str, const char* type) {
    if (!str) return 0;

    if (!type || strcmp(type, "int") == 0) {
        return atoll(str);
    } else if (strcmp(type, "string") == 0) {
        return (uint64_t)(uintptr_t)strdup(str);
    } else if (strcmp(type, "float") == 0) {
        double d = atof(str);
        uint64_t result;
        memcpy(&result, &d, sizeof(double));
        return result;
    } else if (strcmp(type, "bool") == 0) {
        return (strcmp(str, "True") == 0 || strcmp(str, "true") == 0) ? 1 : 0;
    } else {
        return atoll(str);
    }
}

uint64_t boubel_len(void* value, const char* type) {
    if (!value) return 0;

    if (!type || strcmp(type, "string") == 0) {
        return strlen((char*)value);
    } else if (strcmp(type, "array") == 0) {
        uint64_t* array = (uint64_t*)value;
        return array[0];
    }
    return 0;
}

/* ============================================================
 * 5. FICHIERS (FILE I/O)
 * ============================================================ */

int boubel_file_write(const char* filename, const char* content) {
    FILE* f = fopen(filename, "w");
    if (!f) return 0;

    fprintf(f, "%s", content);
    fclose(f);
    return 1;
}

char* boubel_file_read(const char* filename) {
    static char buffer[65536];
    static char empty[] = "";

    FILE* f = fopen(filename, "r");
    if (!f) {
        return empty;
    }

    size_t n = fread(buffer, 1, sizeof(buffer) - 1, f);
    buffer[n] = '\0';
    fclose(f);
    return buffer;
}

void boubel_print_value(uint64_t value, const char* type) {
    char* str = boubel_value_to_string(value, type);
    if (str) {
        printf("%s", str);
    }
}

/* ============================================================
 * 6. FONCTIONS DE TEMPS (pour wa9t.bou)
 * ============================================================ */

#ifdef _WIN32
    #include <windows.h>
    #include <time.h>
#else
    #include <unistd.h>
    #include <sys/time.h>
#endif

uint64_t boubel_time_now(void) {
#ifdef _WIN32
    return (uint64_t)time(NULL);
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec;
#endif
}

void boubel_sleep(uint64_t seconds) {
#ifdef _WIN32
    Sleep((DWORD)(seconds * 1000));
#else
    sleep(seconds);
#endif
}