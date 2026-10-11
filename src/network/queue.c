#include "queue.h"
#include <stddef.h>
_Static_assert(sizeof(ThugQueueNode) == 20, "Original queue header");
_Static_assert(sizeof(ThugPlainMessageNode) == 28, "Original plain node");
_Static_assert(sizeof(ThugReliableMessageNode) == 40, "Original reliable node");
_Static_assert(sizeof(ThugSequencedMessageNode) == 44, "Original sequenced node");
_Static_assert(offsetof(ThugNetworkPeer, sequences) == 0x78, "Original sequence counters");
_Static_assert(offsetof(ThugQueueClient, peers) == 0x1e8c, "Original connection list");
const ThugQueueMethods thug_plain_queue_methods = { thug_plain_queue_delete };
const ThugQueueMethods thug_reliable_queue_methods = { thug_reliable_queue_delete };
const ThugQueueMethods thug_sequenced_queue_methods = { thug_sequenced_queue_delete };
const ThugQueueMethods thug_plain_node_methods = { thug_plain_node_delete };
const ThugQueueMethods thug_reliable_node_methods = { thug_reliable_node_delete };
const ThugQueueMethods thug_sequenced_node_methods = { thug_sequenced_node_delete };
static void initialize_node(ThugQueueNode *node, const ThugQueueMethods *methods) {
    node->value = node; node->priority = 0; node->previous = node; node->next = node; node->methods = methods;
}
/* 0x004555f0 / 0x00455620 / 0x00455650. Unmentioned fields are untouched. */
ThugPlainMessageNode *thug_plain_node_initialize(ThugPlainMessageNode *node, ThugMessage *message) {
    initialize_node(&node->node, &thug_plain_node_methods); node->message = message; node->time = 0; return node;
}
ThugReliableMessageNode *thug_reliable_node_initialize(ThugReliableMessageNode *node, ThugMessage *message) {
    initialize_node(&node->node, &thug_reliable_node_methods); node->message = message; node->time = 0; node->sent = 0; return node;
}
ThugSequencedMessageNode *thug_sequenced_node_initialize(ThugSequencedMessageNode *node, ThugSequencedMessage *message) {
    initialize_node(&node->node, &thug_sequenced_node_methods); node->flags = 0; node->time = 0;
    node->message = message; node->unknown_14 = 0; return node;
}
static void destroy_node(ThugQueueNode *node, const ThugQueueMethods *methods) {
    node->methods = methods;
    node->next->previous = node->previous;
    node->previous->next = node->next;
    node->previous = node; node->next = node;
}
/* Base destructors 0x00455b50 / 0x00455b70 / 0x00455b90. */
void thug_plain_queue_destroy(ThugQueueNode *node) { destroy_node(node, &thug_plain_queue_methods); }
void thug_reliable_queue_destroy(ThugQueueNode *node) { destroy_node(node, &thug_reliable_queue_methods); }
void thug_sequenced_queue_destroy(ThugQueueNode *node) { destroy_node(node, &thug_sequenced_queue_methods); }
/* Base deleting destructors 0x00455170 / 0x004551b0 / 0x004551f0 and derived
 * deleting destructors 0x004557c0 / 0x004557f0 / 0x00455820. Payload ownership
 * is managed by removal, not by these node destructors. */
#define DELETE_NODE(name, destroy) \
ThugQueueNode *name(ThugQueueNode *node, uint32_t flags, const ThugMemory *memory) { \
    destroy(node); if (flags & 1) memory->release(memory->context, node); return node; \
}
DELETE_NODE(thug_plain_queue_delete, thug_plain_queue_destroy)
DELETE_NODE(thug_reliable_queue_delete, thug_reliable_queue_destroy)
DELETE_NODE(thug_sequenced_queue_delete, thug_sequenced_queue_destroy)
DELETE_NODE(thug_plain_node_delete, thug_plain_queue_destroy)
DELETE_NODE(thug_reliable_node_delete, thug_reliable_queue_destroy)
DELETE_NODE(thug_sequenced_node_delete, thug_sequenced_queue_destroy)
#undef DELETE_NODE
/* 0x00457350. Signed ascending priorities; equal priorities insert before
 * earlier nodes. The caller supplies an unlinked node. */
void thug_queue_insert(ThugQueueNode *sentinel, ThugQueueNode *node) {
    ThugQueueNode *next = sentinel->next;
    while ((uintptr_t)next->value != UINT32_MAX) {
        if ((int32_t)node->priority <= (int32_t)next->priority) break;
        next = next->next;
    }
    if ((uintptr_t)next->value == UINT32_MAX) next = sentinel;
    node->next = next; node->previous = next->previous;
    next->previous->next = node; next->previous = node;
}
static ThugQueueNode *previous(ThugQueueNode *node) {
    node = node->previous;
    return (uintptr_t)node->value == UINT32_MAX ? NULL : node;
}
/* 0x0054b6b0. Iteration goes in reverse link order and yields stored values. */
void *thug_queue_first(ThugQueueIterator *iterator, ThugQueueNode *sentinel) {
    iterator->node = sentinel; iterator->node = previous(sentinel);
    return iterator->node ? iterator->node->value : NULL;
}
/* 0x00457910. A null stored peer terminates iteration. */
ThugNetworkPeer *thug_queue_find_peer(ThugQueueClient *client, uint32_t id) {
    ThugQueueNode *node = previous(&client->peers);
    while (node && node->value) {
        ThugNetworkPeer *peer = node->value;
        if (peer->id == id) return peer;
        node = previous(node);
    }
    return NULL;
}
/* 0x00456d90. The client is unused by message allocation. */
ThugSequencedMessage *thug_queue_create_sequenced(ThugQueueClient *client, uint32_t id, uint32_t length,
    const uint8_t *data, uint32_t group, uint32_t compression, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)client;
    ThugSequencedMessage *message = memory->allocate(memory->context, 16, 1);
    return message ? thug_sequenced_message_initialize(message, id, length, data, group, compression, diagnostics, memory) : NULL;
}
/* 0x00457c80. Capture the reverse successor before disposal, and decrement
 * shared ownership before calling the node's concrete virtual destructor. */
