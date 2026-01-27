# [SNIPPET: SPATIAL ANALYSIS LOGIC]
# Technology: Blender Python API (bpy), BMesh, Mathutils (KDTree)
# Purpose: Identify structural wall segments from raw edge clouds using spatial proximity and vector alignment.

# 1. OPTIMIZATION: Build Spatial Tree (KDTree)
# Instead of checking every edge against every other edge (O(n^2)), 
# we build a KDTree for fast nearest-neighbor lookups.
mw = obj.matrix_world
kd = kdtree.KDTree(edge_count)

for idx, e in enumerate(bm.edges):
    v1 = mw @ e.verts[0].co
    v2 = mw @ e.verts[1].co
    center = (v1 + v2) / 2
    kd.insert(center, idx)

kd.balance()

# 2. SAMPLING & ANALYSIS
# We sample edges to determine if this object aligns with neighbors (Wall) or is isolated (Debris).
SAMPLE_SIZE = 50
edges_to_check = random.sample(bm.edges[:], SAMPLE_SIZE) if edge_count > SAMPLE_SIZE else bm.edges

votes_wall = 0
votes_debris = 0

for e in edges_to_check:
    p1 = mw @ e.verts[0].co
    p2 = mw @ e.verts[1].co
    vec = (p2 - p1).normalized() # Get directional vector of current edge
    center = (p1 + p2) / 2
    
    # Search for neighbors within 5 units radius
    for (co, index, dist) in kd.find_n(center, 5):
        if index == e.index: continue # Skip self
        if dist < 0.001: continue     # Skip super-close duplicates
        
        # Get neighbor vector
        n_e = bm.edges[index]
        n_p1 = mw @ n_e.verts[0].co
        n_p2 = mw @ n_e.verts[1].co
        n_vec = (n_p2 - n_p1).normalized()
        
        # VECTOR MATH: Dot Product
        # If absolute dot product is close to 1, edges are parallel.
        # If distance is within the 'Gap' threshold, it's likely a wall chain.
        if abs(vec.dot(n_vec)) > 0.95: 
            if GAP_MIN < dist < GAP_MAX: 
                votes_wall += 1
            elif dist >= GAP_MAX: 
                votes_debris += 1
            break # Found a match, move to next sample
            
    if votes_wall > 5: break # Optimization: Early exit if confirmed