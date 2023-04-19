/*
 * alias.c -- Functions for alias of string value
 *
 * The alias items can not be deleted from the list to eliminate the possible
 * segmentation fault, because other threads may have and refer the pointers
 * of the deleted items.
 *
 * 2008/11/05 Makoto WATANABE -- Initial version
 */

#include <stdlib.h>				/* for realloc() */
#include <string.h>				/* for strcmp(), strncpy() */
#include <errno.h>				/* for errno */
#include "log.h"				/* for error(), info(), debug() */
#include "alias.h"			 	/* for strjoin() */

/*
 * Initialize alias list
 */
int alias_init(alias_t *alias)
{
	alias->num = 0;
	alias->items = NULL;

	return 0;
}

/*
 * Add item into list of alias
 */
int alias_add(alias_t *alias, const char *key, const char *val)
{
	int n;
	alias_item_t *p;

	/* Expand size of array for pointers of items */
	n = alias->num;
	p = (alias_item_t *)realloc(alias->items, sizeof(alias_item_t) * (n + 1));
	if (p == NULL) {
		error_num(errno, "cannot allocate memory for alias");
		return -1;
	}
	alias->items = p;

	p = alias->items + n;
	p->key = strdup(key);
	p->val = strdup(val);
	if (p->key == NULL || p->val == NULL) {
		error_num(errno, "cannot allocate memory for alias item");
		free(p->key);
		free(p->val);
		return -1;
	}
	alias->num++;

	return 0;
}


/*
 * Get number of items in list of alias
 */
int alias_num(alias_t *alias)
{
	return alias->num;
}

/*
 * Get i-th key string in list of alias
 */
const char *alias_key(alias_t *alias, int i)
{
	if (i >= alias->num) {
		return NULL;
	}
	return (alias->items[i]).key;
}

/*
 * Get i-th value string in list of alias
 */
const char *alias_val(alias_t *alias, int i)
{
	if (i >= alias->num) {
		return NULL;
	}
	return (alias->items[i]).val;
}

/*
 * Lookup value by key (if not found, return NULL)
 */
const char *alias_lookup(alias_t *alias, const char *key)
{
	int i, n;
	alias_item_t *item, *item_found;

	n = alias->num;
	item = alias->items;
	item_found = NULL;
	for (i = 0; i < n; i++) {
		if (strcasecmp(item->key, key) == 0) {
			item_found = item;
		}
		item++;
	}

	if (item_found == NULL) {
		return NULL;
	}

	return item_found->val;
}

/*
 * Free resources of alias list
 */
int alias_free(alias_t *alias)
{
	int i, n;
	alias_item_t *item;

	n = alias->num;
	for (i = 0; i < n; i++) {
		item = alias->items + i;
		free(item->key);
		free(item->val);
	}
	free(alias->items);

	alias->num = 0;
	alias->items = NULL;

	return 0;
}
