
import sys, os, errno

def main(TRANSFER_LIST_FILE, NEW_DATA_FILE, OUTPUT_IMAGE_FILE):
    __version__ = '1.0'
    if sys.hexversion < 34013184:
        (
         print >> sys.stderr, 'Python 2.7 or newer is required.')
        try:
            input = raw_input
        except NameError:
            pass

        input('Press ENTER to exit...')
        sys.exit(1)
    else:
        print('sdat2img binary - version: %s\n' % __version__)

    def rangeset(src):
        src_set = src.split(',')
        num_set = [int(item) for item in src_set]
        if len(num_set) != num_set[0] + 1:
            print('Error on parsing following data to rangeset:\n%s' % src)
            sys.exit(1)
        return tuple([(num_set[i], num_set[i + 1]) for i in range(1, len(num_set), 2)])

    def parse_transfer_list_file(path):
        trans_list = open(TRANSFER_LIST_FILE, 'r')
        version = int(trans_list.readline())
        new_blocks = int(trans_list.readline())
        if version >= 2:
            trans_list.readline()
            trans_list.readline()
        commands = []
        for line in trans_list:
            line = line.split(' ')
            cmd = line[0]
            if cmd in ('erase', 'new', 'zero'):
                commands.append([cmd, rangeset(line[1])])
            elif not cmd[0].isdigit():
                print('Command "%s" is not valid.' % cmd)
                trans_list.close()
                sys.exit(1)

        trans_list.close()
        return (version, new_blocks, commands)

    BLOCK_SIZE = 4096
    version, new_blocks, commands = parse_transfer_list_file(TRANSFER_LIST_FILE)
    if version == 1:
        print('Android Lollipop 5.0 detected!\n')
    else:
        if version == 2:
            print('Android Lollipop 5.1 detected!\n')
        else:
            if version == 3:
                print('Android Marshmallow 6.x detected!\n')
            else:
                if version == 4:
                    print('Android Nougat 7.x / Oreo 8.x detected!\n')
                else:
                    print('Unknown Android version!\n')
    try:
        output_img = open(OUTPUT_IMAGE_FILE, 'wb')
    except IOError as e:
        if e.errno == errno.EEXIST:
            print('Error: the output file "{}" already exists'.format(e.filename))
            print('Remove it, rename it, or choose a different file name.')
            sys.exit(e.errno)
        else:
            raise

    new_data_file = open(NEW_DATA_FILE, 'rb')
    all_block_sets = [i for command in commands for i in iter((command[1]))]
    max_file_size = max() * BLOCK_SIZE
    for command in commands:
        if command[0] == 'new':
            for block in command[1]:
                begin = block[0]
                end = block[1]
                block_count = end - begin
                print('Copying {} blocks into position {}...'.format(block_count, begin))
                output_img.seek(begin * BLOCK_SIZE)
                while block_count > 0:
                    output_img.write(new_data_file.read(BLOCK_SIZE))
                    block_count -= 1

        else:
            print('Skipping command %s...' % command[0])

    if output_img.tell() < max_file_size:
        output_img.truncate(max_file_size)
    output_img.close()
    new_data_file.close()
    print('Done! Output image: %s' % os.path.realpath(output_img.name))


if __name__ == '__main__':
    try:
        TRANSFER_LIST_FILE = str(sys.argv[1])
        NEW_DATA_FILE = str(sys.argv[2])
    except IndexError:
        print('\nUsage: sdat2img.py <transfer_list> <system_new_file> [system_img]\n')
        print('    <transfer_list>: transfer list file')
        print('    <system_new_file>: system new dat file')
        print('    [system_img]: output system image\n\n')
        print('Visit xda thread for more information.\n')
        try:
            input = raw_input
        except NameError:
            pass

        input('Press ENTER to exit...')
        sys.exit()

    try:
        OUTPUT_IMAGE_FILE = str(sys.argv[3])
    except IndexError:
        OUTPUT_IMAGE_FILE = 'system.img'

    main(TRANSFER_LIST_FILE, NEW_DATA_FILE, OUTPUT_IMAGE_FILE)
