from display import *
from matrix import *
from gmath import *

def add_mesh(polygons, filename):
    f = open(filename, "r")
    lines = f.read().split("\n")

    # faces start at index 1
    vertices = ["nil"]

    for line in lines:
        parse = line.split(" ")

        # list of geometric vertices
        # v x y z [w]
        if parse[0] == "v":
            if len(parse) == 4:
                vertices.append([10 * float(coord) for coord in parse[1:]])
            if len(parse) == 5:
                vertices.append([10 * float(coord) for coord in parse[1:-1]])
        #print(vertices)
        # polygonal face elements
        # f v/vt/vn v/vt/vn v/vt/vn
        # v     = vertice
        # vt    = texture coordinates
        # vn    = vertex normals
        if parse[0] == "f":
            vert_ind = []
            for par in parse[1:]:
                faces = par.split("/")
                vert_ind.append(int(faces[0]))
            #print(vert_ind)
            v0 = vertices[vert_ind[0]]
            v1 = vertices[vert_ind[1]]
            v2 = vertices[vert_ind[2]]
            #print((v0, v1, v2))

            
            if len(vert_ind) == 4:
                v3 = vertices[vert_ind[3]]
                add_polygon(polygons, v0[0], v0[1], v0[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2])
                add_polygon(polygons, v0[0], v0[1], v0[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2])
            if len(vert_ind) == 3:
                add_polygon(polygons, v0[0], v0[1], v0[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2])
            
