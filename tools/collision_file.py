"""Analysis-time layout of the PC version-10 collision file (loader 0x0049cbb0).

This preflights the actual data used by the differential test, without relocating
anything. It is not the recovered game loader.
"""
import struct


def layout(data):
    if len(data) < 32:
        raise ValueError("Truncated collision header")
    version, count, vertices, large_faces, small_faces, large_vertices, small_vertices, _ = \
        struct.unpack_from("<8I", data)
    if version != 10 or vertices != large_vertices + small_vertices:
        raise ValueError("Unexpected collision version/counts")
    vertex_start = (32 + count * 64 + 15) & ~15
    aux_start = vertex_start + (small_vertices + large_vertices * 2) * 6
    face_start = (aux_start + vertices + 3) & ~3
    face_bytes = large_faces * 10 + small_faces * 8
    node_size_at = face_start + ((face_bytes + large_faces + 3) & ~3)
    if node_size_at + 4 > len(data):
        raise ValueError("Collision sections exceed file")
    node_start = node_size_at + 4
    node_size = struct.unpack_from("<I", data, node_size_at)[0]
    list_start = node_start + node_size
    if list_start > len(data) or node_size % 8:
        raise ValueError("Invalid BSP size")
    seen = set()
    leaves = references = max_depth = 0

    def visit(offset, face_count, depth=0):
        nonlocal leaves, references, max_depth
        if offset % 8 or offset + 8 > node_size or offset in seen or depth > 128:
            raise ValueError("Invalid, cyclic, shared, or excessively deep BSP node")
        seen.add(offset)
        max_depth = max(max_depth, depth)
        word, link = struct.unpack_from("<II", data, node_start + offset)
        if word & 3 == 3:
            count = word >> 16
            begin, end = list_start + link * 2, list_start + (link + count) * 2
            if end > len(data):
                raise ValueError("Invalid BSP leaf list")
            if any(index >= face_count for (index,) in struct.iter_unpack("<H", data[begin:end])):
                raise ValueError("BSP references a nonexistent face")
            leaves += 1
            references += count
        else:
            visit(link & ~3, face_count, depth + 1)
            visit((link & ~3) + 8, face_count, depth + 1)

    objects = [32 + index * 64 for index in range(count)]
    for offset in objects:
        faces = struct.unpack_from("<H", data, offset + 8)[0]
        tree = struct.unpack_from("<I", data, offset + 0x34)[0]
        visit(tree, faces)
    if len(seen) * 8 != node_size:
        raise ValueError("BSP contains unreachable nodes")
    return {"objects": objects, "vertices": vertex_start, "vertex_aux": aux_start,
            "faces": face_start, "extra": face_start + face_bytes,
            "nodes": node_start, "face_list": list_start,
            "bsp_nodes": len(seen), "leaves": leaves, "references": references,
            "max_depth": max_depth}