void thug_queue_remove_message(ThugQueueClient *client, ThugNetworkPeer *peer, uint32_t delivery, uint32_t id, const ThugMemory *memory) {
    (void)client;
    if (delivery > 2) return;
    ThugQueueNode *link = previous(&peer->queues[delivery]);
    ThugQueueNode *node = link ? link->value : NULL;
    while (node) {
        ThugQueueNode *next = previous(link);
        ThugQueueNode *next_value = next ? next->value : NULL;
        ThugMessageHeader *message;
        uint32_t *references;
        if (delivery == 2) {
            ThugSequencedMessage *m = ((ThugSequencedMessageNode *)node)->message;
            message = &m->header; references = &m->references;
        } else {
            ThugMessage *m = delivery ? ((ThugReliableMessageNode *)node)->message : ((ThugPlainMessageNode *)node)->message;
            message = &m->header; references = &m->references;
        }
        if (message->id == (uint8_t)id) {
            if (!--*references) { thug_message_destroy(message, memory); memory->release(memory->context, message); }
            node->methods->dispose(node, 1, memory);
        }
        link = next; node = next_value;
    }
}
static void enqueue_peer(ThugQueueClient *client, ThugNetworkPeer *peer, const ThugMessageSpec *spec,
    uint32_t delivery, void *message, uint32_t broadcast, const ThugMemory *memory) {
    ThugQueueNode *node;
    if (delivery == 2) {
        ThugSequencedMessage *m = message; ++m->references;
        ThugSequencedMessageNode *q = thug_allocate_zeroed(44, memory);
        thug_sequenced_node_initialize(q, m);
        q->node.priority = broadcast ? spec->delivery : spec->priority;
        q->time = spec->delay + client->time; q->retries = 0; q->group = spec->group;
        if (spec->sequence) q->sequence = spec->sequence;
        else { q->sequence = peer->sequences[spec->group]; ++peer->sequences[spec->group]; }
        q->flags = spec->flags; node = &q->node;
    } else {
        if (spec->replace) thug_queue_remove_message(client, peer, spec->delivery, spec->id, memory);
        ThugMessage *m = message; ++m->references;
        if (delivery) {
            ThugReliableMessageNode *q = thug_allocate_zeroed(40, memory);
            thug_reliable_node_initialize(q, m); q->node.priority = spec->priority;
            q->time = spec->delay + client->time; q->retries = 0; node = &q->node;
        } else {
            ThugPlainMessageNode *q = thug_allocate_zeroed(28, memory);
            thug_plain_node_initialize(q, m); q->node.priority = spec->priority;
            q->time = spec->delay + client->time; node = &q->node;
        }
    }
    thug_queue_insert(&peer->queues[delivery], node);
}
/* 0x00457eb0. One message is shared by all eligible destination nodes. */
void thug_queue_enqueue(ThugQueueClient *client, uint32_t recipient, const ThugMessageSpec *spec,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    memory->temp_scope(memory->context, 4);
    uint32_t delivery = spec->delivery;
    if (delivery <= 2) {
        void *message;
        if (delivery == 2) message = thug_queue_create_sequenced(client, spec->id, spec->length, spec->data, spec->group, spec->compression, diagnostics, memory);
        else {
            ThugMessage *m = memory->allocate(memory->context, 12, 1);
            message = m ? thug_message_initialize(m, spec->id, spec->length, spec->data, spec->compression, diagnostics, memory) : NULL;
        }
        if (recipient == 0xff || (recipient & 0x80)) {
            ThugQueueNode *link = previous(&client->peers);
            while (link && link->value) {
                ThugNetworkPeer *peer = link->value;
                if ((recipient == 0xff || peer->id != (recipient & 0xffffff7f)) &&
                    (delivery ? !(peer->flags & 8) : peer->flags == 1))
                    enqueue_peer(client, peer, spec, delivery, message, recipient == 0xff, memory);
                link = previous(link);
            }
        } else {
            ThugNetworkPeer *peer = thug_queue_find_peer(client, recipient);
            if (delivery ? !(peer->flags & 8) : (peer->flags == 1 || spec->id == 9))
                enqueue_peer(client, peer, spec, delivery, message, 0, memory);
        }
        uint32_t references = delivery == 2 ? ((ThugSequencedMessage *)message)->references : ((ThugMessage *)message)->references;
        if (!references) { thug_message_destroy(message, memory); memory->release(memory->context, message); }
    }
    memory->temp_scope(memory->context, 0);
}
/* 0x00459e50. Send to the first reverse-list peer, if any. */
void thug_queue_send_first(ThugQueueClient *client, const ThugMessageSpec *spec, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugQueueNode *node = previous(&client->peers);
    ThugNetworkPeer *peer = node ? node->value : NULL;
    if (peer) thug_queue_enqueue(client, peer->id, spec, diagnostics, memory);
}
/* 0x00532ea0. The caller supplies an in-range slot. */
ThugQueueClient *thug_network_get_client(const void *state, uint32_t index) {
    return ((ThugQueueClient *const *)state)[index + 2];
}