def gouraud(polygons, screen, zbuffer, view, ambient, light, symbols, reflect):
    if len(polygons) < 2:
        print 'Need at least 3 points to draw'
        return


    BOT = 0
    TOP = 2
    MID = 1

    i = 0
    vert_normals = vertex_normal(polygons)
    while i < len(polygons):
        normal = calculate_normal(polygons, i)[:]

        #print normal
        if normal[2] > 0:
            flip = False

            points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
                   (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
                   (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]


            points.sort(key = lambda x: x[1])

            x0 = points[BOT][0]
            z0 = points[BOT][2]
            x1 = points[BOT][0]
            z1 = points[BOT][2]
            y = int(points[BOT][1])

            distance0 = int(points[TOP][1]) - y * 1.0 + 1
            distance1 = int(points[MID][1]) - y * 1.0 + 1
            distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

            #print(vert_normals)
            normal0 = vert_normals[tuple(points[0])]
            normal1 = vert_normals[tuple(points[1])]
            normal2 = vert_normals[tuple(points[2])]

            rgb0 = get_lighting(normal0, view, ambient, light, symbols, reflect )
            rgb1 = get_lighting(normal1, view, ambient, light, symbols, reflect )
            rgb2 = get_lighting(normal2, view, ambient, light, symbols, reflect )

            color0 = rgb0[:]
            color1 = rgb0[:]

            cdiff0 = [((rgb2[w]-rgb0[w])/ distance0 if distance0 != 0 else 0) for w in range(3)]
            cdiff1 = [((rgb1[w]-rgb0[w])/ distance1 if distance1 != 0 else 0) for w in range(3)]
            cdiff2 = [((rgb2[w]-rgb1[w])/ distance2 if distance2 != 0 else 0) for w in range(3)]
            dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
            dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
            dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
            dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

            while y <= int(points[TOP][1]):

                if ( not flip and y >= int(points[MID][1])):
                    flip = True
                    color1 = rgb1[:]
                    cdiff1 = cdiff2[:]

                    dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
                    dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
                    x1 = points[MID][0]
                    z1 = points[MID][2]

                draw_scanline_new(int(x0), z0, int(x1), z1, y, screen, zbuffer, 0, color0, color1, view, ambient, light, symbols, reflect, 'gouraud')
                color0 = [color0[w] + cdiff0[w] for w in range(3)]
                color1 = [color1[w] + cdiff1[w] for w in range(3)]

                x0+= dx0
                z0+= dz0
                x1+= dx1
                z1+= dz1
                y+= 1

        i += 3

def draw_scanline_new(x0, z0, x1, z1, y, screen, zbuffer, color, n0, n1, view, ambient, light, symbols, reflect, shade_type):
    if x0 > x1: 
        draw_scanline_new(x1, z1, x0, z0, y, screen, zbuffer, color, n1, n0, view, ambient, light, symbols, reflect, shade_type)
        return
    
    x = x0
    z = z0
    delta_z = (z1 - z0) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0
    
    if (shade_type != 'flat'):
        diff = [((n1[w]-n0[w])/ (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0) for w in range(3)]
    
    while x <= x1:
        if (shade_type == 'gouraud'):
            for i in range(3):
                if n0[i]>255:
                    n0[i]=255
                if n0[i]<0:
                    n0[i] = 0
            color =[int(ind) for ind in n0]
            n0 = [n0[w] + diff[w] for w in range(3)]
        if (shade_type == 'phong'):
            color = get_lighting(n0, view, ambient, light, symbols, reflect )
            n0 = [n0[w] + diff[w] for w in range(3)]
        
        plot(screen, zbuffer, color, int(x), int(y), z)
        x+= 1
        z+= delta_z
        z+= delta_z
def phong(polygons, screen, zbuffer, view, ambient, light, symbols, reflect):
    if len(polygons) < 2:
        print 'Need at least 3 points to draw'
        return


    BOT = 0
    TOP = 2
    MID = 1

    i = 0
    vert_normals = vertex_normal(polygons)
    while i < len(polygons):
        normal = calculate_normal(polygons, i)[:]

        #print normal
        if normal[2] > 0:
            flip = False

            points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
                   (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
                   (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]


            points.sort(key = lambda x: (x[1], x[0]))

            x0 = points[BOT][0]
            z0 = points[BOT][2]
            x1 = points[BOT][0]
            z1 = points[BOT][2]
            y = int(points[BOT][1])

            distance0 = int(points[TOP][1]) - y * 1.0 + 1
            distance1 = int(points[MID][1]) - y * 1.0 + 1
            distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

            normal0 = vert_normals[tuple(points[0])]
            normal1 = vert_normals[tuple(points[1])]
            normal2 = vert_normals[tuple(points[2])]

            n0=normal0[:]
            n1=normal0[:]

            vdiff0 = [((normal2[w]-normal0[w])/ distance0 if distance0 != 0 else 0) for w in range(3)]
            vdiff1 = [((normal1[w]-normal0[w])/ distance1 if distance1 != 0 else 0) for w in range(3)]
            vdiff2 = [((normal2[w]-normal1[w])/ distance2 if distance2 != 0 else 0) for w in range(3)]

            dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
            dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
            dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
            dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

            while y <= int(points[TOP][1]):

                if ( not flip and y >= int(points[MID][1])):
                    flip = True
                    n1 = normal1[:]
                    vdiff1 = vdiff2[:]

                    dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
                    dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
                    x1 = points[MID][0]
                    z1 = points[MID][2]

                #draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
                
                #draw_scanline_phong(int(x0), z0, int(x1), z1, y, screen, zbuffer, n0, n1, view, ambient, light, symbols, reflect)
                draw_scanline_new(int(x0), z0, int(x1), z1, y, screen, zbuffer, 0, n0, n1, view, ambient, light, symbols, reflect, 'phong')
                n0 = [n0[w] + vdiff0[w] for w in range(3)]
                n1 = [n1[w] + vdiff1[w] for w in range(3)]

                x0+= dx0
                z0+= dz0
                x1+= dx1
                z1+= dz1
                y+= 1

        i += 3


def scanline_convert(polygons, i, screen, zbuffer, color):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
               (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
               (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]

    points.sort(key = lambda x: x[1])
    x0 = points[BOT][0]
    z0 = points[BOT][2]
    x1 = points[BOT][0]
    z1 = points[BOT][2]
    y = int(points[BOT][1])

    distance0 = int(points[TOP][1]) - y * 1.0 + 1
    distance1 = int(points[MID][1]) - y * 1.0 + 1
    distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

    dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

    while y <= int(points[TOP][1]):
        if ( not flip and y >= int(points[MID][1])):
            flip = True

            dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
            dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
            x1 = points[MID][0]
            z1 = points[MID][2]

        draw_scanline_new(x0, z0, x1, z1, y, screen, zbuffer, color, 0, 0, 0, 0, 0, 0, 0, 'flat')
        x0+= dx0
        z0+= dz0
        x1+= dx1
        z1+= dz1
        y+= 1



def add_polygon( polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2 ):
    add_point(polygons, x0, y0, z0)
    add_point(polygons, x1, y1, z1)
    add_point(polygons, x2, y2, z2)

def draw_polygons( polygons, screen, zbuffer, view, ambient, light, symbols, reflect):
    if len(polygons) < 2:
        print 'Need at least 3 points to draw'
        return

    point = 0
    while point < len(polygons) - 2:

        normal = calculate_normal(polygons, point)[:]

        #print normal
        if normal[2] > 0:

            color = get_lighting(normal, view, ambient, light, symbols, reflect )
            scanline_convert(polygons, point, screen, zbuffer, color)
            
        point+= 3

def foo(polygons, screen, zbuffer, view, ambient, light, symbols, reflect, shade_type):

    if (shade_type == 'flat'):
        draw_polygons( polygons, screen, zbuffer, view, ambient, light, symbols, reflect)
    if (shade_type == 'gouraud'):
        gouraud( polygons, screen, zbuffer, view, ambient, light, symbols, reflect)
    if (shade_type == 'phong'):
        phong( polygons, screen, zbuffer, view, ambient, light, symbols, reflect)
        

def add_box( polygons, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z)
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z)

    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1)
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1)

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1)
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1)
    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z)
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z)

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1)
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z)
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z)
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1)

