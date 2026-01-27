# [SNIPPET: HEURISTIC OPTIMIZATION]
# Purpose: Pre-emptive optimization of massive CAD imports.
# Logic: Calculates a 'Density Score' (Vertex Count / Diagonal Size) to identify 
# 'Monolith' objects that will kill viewport performance. Automatically fragments them.

MONOLITH_SIZE_MIN = 10.0  
MONOLITH_DENSITY  = 500   

# Iterate through candidate objects (Mesh/Curve)
for obj in candidates:
    if is_immune(obj): continue
    
    # 1. HEURISTIC CALCULATION
    # Get bounding box diagonal to determine physical scale
    dims = obj.dimensions
    diag = (dims.x**2 + dims.y**2 + dims.z**2)**0.5
    
    if diag < MONOLITH_SIZE_MIN: continue
        
    v_count = 0
    if obj.type == 'MESH': 
        v_count = len(obj.data.vertices)
    elif obj.type == 'CURVE': 
        v_count = len(obj.data.splines) * 10 # Approximation for spline points
    
    if diag == 0: continue
    
    # DENSITY SCORE:
    # A high vertex count distributed over a large area is fine.
    # A high vertex count in a small area (or a single giant object) needs breaking.
    density_score = v_count / diag
    
    # 2. AUTOMATED FRAGMENTATION
    if density_score < MONOLITH_DENSITY:
        # Select and isolate the object
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Convert Curves to Mesh for processing
        if obj.type == 'CURVE':
            try: bpy.ops.object.convert(target='MESH')
            except: pass
        
        # 'Loose' separation breaks the Monolith into logical islands.
        # This drastically improves culling and viewport performance.
        try:
            bpy.ops.mesh.separate(type='LOOSE')
            monoliths_cracked += 1
        except: pass