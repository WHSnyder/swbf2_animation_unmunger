import io, sys, os
from chunk_reader import *


filename = sys.argv[1]

with open(filename, 'rb') as input_file:
    with Reader(input_file) as smna:
        smna.skip_bytes(12)
        num_anims = smna.read_u16()

        print("\nFile contains {} animations\n".format(num_anims))

        smna.skip_bytes(2)

        anim_crcs = []
        anim_metadata = {}

        with smna.read_child() as mina:
            mina.skip_bytes(8)

            for i in range(num_anims):
                anim_hash = mina.read_u32() 
                anim_crcs += [anim_hash]

                anim_data = {}
                anim_data["num_frames"] = mina.read_u16()
                anim_data["num_bones"]  = mina.read_u16()

                if i != num_anims - 1:
                    mina.skip_bytes(8)

                anim_metadata[anim_hash] = anim_data


        with smna.read_child() as tnja:

            for i,crc in enumerate(anim_crcs):

                bone_params = {}

                for _ in range(anim_metadata[crc]["num_bones"]):

                    bone_hash = tnja.read_u32()

                    rot_offsets = [tnja.read_u32() for _ in range(4)]
                    loc_offsets = [tnja.read_u32() for _ in range(3)]    
                    
                    qparams = [tnja.read_f32() for _ in range(4)]

                    params = {"rot_offsets" : rot_offsets, "loc_offsets" : loc_offsets, "qparams" : qparams}

                    bone_params[bone_hash] = params

                anim_metadata[crc]["bone_params"] = bone_params


        with smna.read_child() as tada:

            for crc in anim_crcs:

                num_frames = anim_metadata[crc]["num_frames"]
                num_bones = anim_metadata[crc]["num_bones"]

                print("\n\tAnim hash: {} Num frames: {} Num joints: {}".format(hex(crc), num_frames, num_bones))

                bone_num = -1
                for bone_hash in anim_metadata[crc]["bone_params"]:
                    bone_num += 1

                    params_bone = anim_metadata[crc]["bone_params"][bone_hash]
                    
                    offsets_list = params_bone["rot_offsets"] + params_bone["loc_offsets"]
                    qparams = params_bone["qparams"]


                    print("\n\t\tBone #{} hash: {}".format(bone_num,hex(bone_hash)))
                    print("\n\t\tQParams: {}, {}, {}, {}".format(*qparams))

                    
                    for o,start_offset in enumerate(offsets_list):
                        #start_offset = offsets_list[i]
                        tada.skip_bytes(start_offset)

                        if o < 4:
                            mult = 1 / 2047
                            offset = 0.0
                        else:
                            mult = qparams[-1]
                            offset = qparams[o - 4]


                        print("\n\t\t\tOffset {}: {} ({}, {} remaining)".format(o,start_offset, tada.get_current_pos(), tada.how_much_left(tada.get_current_pos())))

                        j = 0
                        exit_loop = False
                        while (j < num_frames and not exit_loop):
                            val = offset + mult * tada.read_i16()
                            print("\t\t\t\t{}: {}".format(j, val))
                            j+=1

                            if (j >= num_frames):
                                break

                            while (True):

                                if (j >= num_frames):
                                    exit_loop = True
                                    break

                                control = tada.read_i8()
                                #print("\t\t\t\tControl val: {}".format(hex(control)))

                                if control == 0x00:
                                    print("\t\t\t\tControl: HOLDING FOR A FRAME")
                                    print("\t\t\t\t{}: {}".format(j, val))
                                    j+=1

                                    if (j >= num_frames):
                                        break

                                elif control == -0x7f:
                                    print("\t\t\t\tControl: READING NEXT FRAME")
                                    break #get ready for new frame

                                elif control == -0x80:
                                    num_skips = tada.read_u8()
                                    print("\t\t\t\tControl: HOLDING FOR {} FRAMES".format(num_skips))

                                    for _ in range(num_skips):
                                        #print("\t\t{}: {}".format(j, val * mult))
                                        j+=1

                                    #break

                                else:
                                    val += mult * float(control) 
                                    print("\t\t\t\t{}: {}".format(j, val))
                                    j+=1                           
                                    #while (j < num_frames):
                                    #    val += mult * float(control)
                                        #print("\t\t\tControl: UKNOWN VALUE FOUND: {}, val: {}".format(hex(control), val))#float(control)))
                                        #control = tada.read_i8()
                                    #    j+=1

                                    #exit_loop = True
                                    

                        tada.reset_pos()



# Groups of steadily increasing (by 1 in toy example) values > 32 do not use 81 to denote new keys,
# instead the data seems to be just laid out plainly...


# Must divide angle bytes by 2047, 2048 = 2 ^ 11, from 12 bit compression...













# 13 bit: 10110000 11110100
# 14 bit: 01100000 11101001
# 15 bit: 10111111 11010010
# 16 bit: 01111110 10100101



# 3 11111101 11111111
# 4 11111001 11111111       11111011 11111111
# 5 11110001 11111111       11110101 11111111
# 6 11100001 11111111       11101010 11111111
# 7 11000001 11111111       11010011 11111111
# 8 10000001 11111111        10100110 11111111
# 9 00000001 11111111
#10 00000001 11111110