# Shared explicit original global registry identity and initialized CRT locale.
REGISTRY_INDEX=len(globals_)
for i,value in enumerate([0x648a3c,0xffffffff,0,0x6fa7e0,0x6fa7e0]):
 globals_.append(['thug_level_scene_sentinel_draft',0x6fa7e0+i*4,4,i*4]);defaults.append(value)
HEAD_INDEX=len(globals_);globals_.append(['thug_collision_scene_list',0x6fa7ec,4]);defaults.append(0x6fa7e0)
SHARED_INDEX=len(globals_);globals_.append(['thug_level_shared_vertices_draft',0x786ab6,1]);defaults.append(0)
registry_pointer_globals=[REGISTRY_INDEX,REGISTRY_INDEX+3,REGISTRY_INDEX+4,HEAD_INDEX]
exports += [[0x6fa7e0,'thug_level_scene_sentinel_draft'],[0x648a38,'thug_level_scene_node_methods_draft'],[0x648a3c,'thug_level_scene_sentinel_methods_draft']]
# Ordinary narrow-string sprintf executes its original CRT instructions.
# Initialize the default C locale rather than replacing the formatting call.
LOCALE=oracle.stack+0x1000;oracle.cpu.mem_write(LOCALE,bytes(0x1000));oracle.setword(0x68ecfc,LOCALE)
