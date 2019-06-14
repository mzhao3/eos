import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1
    shade_type = 'flat'

    vary_here = False
    name_here = False
    frames_here = False
    for command in commands:
        if (command['op'] == 'frames'):
            num_frames = int(command['args'][0])
            frames_here = True
        if (command['op'] == 'basename'):
            name = command['args'][0]
            name_here = True
        if (command['op'] == 'vary'):
            vary_here = True
        if (command['op'] == 'shading'):
            shade_type = command['shade_type']

    if (vary_here and not frames_here):
        print("No frames provided.")
        exit(0)
    if (frames_here and not name_here):
        name = 'default'
        print("No name provided. Using 'default' for base name.")
    return (name, num_frames, shade_type)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    cmds = []
    for command in commands:
        op = command['op']
        args = command['args']
        if (op == 'vary'):
            start_f = int(args[0])
            end_f = int(args[1])
            start_r = args[2]
            end_r = args[3]

            range_f = int(end_f - start_f)
            vary = (end_r - start_r) / (end_f - start_f)

            for i in range(start_f, end_f + 1):
                frames[i][command['knob']] = start_r + ((i - start_f) * vary)

    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'
    shade_type = 'flat'
    #print(commands)
    (name, num_frames, shade_type) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    print(frames)

    for i in range(int(num_frames)):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []


        for command in commands:
            print command
            c = command['op']
            args = command['args']
            knob_value = 1
            if ('knob' in command.keys() and command['knob']!= None):
                knob_value = frames[i][command['knob']]

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                foo(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shade_type)
                #phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)

                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                #phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)

                foo(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shade_type)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                foo(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shade_type)
                #phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)

                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0] , args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'mesh':
                #print(command)
                if command['constants'] and command['constants'] != ":":
                    reflect = command['constants']

                add_mesh(tmp, args[0])
                matrix_mult( stack[-1], tmp )
                foo(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shade_type)
                #phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
#            elif c == 'shading':
#                shade_type = command['shade_type']
            elif c == 'save_coord_system':
                symbols[command['cs']][1] = stack[-1]
                print(symbols['germ'][1])
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
                print(stack)
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

            save_extension(screen, "./anim/" + name + "%03d"%i)
        # end operation loop
