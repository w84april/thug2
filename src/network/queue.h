#ifndef THUG_NETWORK_QUEUE_H
#define THUG_NETWORK_QUEUE_H
#include "messages.h"
typedef struct ThugQueueNode ThugQueueNode;
typedef struct { ThugQueueNode *(*dispose)(ThugQueueNode *, uint32_t, const ThugMemory *); } ThugQueueMethods;
struct ThugQueueNode {
    const ThugQueueMethods *methods;
    void *value;
    uint32_t priority;
    ThugQueueNode *previous, *next;
};
typedef struct { ThugQueueNode node; ThugMessage *message; uint32_t time; } ThugPlainMessageNode;
typedef struct {
    ThugQueueNode node;
    uint32_t retries;
    ThugMessage *message;
    uint32_t unknown_1c;
    uint8_t sent, padding[3];
    uint32_t time;
} ThugReliableMessageNode;
typedef struct {
    ThugQueueNode node;
    uint8_t unknown_14, group, flags, padding;
    uint32_t unknown_18, retries, sequence, time;
    ThugSequencedMessage *message;
} ThugSequencedMessageNode;
typedef struct { uint32_t unknown; ThugQueueNode *node; } ThugQueueIterator;
/* Partial layouts; group indices and all links must refer to valid storage. */
typedef struct {
    ThugQueueNode queues[3];
    uint32_t id;
    uint8_t unknown_40[0x20];
    uint32_t flags;
    uint8_t unknown_64[0x14];
    uint32_t sequences[];
} ThugNetworkPeer;
typedef struct {
    uint8_t unknown_0[8];
    uint32_t time;
    uint8_t unknown_c[0x1e80];
    ThugQueueNode peers;
} ThugQueueClient;
extern const ThugQueueMethods thug_plain_queue_methods, thug_reliable_queue_methods, thug_sequenced_queue_methods,
    thug_plain_node_methods, thug_reliable_node_methods, thug_sequenced_node_methods;
ThugPlainMessageNode *thug_plain_node_initialize(ThugPlainMessageNode *, ThugMessage *);
ThugReliableMessageNode *thug_reliable_node_initialize(ThugReliableMessageNode *, ThugMessage *);
ThugSequencedMessageNode *thug_sequenced_node_initialize(ThugSequencedMessageNode *, ThugSequencedMessage *);
void thug_plain_queue_destroy(ThugQueueNode *);
void thug_reliable_queue_destroy(ThugQueueNode *);
void thug_sequenced_queue_destroy(ThugQueueNode *);
ThugQueueNode *thug_plain_queue_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_reliable_queue_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_sequenced_queue_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_plain_node_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_reliable_node_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_sequenced_node_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
void thug_queue_insert(ThugQueueNode *sentinel, ThugQueueNode *node);
void *thug_queue_first(ThugQueueIterator *, ThugQueueNode *sentinel);
ThugNetworkPeer *thug_queue_find_peer(ThugQueueClient *, uint32_t id);
ThugSequencedMessage *thug_queue_create_sequenced(ThugQueueClient *, uint32_t id, uint32_t length,
    const uint8_t *data, uint32_t group, uint32_t compression, const ThugDiagnostics *, const ThugMemory *);
void thug_queue_remove_message(ThugQueueClient *, ThugNetworkPeer *, uint32_t delivery, uint32_t id, const ThugMemory *);
/* Direct recipients must exist. Full 0xff broadcasts; other recipients with
 * low bit 0x80 set exclude (recipient & ~0x80). The queue does not send sockets. */
void thug_queue_enqueue(ThugQueueClient *, uint32_t recipient, const ThugMessageSpec *, const ThugDiagnostics *, const ThugMemory *);
void thug_queue_send_first(ThugQueueClient *, const ThugMessageSpec *, const ThugDiagnostics *, const ThugMemory *);
ThugQueueClient *thug_network_get_client(const void *state, uint32_t index);
#endif
