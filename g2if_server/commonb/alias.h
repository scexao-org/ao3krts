/*
 * alias.h -- Definitions for alias of string value
 *
 * 2008/11/15 Makoto WATANABE -- Initial version
 */

#ifndef _ALIAS_H
#define _ALIAS_H

/* Structure to store an alias item */

typedef struct alias_item {
	char *key;					/* key string */
	char *val;					/* value string */
} alias_item_t;

/* Structure for handling alias list */

typedef struct alias {
	int num;					/* number of items */
	alias_item_t *items;		/* pointer of items */
} alias_t;

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int alias_init(alias_t *alias);
int alias_add(alias_t *alias, const char *key, const char *val);
int alias_num(alias_t *alias);
const char *alias_key(alias_t *alias, int i);
const char *alias_val(alias_t *alias, int i);
const char *alias_lookup(alias_t *alias, const char *key);
int alias_free(alias_t *alias);

#ifdef __cplusplus
}
#endif

#endif /* _ALIAS_H */