def add_sphere(polygons, cx, cy, cz, r, step ):
    points = generate_sphere(cx, cy, cz, r, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    step+= 1
    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt
            p1 = p0+1
            p2 = (p1+step) % (step * (step-1))
            p3 = (p0+step) % (step * (step-1))

            if longt != step - 2:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p1][0],
                             points[p1][1],
                             points[p1][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2])
            if longt != 0:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2],
                             points[p3][0],
                             points[p3][1],
                             points[p3][2])


def generate_sphere( cx, cy, cz, r, step ):
    points = []

    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop+1):
            circ = circle/float(step)

            x = r * math.cos(math.pi * circ) + cx
            y = r * math.sin(math.pi * circ) * math.cos(2*math.pi * rot) + cy
            z = r * math.sin(math.pi * circ) * math.sin(2*math.pi * rot) + cz

            points.append([x, y, z])
            #print 'rotation: %d\tcircle%d'%(rotation, circle)
    return points

def add_torus(polygons, cx, cy, cz, r0, r1, step ):
    points = generate_torus(cx, cy, cz, r0, r1, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt;
            if (longt == (step - 1)):
                p1 = p0 - longt;
            else:
                p1 = p0 + 1;
            p2 = (p1 + step) % (step * step);
            p3 = (p0 + step) % (step * step);

            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p3][0],
                        points[p3][1],
                        points[p3][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2] )
            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2],
                        points[p1][0],
                        points[p1][1],
                        points[p1][2] )


def generate_torus( cx, cy, cz, r0, r1, step ):
    points = []
    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop):
            circ = circle/float(step)

            x = math.cos(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cx;
            y = r0 * math.sin(2*math.pi * circ) + cy;
            z = -1*math.sin(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cz;

            points.append([x, y, z])
    return points


def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy
    i = 1

    while i <= step:
        t = float(i)/step
        x1 = r * math.cos(2*math.pi * t) + cx;
        y1 = r * math.sin(2*math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        i+= 1

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):

    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    i = 1
    while i <= step:
        t = float(i)/step
        x = t * (t * (xcoefs[0] * t + xcoefs[1]) + xcoefs[2]) + xcoefs[3]
        y = t * (t * (ycoefs[0] * t + ycoefs[1]) + ycoefs[2]) + ycoefs[3]
        #x = xcoefs[0] * t*t*t + xcoefs[1] * t*t + xcoefs[2] * t + xcoefs[3]
        #y = ycoefs[0] * t*t*t + ycoefs[1] * t*t + ycoefs[2] * t + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        i+= 1


def draw_lines( matrix, screen, zbuffer, color ):
    if len(matrix) < 2:
        print 'Need at least 2 points to draw'
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line( int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )



def draw_line( x0, y0, z0, x1, y1, z1, screen, zbuffer, color ):

    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x + 1
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y) + 1
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0

    while ( loop_start < loop_end ):
        plot( screen, zbuffer, color, x, y, z )
        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):

            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east
        z+= dz
        loop_start+= 1
    plot( screen, zbuffer, color, x, y, z )
