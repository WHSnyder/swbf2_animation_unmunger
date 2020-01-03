import io, sys, os
from chunk_reader import *
from crc import *





for file in os.listdir("."):
    filename = os.path.basename(file)
    if filename.endswith(".msh") and not filename.startswith("basepose"):

        anim_name = filename[0:-4]

        print("Found MSH file {}, crc: {}\n".format(anim_name, hex(to_crc(anim_name))))




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

            for i in range(num_anims):
                mina.skip_bytes(8)

                anim_hash = mina.read_u32() 
                anim_crcs += [anim_hash]

                anim_data = {}
                anim_data["num_frames"] = mina.read_u16()
                anim_data["num_bones"]  = mina.read_u16()

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

                if crc != to_crc("grab"):
                    continue

                num_frames = anim_metadata[crc]["num_frames"]
                num_bones = anim_metadata[crc]["num_bones"]

                print("\n\tAnim hash: {} Num frames: {} Num joints: {}".format(hex(crc), num_frames, num_bones))

                num_frames = 5

                for bone_num, bone_hash in enumerate(anim_metadata[crc]["bone_params"]):

                    params_bone = anim_metadata[crc]["bone_params"][bone_hash]
                    
                    offsets_list = params_bone["rot_offsets"] + params_bone["loc_offsets"]
                    qparams = params_bone["qparams"]


                    print("\n\t\tBone #{} hash: {}".format(bone_num,hex(bone_hash)))
                    print("\n\t\tQParams: {}, {}, {}, {}".format(*qparams))

                    
                    for o,start_offset in enumerate(offsets_list):
                        tada.skip_bytes(start_offset)


                        if o < 4:
                            mult = 1 / 2047
                            offset = 0.0
                        else:
                            mult = qparams[-1]
                            offset = qparams[o - 4]

                            print("\n\t\t\tBias = {}, multiplier = {}".format(offset, mult))


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
                                        j+=1

                                else:
                                    val += mult * float(control) 
                                    print("\t\t\t\t{}: {}".format(j, val))
                                    j+=1                           


                        tada.reset_pos()